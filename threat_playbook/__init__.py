import os
import sys


class CreateThreatModelPlaybook:
    def __init__(self, argv):
        self.argv = argv or sys.argv[:]
        self.args = sys.argv[1:]
        if self.args:
            self.proj_name = self.args[0]
        else:
            self.proj_name = self.argv

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

        entities_dir = os.path.join(os.getcwd(), "entities")
        try:
            entities_file = open(entities_dir + "entities_connections.yml", 'r')
        except IOError:
            entities_file = open(entities_dir + "entities_connections.yml", 'w')

        stdir = os.path.join(os.getcwd(), "security_tests")
        try:
            entities_file = open(stdir + "security_tests.yml", 'r')
        except IOError:
            entities_file = open(stdir + "security_tests.yml", 'w')


def execute_from_command_line(argv):
    utility = CreateThreatModelPlaybook(argv)
    utility.execute()

