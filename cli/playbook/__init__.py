"""ThreatPlaybook Client v 1.0.0

Usage:
    playbook init <projectname>
    playbook set project <project_name>
    playbook login
    playbook create [--file=<tm_file>] [--dir=<tm_dir>]
    playbook get feature [--name=<name>] [--json | --table]
    playbook get-scans
    playbook sync-scan <scan_name>
    playbook configure
    playbook change-password
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
"""

from docopt import docopt
from huepy import *
from os import path, makedirs
import json
import pickledb
import requests
from sys import exit
#import utils
from . import utils
import yaml
import pyjq
from glob import glob
from tabulate import tabulate
from getpass import getpass


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
        token = db.get('token')
        r = requests.post(baseUrl, headers={"Authorization": token}, json={'query': query})
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
        db = pickledb.load('.cred', False)
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
    print("in init method")
    db = pickledb.load('.cred', False)
    if not verify_host_port():
        print(bad("There's no host and port configured. Please run the `playbook configure` option first."))
        exit(1)
    else:
        if verify_project():
            project_input = input(
                "There's already a project here. Are you sure you want to re-initialize? It will overwrite existing project info ")
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
                print(res)
                try:
                    cleaned_response = utils.validate_project_response(res)
                    if cleaned_response:
                        db.set('project', project_name)
                        db.dump()
                        print(good("Project: {} successfully created in API".format(project_name)))
                        # create boilerplate directories
                        list_of_directories = ["cases"]
                        for dir in list_of_directories:
                            if not path.exists(dir):
                                makedirs(dir)
                        print(good("Boilerplate directories `cases` generated"))
                    else:
                        print(bad(res))
                except Exception as e:
                    print(bad(e.message))
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
            print(res)
            try:
                cleaned_response = utils.validate_project_response(res)
                if cleaned_response:
                    db.set('project', project_name)
                    db.dump()
                    print(good("Project: {} successfully created in API".format(project_name)))
                    # create boilerplate directories
                    list_of_directories = ["cases"]
                    for dir in list_of_directories:
                        if not path.exists(dir):
                            makedirs(dir)
                    print(good("Boilerplate directories `cases` generated"))
                else:
                    print(bad(res))
            except Exception as e:
                print(bad(e.message))


