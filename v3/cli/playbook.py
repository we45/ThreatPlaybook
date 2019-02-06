"""ThreatPlaybook Controller

Usage:
    playbook init <project_name>
    playbook set project <project_name>
    playbook login
    playbook create [--file=<tm_file>] [--dir=<tm_dir>]
    playbook get (feature|abuser_story|model|test_case) --fields=<fieldlist> [--json | --table]
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
    --json      Show information in json dump
    --table     Show information in asciitable view
    --fields=<fieldlist>    query specific fields in the CLI with comma separated list value. Only works with JSON
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
                                  testCase
                                  tags
                                }
                              }
                            }
                            """ % single['reference']['name']
                            res = _make_request(repo_gql_query)
                            if validations.validate_repo_query(res):
                                cwe = pyjq.first('.data.repoByName.cwe',res) or 0
                                vul_name = pyjq.first('.data.repoByName.name',res) or "Unknown Vulnerability"
                                mitigations = list(pyjq.first('.data.repoByName.mitigations',res))
                                categories = list(pyjq.first('.data.repoByName.categories',res))

                                mutation_vars = {
                                    "name": {"name": name, "type": "string"},
                                    "cwe": {"name": cwe, "type": "integer"},
                                    "description": {"name": description, "type": "string"},
                                    "vulName": {"name": vul_name, "type": "string"}
                                }

                                if mitigations:
                                    mutation_vars["mitigations"] = {"name": mitigations, "type": "list"}

                                if len(categories) > 0:
                                    mutation_vars["categories"] = {"name": categories, "type": "list"}

                                if len(abuser_story) > 0:
                                    mutation_vars['abuserStories'] = {'name': [abuser_story], "type": "list"}

                                if user_story:
                                    mutation_vars['userStory'] = {'name': user_story, "type": "string"}

                                final_query = validations.template_threat_model_mutation().render(mutation_vars = mutation_vars)
                                tm_res = _make_request(final_query)
                                if tm_res:
                                    cleaned_data = validations.validate_threat_model_query(tm_res)
                                    if cleaned_data:
                                        print(good("Created/Updated Threat Scenario:`{}`".format(name)))
                                        if 'tests' in res['data']['repoByName']:
                                            all_tests = res['data']['repoByName']['tests']
                                            if all_tests:
                                                for one_test in all_tests:
                                                    test_name = one_test.get('name', 'Unknown Test Case')
                                                    test_case = one_test.get('testCase', 'Unknown Test Case Description')
                                                    test_type = one_test.get('type', 'discovery')
                                                    tools = list(one_test.get('tools'))

                                                    t_mutation_vars = {
                                                        "name": {"name": test_name, "type": "string"},
                                                        "testCase": {"name": test_case, "type": "string"},
                                                        "threatModel": {"name": name, "type": "string"},
                                                        "type": {"name": test_type, "type": "string"},
                                                    }

                                                    if len(tools) > 0:
                                                        t_mutation_vars['tools'] = {"name": tools, "type": "list"}

                                                    final_mutation = validations.template_test_case_mutation().\
                                                        render(mutation_vars = t_mutation_vars)
                                                    test_case_res = _make_request(final_mutation)
                                                    if test_case_res:
                                                        if validations.validate_test_case_query(test_case_res):
                                                            print("\t",good(
                                                                "Created/Updated Test Case:`{}`".format(
                                                                    test_name)))
                                                        else:
                                                            print("\t", bad(test_case_res))
                                    else:
                                        print(bad(tm_res))
                                else:
                                    print(bad("Unable to load Threat Model Request"))

                            else:
                                print(bad(res))

                elif type == 'inline':
                    inline_vul_name = single.get('vul_name', 'Unkown Vulnerability Name')
                    inline_description = single.get('description', "Unknown Vulnerability Description")
                    inline_cwe = int(single.get('cwe', 0))
                    inline_severity = int(single.get('severity', 1))
                    inline_test_cases = single.get('test-cases', [])
                    inline_mutation_vars = {
                        "name": {"name": name, "type": "string"},
                        "cwe": {"name": inline_cwe, "type": "integer"},
                        "description": {"name": inline_description, "type": "string"},
                        "vulName": {"name": inline_vul_name, "type": "string"},
                        "severity": {"name": inline_severity, "type": "integer"},

                    }

                    if abuser_story:
                        inline_mutation_vars['abuserStories'] = {'name': [abuser_story], "type": "list"}

                    if user_story:
                        inline_mutation_vars['userStory'] = {'name': user_story, "type": "string"}

                    inline_final_query = validations.template_threat_model_mutation().render(mutation_vars=
                                                                                             inline_mutation_vars)


                    inline_res = _make_request(inline_final_query)
                    if inline_res:
                        inline_cleaned_data = validations.validate_threat_model_query(inline_res)
                        if inline_cleaned_data:
                            print(good("Created/Updated Threat Scenario: `{}`".format(name)))
                            for one_test in inline_test_cases:
                                test_name = one_test.get('name', 'Unknown Test Case')
                                test_case = one_test.get('testCase', 'Unknown Test Case Description')
                                test_type = one_test.get('type', 'discovery')
                                tools = list(one_test.get('tools'))
                                final_test_mutation = {
                                    "name": {"name": test_name, "type": "string"},
                                    "testCase": {"name": test_case, "type": "string"},
                                    "threatModel": {"name": name, "type": "string"},
                                    "type": {"name": test_type, "type": "string"}
                                }
                                if len(tools) > 0:
                                    final_test_mutation['tools'] = {"name": tools, "type": "list"}

                                final_test_mute = validations.template_test_case_mutation().render(
                                    mutation_vars = final_test_mutation)
                                test_case_res = _make_request(final_test_mute)
                                if test_case_res:
                                    if validations.validate_test_case_query(test_case_res):
                                        print("\t", good(
                                            "Created/Updated Security Test Case:`{}`".format(
                                                test_name)))
                                    else:
                                        print("\t", bold(red(test_case_res)))
                                else:
                                    print(bold(red(test_case_res)))
                        else:
                            print(bold(red(inline_res)))
                    else:
                        print(bold(red("Request for Loading Threat Scenario: {} failed".format(name))))

                else:
                    print(bold(red("Your Threat Scenario must either be of type `repo` or `inline`. This doesn't seem to be either.")))
                    pass

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
                            print(good("Created/Updated Feature/UserStory: `{}`".format(user_story_short_name)))
                        else:
                            print(bad(res))
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
                                        print(good("Created/Updated Abuser Story: `{}`".format(single['name'])))

                                        if 'threat_scenarios' in single:
                                            parse_threat_models(single['threat_scenarios'], user_story_short_name,
                                                                abuser_story = single['name'])
                                    else:
                                        print(bad(res))
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




