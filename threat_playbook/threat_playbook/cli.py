#TODO: Add load() event for loading canned threats
#TODO: add lookup for loading existing threats

'''
ThreatPlaybook v 1.2

Usage:
  threat-playbook new-project <projectname>
  threat-playbook show-vulns [--session=<session>] [--filter-severity=<severity>] [--format=<vul_format>]
  threat-playbook get [--entity=<entity_type> [--format=<get_format>]
  threat-playbook set [--directory=<directory_path>]
  threat-playbook report [--path=<report_path>] [--format=<report_format>]

Options:
  -h --help     Show this screen.
  --version     Show version.
  --session=<session>   Session that has the vulnerabilities. Defaults to latest session
  --filter-severity=<severity>  Filters severity by high,medium,low. Defaults to all.
  --format=<vul_format> response in format of choice between json and yaml or cmdline table. Defaults to table
  --format=<get_format> response in format of choice between json and yaml or cmdline table. Defaults to table
  --entity=<entity_type>    Options for entities are: user stories, abuser stories, (threat) scenarios, security test cases
  --directory=<directory_path>  loads threat models from directory (absolute path), etc without having to be linked to automation. defaults to cwd
  --path=<report_path>  generates reports at a given path (absolute path), else generates markdown/HTML report in the same path
  --format=<report_format>  generates report in given format. Choices are `md` for markdown, or `html` for HTML. MD is default
'''


from models import *
from docopt import docopt
from ThreatPlaybook import ThreatPlaybook
import json
import yaml
from texttable import Texttable
import os
from pprint import pprint
import shelve
from glob import glob
import ntpath

connect('threat_playbook')
rdb = shelve.open('repo')

def create_new_project(proj_name):
    list_of_directories = ['results', 'cases', 'entities', 'security_tests']
    file_name = '{0}/SecurityTest.robot'.format(proj_name)
    for directory in list_of_directories:
        directory = '{0}/{1}'.format(proj_name, directory)
        if not os.path.exists(directory):
            os.makedirs(directory)
    try:
        file = open(file_name, 'r')
    except IOError:
        file = open(file_name, 'w')

    entities_dir = os.path.join(os.getcwd(), "{0}/entities".format(proj_name))
    try:
        entities_file = open(entities_dir + "/entities_connections.yml", 'r')
    except IOError:
        entities_file = open(entities_dir + "/entities_connections.yml", 'w')

    stdir = os.path.join(os.getcwd(), "{0}/security_tests".format(proj_name))
    try:
        entities_file = open(stdir + "/security_tests.yml", 'r')
    except IOError:
        entities_file = open(stdir + "/security_tests.yml", 'w')

def print_vul_table(vuls):
    table = Texttable()
    table.set_cols_align(["l", "c", "c", "c"])
    table.set_cols_valign(["m", "m", "m", "m"])
    table.add_row(['Name', 'Tool', 'Severity', 'CWE'])
    for vul in vuls:
        if vul.severity == 3:
            sev = 'High'
        elif vul.severity == 2:
            sev = 'Medium'
        else:
            sev = 'Low'
        table.add_row([vul.name, vul.tool, sev, vul.cwe])

    print table.draw() + "\n"



def get_vulnerabilities(session = None, filter = None, format = 'table'):
    if session and filter:
        all_vuls = Vulnerability.objects(session = session, severity = filter).exclude('_id', 'models', 'cases')
    elif session and filter == None:
        all_vuls = Vulnerability.objects(session=session).exclude('_id', 'models', 'cases')
    elif filter and session == None:
        all_vuls = Vulnerability.objects(severity=filter).exclude('_id', 'models', 'cases')
    else:
        all_vuls = Vulnerability.objects()

    if format == 'table':
        print_vul_table(all_vuls)
    elif format == 'json':
        pprint(all_vuls.to_json())
    else:
        print("Unable to understand the input. Exiting...")

def get_repo_item(name = 'all', format = 'table'):
    if format == 'table':
        table = Texttable()
        table.set_cols_align(["l", "c", "c"])
        table.set_cols_valign(["m", "m", "m"])
        table.add_row(['Name', 'CWE', 'Mitigations'])
        if name == 'all':
            for one in rdb.iterkeys():
                table.add_row([rdb[one]['name'], rdb[one]['cwe'], len(rdb[one]['mitigations'])])
            print(table.draw())
        else:
            print 'in specific name loop'
            if name in rdb:
                specific = rdb[name]
                table.add_row([specific['name'], specific['cwe'], len(specific['mitigations'])])
    elif format == 'json':
        if name == 'all':
            print json.dumps(dict(rdb))
        else:
            print 'in specific name loop'
            if name in rdb:
                specific2 = rdb[name]
                print json.dumps(specific2)
    else:
        print bad('Unrecognized Input. Bye!')



def load_reload_repo_db():
    repo_path = os.path.join(os.getcwd(), "repo/")
    for single in glob(repo_path + "*.yaml"):
        single_name = ntpath.basename(single).split('.')[0]
        with open(single,'r') as rfile:
            rval = rfile.read()

        rcon = yaml.safe_load(rval)
        if not rdb.has_key(single_name):
            rdb[single_name] = rcon




if __name__ == '__main__':
    load_reload_repo_db()