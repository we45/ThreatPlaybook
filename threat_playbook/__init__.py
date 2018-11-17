'''
ThreatPlaybook v 1.2

Usage:
  threat-playbook new-project <projectname>
  threat-playbook set-project <project_name>
  threat-playbook show-vulns [--filter-severity=<severity>] [--format=<vul_format>]
  threat-playbook show-repo [--repoformat=<repo_format>]
  threat-playbook reload-repo


Options:
  -h --help     Show this screen.
  --version     Show version.
  --session=<session>   Session that has the vulnerabilities. Defaults to latest session
  --filter-severity=<severity>  Filters severity by high,medium,low. Defaults to all.
  --format=<vul_format> response in format of choice between json and yaml or cmdline table. Defaults to table
  --repoformat=<repo_format> specific format for the repo vulnerabilities. Default is "table", but you can get responses in JSON

'''

import os
from sys import exit
from docopt import docopt
from texttable import Texttable
from huepy import *
from models import *
import threat_playbook.ThreatPlaybook
from glob import glob
import json
from pprint import pprint
import yaml
import ntpath
from tinydb import TinyDB, Query


connect('threat_playbook')
module_path = os.path.dirname(threat_playbook.__file__)
rdb = TinyDB(os.path.join(module_path, "repo.json"))
Repo = Query()

def set_project(project_name):
    focus_project = Project.objects.get(name = project_name)
    if focus_project:
        os.environ['TP_PROJECT_NAME'] = focus_project.name
        os.environ['TP_PROJECT_ID'] = str(focus_project.id)
    else:
        print(bad("There's no project by that name. Please try again"))


def create_new_project(proj_name):
    list_of_directories = ['results', 'cases', 'entities']
    file_name = '{0}/SecurityTest.robot'.format(proj_name)
    for directory in list_of_directories:
        directory = '{0}/{1}'.format(proj_name, directory)
        if not os.path.exists(directory):
            os.makedirs(directory)
    if not os.path.isfile(file_name):
        file(file_name, 'w').close()

    entities_dir = os.path.join(os.getcwd(), "{0}/entities".format(proj_name))
    if not os.path.isfile(entities_dir + "/entities_connections.yml"):
        file(entities_dir + "/entities_connections.yml", 'w').close()

    if not os.path.isfile('.env'):
        file('.env', 'w').close()


def get_repo_item(format = 'table'):
    if format == 'table':
        table = Texttable()
        table.set_cols_align(["l", "c", "c"])
        table.set_cols_valign(["m", "m", "m"])
        table.add_row(['Name', 'CWE', 'Mitigations'])
        all_vuls = rdb.all()
        for one in all_vuls:
            table.add_row(one['name'], one['cwe'], len(one['mitigations']))
        print(table.draw())
    elif format == 'json':
        print json.dumps(all_vuls)
    elif format == 'yaml':
        print yaml.dump(all_vuls)
    else:
        print bad('Unrecognized Input. Bye!')



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

def get_vulnerabilities(filter = None, format = 'table'):
    if not os.environ['TP_PROJECT_NAME'] or os.environ['TP_PROJECT_ID']:
        print(bad("You need to set the project first by using `threat-playbook set-project <projectname>"))

    latest_session = Session.objects.order_by("created_on").first() #fetches the latest session

    if filter:
        all_vuls = Vulnerability.objects(session = latest_session, severity = filter).\
            exclude('_id', 'models', 'cases')

    all_vuls = Vulnerability.objects(session = latest_session)

    if format == 'table':
        print_vul_table(all_vuls)
    elif format == 'json':
        pprint(all_vuls.to_json())
    else:
        print("Unable to understand the input. Exiting...")


def load_reload_repo_db():
    repo_path = os.path.join(module_path, "repo/")
    for single in glob(repo_path + "*.yaml"):
        single_name = ntpath.basename(single).split('.')[0]
        with open(single,'r') as rfile:
            rval = rfile.read()

        rcon = yaml.safe_load(rval)
        has_value = rdb.get(Repo.repo_id == single_name)
        if not has_value:
            x = {}
            x['repo_id'] = single_name
            x.update(rcon)
            rdb.insert(x)


def main():
    arguments = docopt(__doc__, version = 'ThreatPlaybook CLI for v 1.2')
    if arguments['new-project']:
        if arguments['<projectname>']:
            if ' ' in arguments['<projectname>']:
                print(bad('There seems to be whitespace in your project name. Only have A-Za-Z0-9_- values'))
                exit(1)
            try:
                create_new_project(arguments['<projectname>'])
                print(good("Project: {} created successfully. You should have generated boilerplate code".format(arguments['<projectname>'])))
            except Exception as e:
                print(bad(e))
                exit(1)
    if arguments['set-project']:
        if arguments['<project_name>']:
            try:
                set_project(arguments['<project_name>'])
                print(good("Successfully set Project to {}".format(arguments['<project_name>'])))
            except Exception as e:
                print(bad(e))
                exit(1)
    if arguments['show-vulns']:
        filter = None
        format = 'table'
        if arguments['--filter']:
            filter = arguments['--filter']
        if arguments['--format']:
            format = arguments['--format']
        try:
            get_vulnerabilities(filter, format)
        except Exception as e:
            print(e)
            exit(1)
    if arguments['show-repo']:
        if arguments['--repoformat']:
            try:
                get_repo_item(arguments['--repoformat'])
            except Exception as e:
                print(bad(e))
                exit(1)
        else:
            try:
                get_repo_item()
            except Exception as e:
                print(bad(e))
                exit(1)

    if arguments['reload-repo']:
        try:
            print(good("Attempting to reload repo DB"))
            load_reload_repo_db()
        except Exception as e:
            print(bad(e))
            exit(1)
