"""ThreatPlaybook Controller

Usage:
    playbook init <project_name>
    playbook set project <project_name>
    playbook login
    playbook create [--file=<tm_file>] [--dir=<tm_dir>]
    playbook get (feature|abuser_story|model|test_case) --a=<get_kv> --show-children [--tree | --table]
    playbook delete (feature|abuser_story|model|test_case) --attrib=<delete_kv>
    playbook report <project_name>
    playbook configure
    playbook (-h | --help)
    playbook --version

Options:
    -h --help   Show this screen
    --version   Show version
    --file=<tm_file>    YAML File to import information from
    --dir=<tm_dir>      Directory with YAML files to parse from
    --attribute=<get_kv>    attribute Key value pair based search. typically name or short_name
    --show-children     Show all child objects under the parent object based on query scope
    --tree      Show information in asciitree view
    --table     Show information in asciitable view
    --a=<get_kv>    Search by attribute based on key-value pair with field. Typically, name or short_name
    --attrib=<delete_kv>    Delete by attribute based on key-value pair with field. Typically, name or short_name
"""

from docopt import docopt
from huepy import *
from os import path, makedirs
import json
import pickledb
import requests
from sys import exit
from jsonschema import validate, ValidationError
import validations


def configure_server():
    """
    This function configures the ThreatPlaybook. By default the server runs on port 5042.
    :return:
    """
    host = str(input("Enter Host Information. Defaults to http://localhost if nothing is entered. "
                     "eg: http://threat-playbook ") or "http://localhost")
    port = int(input("Enter port information, port defaults to 5042 if nothing is entered ") or 5042)
    base_url = "{}:{}/graph".format(host, port)
    if requests.get(base_url).status_code == 200:
        db = pickledb.load('.cred',False)
        db.set('host', host)
        db.set('port', port)
        db.dump()
        print(good("Successfully set host to: {} and port to: {}".format(host, port)))
    else:
        print(bad("Unable to connect to host and port on given parameters. Please try again"))
        exit(1)

def create_project(project_name):
    """
    This function does the following:
    * Creates the Project in the TP Server and receives success message
    * Creates boilerplate directories in the current directory
    * Initializes the .cred file in the project directory
    * Sets the cred file with project name information
    :param project_name:
    :return:
    """
    db = pickledb.load('.cred', False)
    if not db.get('host') and not db.get('port'):
        print(bad("There's no host and port configured. Please run the `playbook configure` option first."))
        exit(1)
    else:
        if db.get('project'):
            project_input = input("There's already a project here. Are you sure you want to re-initialize? It will overwrite existing project info ")
            if any(project_input == word for word in ['no', 'n', 'N', 'NO']):
                print(info("Project will not be overwritten. Current action ignored"))
        else:
            if ' ' in project_name:
                project_name = project_name.replace(' ', '_').lower()
            else:
                project_name = project_name.lower()

            create_project_query = """
                mutation {
                  createProject(name: "%s") {
                    project {
                      name
                    }
                  }
                }
            """ % project_name

            baseUrl = "{}:{}/graph".format(db.get('host'), db.get('port'))
            r = requests.post(baseUrl, json = {"query": create_project_query})
            try:
                validate(instance = r.json(), schema = validations.project_response_schema)
                db.set('project', project_name)
                db.dump()
                print(good("Project: {} successfully created in API".format(project_name)))
                # create boilerplate directories
                list_of_directories = ["cases", "robot"]
                for dir in list_of_directories:
                    if not path.exists(dir):
                        makedirs(dir)
                print(good("Boilerplate directories `cases` and `robot` generated"))
            except ValidationError as e_val:
                print(bad(e_val.message, r.json()))
            except Exception as e:
                print(bad(e.message))

# def parse_spec_file


if __name__ == '__main__':
    arguments = docopt(__doc__, version = "ThreatPlaybook Controller v 1.0.0")
    if arguments.get('configure'):
        configure_server()
    if arguments.get('init'):
        if arguments.get('<project_name>'):
            create_project(arguments.get('<project_name>'))
        else:
            print(bad("There seems to be NO Project Name"))
    # if arguments.get('create'):
    #     if arguments.get('--file'):