def parse_threat_models(content, user_story, abuser_story=None):
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
                            if utils.validate_repo_query(res):
                                cwe = pyjq.first('.data.repoByName.cwe', res) or 0
                                vul_name = pyjq.first('.data.repoByName.name', res) or "Unknown Vulnerability"
                                mitigations = list(pyjq.first('.data.repoByName.mitigations', res))
                                categories = list(pyjq.first('.data.repoByName.categories', res))

                                mutation_vars = {
                                    "name": {"name": name, "type": "string"},
                                    "cwe": {"name": cwe, "type": "integer"},
                                    "description": {"name": description, "type": "string"},
                                    "vulName": {"name": vul_name, "type": "string"},
                                    "severity": {"name": single['reference']['severity'], "type": "integer"}
                                }

                                if mitigations:
                                    mutation_vars["mitigations"] = {"name": mitigations, "type": "list"}

                                if len(categories) > 0:
                                    mutation_vars["categories"] = {"name": categories, "type": "list"}

                                if len(abuser_story) > 0:
                                    mutation_vars['abuserStories'] = {'name': [abuser_story], "type": "list"}

                                if user_story:
                                    mutation_vars['userStory'] = {'name': user_story, "type": "string"}

                                final_query = utils.template_threat_model_mutation().render(mutation_vars=mutation_vars)
                                tm_res = _make_request(final_query)
                                if tm_res:
                                    cleaned_data = utils.validate_threat_model_query(tm_res)
                                    if cleaned_data:
                                        print(good("Created/Updated Threat Scenario:`{}`".format(name)))
                                        if 'tests' in res['data']['repoByName']:
                                            all_tests = res['data']['repoByName']['tests']
                                            if all_tests:
                                                for one_test in all_tests:
                                                    test_name = one_test.get('name', 'Unknown Test Case')
                                                    test_case = one_test.get('testCase',
                                                                             'Unknown Test Case Description')
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

                                                    final_mutation = utils.template_test_case_mutation(). \
                                                        render(mutation_vars=t_mutation_vars)
                                                    test_case_res = _make_request(final_mutation)
                                                    if test_case_res:
                                                        if utils.validate_test_case_query(test_case_res):
                                                            print("\t", good(
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

                    inline_final_query = utils.template_threat_model_mutation().render(mutation_vars=
                                                                                       inline_mutation_vars)

                    inline_res = _make_request(inline_final_query)
                    if inline_res:
                        inline_cleaned_data = utils.validate_threat_model_query(inline_res)
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

                                final_test_mute = utils.template_test_case_mutation().render(
                                    mutation_vars=final_test_mutation)
                                test_case_res = _make_request(final_test_mute)
                                if test_case_res:
                                    if utils.validate_test_case_query(test_case_res):
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
                    print(bold(red(
                        "Your Threat Scenario must either be of type `repo` or `inline`. This doesn't seem to be either.")))
                    pass


def parse_interactions(user_story_short_name, all_interaction, type):
    for single_interaction in all_interaction:
        if isinstance(single_interaction, dict):
            int_mutation_vars = {"userStoryName": user_story_short_name, "nature": type,
                                 "dataFlow": list(single_interaction.values())[0],
                                 "endpoint": list(single_interaction.keys())[0]}
            ii_mutation = utils.template_interaction_mutation().render(
                mutation_vars=int_mutation_vars)
            ii_res = _make_request(ii_mutation)
            if ii_res:
                if 'data' in ii_res:
                    print(good("Added interaction with {}".format(
                        list(single_interaction.keys())[0])))
                else:
                    print(bad(ii_res))


def parse_spec_file(case_content):
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
    # pre-processing ops
    db = pickledb.load('.cred', False)
    if not verify_host_port():
        print(bad("You dont seem to have a project set. Please set/create project first"))
        exit(1)
    else:
        if verify_project():
            project_name = db.get('project')
            if pyjq.first('.objectType', case_content) == 'Feature':
                user_story_fields = pyjq.all('.name, .description', case_content)

                if isinstance(user_story_fields, list) and user_story_fields and len(user_story_fields) == 2:
                    if 'part_of' in case_content:
                        part_of = case_content['part_of']
                        mutation_vars = {"description": user_story_fields[1], "shortName": user_story_fields[0],
                                         "partOf": part_of, "project": project_name}
                    else:
                        mutation_vars = {"description": user_story_fields[1], "shortName": user_story_fields[0],
                                         "project": project_name}

                    user_story_mutation = utils.template_user_story_mutation().render(mutation_vars=mutation_vars)
                    res = _make_request(user_story_mutation)
                    if res:
                        cleaned_response = utils.validate_user_story(res)
                        if cleaned_response:
                            user_story_short_name = cleaned_response
                            print(good("Created/Updated Feature/UserStory: `{}`".format(user_story_short_name)))

                            if 'internal_interactions' in case_content:
                                parse_interactions(user_story_short_name, case_content['internal_interactions'], "I")

                            if 'external_interactions' in case_content:
                                parse_interactions(user_story_short_name, case_content['external_interactions'], "E")

                        else:
                            print(bad(res))
                    else:
                        print(bad("Error in making request to ThreatPlaybook server"))

                    # abuser story section
                    if 'abuse_cases' in case_content:
                        all_abuses = case_content['abuse_cases']
                        for single in all_abuses:
                            if 'name' in single and 'description' in single:
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
                                """ % (single['name'], single['description'], user_story_fields[0], db.get('project'))
                                res = _make_request(abuser_mutation_query)
                                if res:
                                    cleaned_abuser_response = utils.validate_abuser_story(res)
                                    if cleaned_abuser_response:
                                        print(good("Created/Updated Abuser Story: `{}`".format(single['name'])))

                                        if 'threat_scenarios' in single:
                                            parse_threat_models(single['threat_scenarios'], user_story_fields[0],
                                                                abuser_story=single['name'])
                                    else:
                                        print(bad(res))
                    if 'threat_scenarios' in case_content:
                        parse_threat_models(case_content['threat_scenarios'], user_story_short_name)

            else:
                print(bad(
                    "objectType not defined or not a Feature objectType. objectType has to be set to feature, `objectType: Feature`"))
        else:
            print(bad("you dont have a project set. Please set/create project first"))


def get_user_stories(nameval=None, table=False):
    """
    This function queries the single query or the joint query to find the feature/user story(stories).
    * The function queries the GraphQL server for the details
    * The function returns results in JSON or table (asciitable as required)
    :param nameval:
    :param table:
    :return:
    """
    if nameval:
        final_query = utils.template_user_story_query(nameval)
        res = _make_request(final_query)
        if res:
            if utils.validate_user_story_name_select(res):
                if not table:
                    print(json.dumps(res))
                else:
                    return res
            else:
                print(bold(red(res)))
        else:
            print(bold(red("Unable to make request to fetch user stories")))
    else:
        full_query = utils.template_user_story_full()
        full_res = _make_request(full_query)
        if full_res:
            if utils.validate_user_stories(full_res):
                if not table:
                    print(json.dumps(full_res))
                else:
                    return full_res
            else:
                print(bold(red(full_res)))
        else:
            print(bold(red("Unable to make request to fetch user stories")))


def main():
    arguments = docopt(__doc__, version="ThreatPlaybook Client v 1.0.0")
    if arguments.get('configure'):
        configure_server()
    if arguments.get('init'):
        if arguments.get('<projectname>'):
            create_project(arguments.get('<projectname>'))
        else:
            print(bad("There seems to be NO Project Name"))
    if arguments.get('create'):
        if arguments.get('--file'):
            if path.isfile(arguments.get('--file')):
                if path.splitext(arguments.get('--file'))[1] == '.yaml':
                    full_path = arguments.get('--file')
                    print(full_path)
                    case_content = yaml.safe_load(open(full_path, 'r').read())
                    parse_spec_file(case_content)
        elif arguments.get('--dir'):
            if path.isdir(arguments.get('--dir')):
                full_dir_path = arguments.get('--dir')
                file_list = glob(full_dir_path + "*.yaml")
                if file_list:
                    for single in file_list:
                        with open(single, 'r') as yfile:
                            dir_case_content = yaml.safe_load(yfile.read())
                            parse_spec_file(dir_case_content)
                else:
                    print(bold(red("No files found in path")))
        else:
            print(bold(red("Unrecognized Option. Exiting...")))
            exit(1)
    if arguments.get('get'):
        if arguments.get('--json'):
            get_json_var = True
        else:
            get_json_var = False

        name_val = None
        if arguments.get('--name'):
            name_val = arguments.get('--name')

        if arguments.get('--table'):
            table_var = True
        else:
            table_var = False

        if arguments.get('feature'):
            if get_json_var and name_val:
                get_user_stories(nameval=name_val)
            elif get_json_var and not name_val and not table_var:
                get_user_stories()
            elif name_val and table_var:
                table_dict = get_user_stories(nameval=name_val, table=True)
                abuser_story_string = '\n'.join(pyjq.all('.data.userStoryByName.abuses[] | .shortName', table_dict))
                threat_model_strings = '\n'.join(
                    pyjq.all('.data.userStoryByName.abuses[].models[] | .name', table_dict))
                feature_short_name = pyjq.first('.data.userStoryByName.shortName', table_dict)
                print(tabulate([["Feature/User Story", "Abuser Story Names", "Threat Scenarios"], [feature_short_name,
                                                                                                   abuser_story_string,
                                                                                                   threat_model_strings]]
                               , headers="firstrow", tablefmt="fancy_grid"))
            elif table_var and not get_json_var and not name_val:
                all_table_dict = get_user_stories(table=True)
                feature_list = []
                abuser_story_list = []
                threat_model_list = []
                for single_table_item in all_table_dict['data']['userStories']:
                    fshort = single_table_item['shortName']
                    feature_list.append(fshort)
                    abuser_story_string = '\n'.join(pyjq.all('.abuses[] | .shortName', single_table_item))
                    abuser_story_list.append(abuser_story_string)
                    threat_model_strings = '\n'.join(
                        pyjq.all('.abuses[].models[] | .name', single_table_item))
                    threat_model_list.append(threat_model_strings)

                table_dict = {"Feature/User Story": feature_list, "Abuser Stories": abuser_story_list,
                              "Threat Scenarios": threat_model_list}

                print(tabulate(table_dict, headers="keys", tablefmt="fancy_grid"))

        else:
            print(bold(red("Unknown Option")))
            exit(1)

    if arguments.get('login'):
        if verify_host_port():
            email = input("Please enter your email: ")
            password = getpass('Please enter your password: ')
            db = pickledb.load('.cred', False)
            login_url = "{}:{}/login".format(db.get('host'), db.get('port'))
            r = requests.post(
                login_url,
                json={'email': email, 'password': password}
            )
            if r.status_code == 200 and 'token' in r.json():
                print(good("Successfully logged in"))
                db.set('token', r.json()['token'])
                db.dump()
            else:
                print(bold(red("Invalid credentials")))

        else:
            print(bold(red("No host and port configured for API. Please run `configure` first")))

    if arguments.get('set'):
        if arguments.get('project'):
            if arguments.get('<project_name>'):
                project_name = arguments.get('<project_name>')
                query = """
                query {
                  projectByName(name: "%s") {
                    name
                  }
                }
                """ % project_name
                res = _make_request(query)
                if res:
                    if 'data' in res:
                        db = pickledb.load('.cred', False)
                        db.set('project', project_name)
                        db.dump()
                        print(good("Project {} has been set successfully".format(project_name)))
                    else:
                        print(bad(res))

    if arguments.get('change-password'):
        if verify_host_port():
            db = pickledb.load('.cred', False)
            email = input("Email: ")
            old_password = getpass("Enter old/default password: ")
            new_password = getpass("Enter new password: ")
            verify_password = getpass("Verify new password: ")
            baseUrl = "{}:{}/change-password".format(db.get('host'), db.get('port'))
            pass_req = requests.post(baseUrl, json={
                "email": email,
                "old_password": old_password,
                "new_password": new_password,
                "verify_password": verify_password
            })
            if pass_req.status_code == 200:
                if 'success' in pass_req.json():
                    print(good("Password for user changed successfully. Please login"))

    if arguments.get('get-scans'):
        if verify_host_port():
            get_all_scans = """
            query {
              scans {
                name
                synced
              }
            }
            """
            scan_resp = _make_request(get_all_scans)
            if scan_resp:
                if 'data' in scan_resp:
                    print(json.dumps(scan_resp, indent=2, sort_keys=True))
        else:
            print(bad("ERROR: There seems to be no host configured or you you seem to be logged out"))

    #
    # if arguments.get('sync-scan'):
    #     if arguments.get('')

# if __name__ == '__main__':
#     main()