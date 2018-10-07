'''
ThreatPlaybook v 1.2

Usage:
  threat-playbook new-project <projectname>
  threat-playbook set-project <projectname>
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

import os
import sys
from docopt import docopt


class CreateThreatModelPlaybook:
    def __init__(self, argv):
        self.argv = argv
        self.args = sys.argv[1:]
        if self.args:
            self.proj_name = self.args[0]
        else:
            print('Warning : Please enter project name. Example: "threat-playbook ProjectName"')
            sys.exit(0)

    def execute(self):
        list_of_directories = ['results', 'cases', 'entities', 'security_tests']
        file_name = '{0}/SecurityTest.robot'.format(self.proj_name)
        for directory in list_of_directories:
            directory = '{0}/{1}'.format(self.proj_name, directory)
            if not os.path.exists(directory):
                os.makedirs(directory)
        try:
            file = open(file_name, 'r')
        except IOError:
            file = open(file_name, 'w')

        entities_dir = os.path.join(os.getcwd(), "{0}/entities".format(self.proj_name))
        try:
            entities_file = open(entities_dir + "/entities_connections.yml", 'r')
        except IOError:
            entities_file = open(entities_dir + "/entities_connections.yml", 'w')

        stdir = os.path.join(os.getcwd(), "{0}/security_tests".format(self.proj_name))
        try:
            entities_file = open(stdir + "/security_tests.yml", 'r')
        except IOError:
            entities_file = open(stdir + "/security_tests.yml", 'w')


def execute_from_command_line(argv=None):
    utility = CreateThreatModelPlaybook(argv)
    utility.execute()

