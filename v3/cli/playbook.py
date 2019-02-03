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
import validations
import yaml
import pyjq

def verify_host_port():
    db = pickledb.load('.cred', False)
    if db.get('host') and db.get('port'):
        return True

    return False

def verify_project():
    db = pickledb.load('.cred', False)
    if db.get('project'):
        return True

    return False

def _make_request(query):
    db = pickledb.load('.cred', False)
    if verify_host_port():
        baseUrl = "{}:{}/graph".format(db.get('host'), db.get('port'))
        r = requests.post(baseUrl, json = {'query': query})
        return r.json()

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
    if not verify_host_port():
       print(bad("There's no host and port configured. Please run the `playbook configure` option first."))
       exit(1)
    else:
        if verify_project():
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

                # baseUrl = "{}:{}/graph".format(db.get('host'), db.get('port'))
                # r = requests.post(baseUrl, json = {"query": create_project_query})
                res = _make_request(create_project_query)
                try:
                    cleaned_response = validations.validate_project_response(res)
                    if cleaned_response:
                        db.set('project', project_name)
                        db.dump()
                        print(good("Project: {} successfully created in API".format(project_name)))
                        # create boilerplate directories
                        list_of_directories = ["cases", "robot"]
                        for dir in list_of_directories:
                            if not path.exists(dir):
                                makedirs(dir)
                        print(good("Boilerplate directories `cases` and `robot` generated"))
                    else:
                        print(bad(res))
                except Exception as e:
                    print(bad(e.message))

def parse_threat_models(content, user_story, abuser_story = None):
    if isinstance(content, list):
        for single in content:
            if not 'name' in single and not 'type' in single:
                raise Exception("Mandatory field `name` or `type` not in Threat Model. Exiting...")
                exit(1)
            else:
                name = single['name']
                type = single['type']
                description = single['description']
                if type == 'repo':
                    if 'reference' in single:
                        if not 'name' in single['reference'] and not 'severity' in single['reference']:
                            raise Exception("Mandatory fields `name` and `severity` missing from Threat Model")
                        else:
                            repo_gql_query = """
                            query {
                              repoByName(shortName: "%s") {
                                cwe
                                name
                                description
                                relatedCwes
                                mitigations
                                categories
                                tests {
                                  name
                                  tools
                                  type
                                }
                              }
                            }
                            """ % single['reference']['name']
                            res = _make_request(repo_gql_query)
                            if validations.validate_repo_query(res):
                                cwe = int(pyjq.first('.data.repoByName.cwe',res), 0)
                                vul_name = str(pyjq.first('.data.repoByName.name',res), "Unknown Vulnerability")
                                related_cwes = list(pyjq.first('.data.repoByName.related_cwes',res))
                                mitigations = list(pyjq.first('.data.repoByName.mitigations',res))
                                categories = list(pyjq.first('.data.repoByName.categories',res))
                                mutation_vars = {
                                    "name": {"name": name, "type": "string"},
                                    "cwe": {"name": cwe, "type": "integer"},
                                    "mitigations": {"name": mitigations, "type": "list"},
                                    "categories": {"name": categories, "type": "list"},
                                    "description": {"name": description, "type": "string"},
                                    "vul_name": {"name": vul_name, "type": "string"},
                                    "related_cwes": {"name": related_cwes, "type": "list"}
                                }
                                final_query = validations.template_threat_model_mutation().render(mutation_vars = mutation_vars)
                                res = _make_request(final_query)
                                # if res:









def parse_spec_file(fileval):
    """
    This function loads a case file (Feature file) and performs the following operations:
    * create or update user story/feature information => GraphQL Mutation
    * Query the created user story and maintain id/name for abuser story
    * create or update abuser stories related to user story => graphql mutation
    * Query the created abuser story and maintain id/name for threat model
    * create or update threat models related to abuser stories/user story => graphql mutation
    * Query the created threat model for test case
    * create or update test cases related to threat model => graphql mutation
    * load file information in pickledb just to ensure that the state of the file is maintained in the database
    :param fileval:
    :return:
    """
    #pre-processing ops
    db = pickledb.load('.cred', False)
    if not verify_host_port():
        print(bad("You dont seem to have a project set. Please set/create project first"))
        exit(1)
    else:
        if verify_project():
            project_name = db.get('project')
            if pyjq.first('.objectType',case_content) == 'Feature':
                user_story_fields = pyjq.all('.name, .description',case_content)
                if isinstance(user_story_fields, list) and user_story_fields and len(user_story_fields) == 2:
                    user_story_mutation = """
                    mutation {
                      createOrUpdateUserStory(
                        description: "%s",
                        shortName: "%s",
                        project: "%s"
                      ) {
                        userStory {
                          shortName
                        }
                      }
                    }
                    """ % (user_story_fields[1], user_story_fields[0], project_name)

                    res = _make_request(user_story_mutation)
                    if res:
                        cleaned_response = validations.validate_user_story(res)
                        if cleaned_response:
                            user_story_short_name = cleaned_response
                            print(good("Added Feature: `{}` to ThreatPlaybook".format(user_story_short_name)))
                        else:
                            print(bad(res.json()))
                    else:
                        print(bad("Error in making request to ThreatPlaybook server"))

                    # abuser story section
                    if 'abuse_cases' in case_content:
                        all_abuses = case_content['abuse_cases']
                        for single in all_abuses:
                            if 'name' in single  and 'description' in single:
                                abuser_mutation_query = """
                                mutation {
                                  createOrUpdateAbuserStory(
                                    shortName: "%s",
                                    description: "%s",
                                    userStory: "%s"
                                    project: "%s"
                                  ) {
                                    abuserStory {
                                      shortName
                                    }
                                  }
                                }
                                """ % (single['name'], single['description'], user_story_short_name, db.get('project'))
                                res = _make_request(abuser_mutation_query)
                                if res:
                                    cleaned_abuser_response = validations.validate_abuser_story(res)
                                    if cleaned_abuser_response:
                                        abuser_story_short_name = cleaned_abuser_response
                                        if 'threat_scenarios' in case_content['abuse_cases']:
                                            parse_threat_models(case_content['abuse_cases']['threat_scenarios'], user_story_short_name,
                                                                abuser_story = abuser_story_short_name)
                    if 'threat_scenarios' in case_content:
                        parse_threat_models(case_content['threat_scenarios'], user_story_short_name)










            else:
                print(bad("objectType not defined or not a Feature objectType. objectType has to be set to feature, `objectType: Feature`"))
        else:
            print(bad("you dont have a project set. Please set/create project first"))



if __name__ == '__main__':
    arguments = docopt(__doc__, version = "ThreatPlaybook Controller v 1.0.0")
    if arguments.get('configure'):
        configure_server()
    if arguments.get('init'):
        if arguments.get('<project_name>'):
            create_project(arguments.get('<project_name>'))
        else:
            print(bad("There seems to be NO Project Name"))
    if arguments.get('create'):
        if arguments.get('--file'):
            if path.isfile(arguments.get('--file')):
                if path.splitext(arguments.get('--file'))[1] == '.yaml':
                    full_path = path.abspath(arguments.get('--file'))
                    case_content = yaml.safe_load(open(full_path, 'r').read())
                    parse_spec_file(case_content)



