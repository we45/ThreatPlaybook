import os
from robot.api import logger
import yaml
import json
from base64 import b64encode
from models import *
from mongoengine import *
from sys import exit
from glob import glob
from pathlib import Path
from utils import parse_zap_json_file, manage_recon_results
from subprocess import call
import textwrap

class ThreatPlaybook(object):
    ROBOT_LIBRARY_SCOPE = 'GLOBAL'

    def __init__(self, project_name, default_connection = True):
        '''
        Initialize the ThreatPlaybook API

        By default, the param ``default_connection`` is set to true. This means that ThreatPlaybook will attempt to connect to
        the local MongoDB instance on DB ``threat_playbook`` with no authentication or other params

        If you want to connect to a mongoDB instance with authentication and other params, you need to enable Environment Variables:
        ``TP_MONGO_USER`` => Mongo Username
        ``TP_MONGO_PASS`` => Mongo Password
        ``TP_MONGO_HOST`` => Mongo Host IP
        ``TP_MONGO_PORT`` => Mongo Port

        All these params have to be set if the default_connection is initialized with `False`

        | ThreatPlaybook  | project_name | default_connection=True/False |

        '''

        try:
            if not default_connection:
                logger.warn("Running MongoDB without Authentication. Highly recommend running MongoDB with Authentication")
                connect('threat_playbook')
            else:
                mongo_user = os.getenv("TP_MONGO_USER", None)
                mongo_pass = os.getenv("TP_MONGO_PASS", None)
                mongo_host = os.getenv("TP_MONGO_HOST", None)
                mongo_port = os.getenv("TP_MONGO_PORT", None)
                connect(db = 'threat_playbook', username = mongo_user, password = mongo_pass, host=mongo_host, port = mongo_port)
        except:
            logger.error("Unable to connect to DB. Disconnecting")
            exit(1)

        Project.objects(name = project_name).update_one(name = project_name, upsert = True)
        self.project = Project.objects.get(name = project_name)

        new_session = Session(project = self.project)
        new_session.save()
        self.session = new_session


    def load_entity_file(self, filepath = None):
        '''
        Loads Entity File. Looks for by default in entities/entities_connections.yml in the CWD.
        You can specify a custom path by setting the file_path param with an absolute path + filename

        :param filepath: optional

        | load entity file  | filepath (optional) |

        '''
        if not filepath:
            filepath = os.path.join(os.getcwd(), "entities/entities_connections.yml")

        with open(filepath, 'r') as yfile:
            edata = yfile.read()

        self.entity_info = yaml.safe_load(edata)


    def find_or_create_entities(self):
        '''
        Find or Create Entities. Does not duplicate entities, unless they have changed in someway from a previous occasion

        | find or create entities  |
        '''
        if isinstance(self.entity_info, dict):
            for short, deets in self.entity_info['entities'].iteritems():
                new_entity = Entity.objects(short = short).update_one(name = deets['name'], description = deets['description'], short = short, caption=deets['caption'], project = self.project, upsert=True)


    def find_or_connect_entities(self):
        '''
        Finds or Connect Entities. Does not duplicate entities, unless they have changed in someway from a previous occasion
        | find or connect entities |

        '''
        for econn in self.entity_info['connections']:
            st = Entity.objects.get(short = econn[0])
            end = Entity.objects.get(short = econn[1])
            if len(econn) == 3:
                EntityMapping.objects(start = st.id, end = end.id, link_text = econn[2], project = self.project).update_one(start = st, end = end, link_text = econn[2], project = self.project, upsert=True)
            elif len(econn) == 4:
                EntityMapping.objects(start=st.id, end=end.id, link_text=econn[2], subgraph = econn[3], project=self.project).update_one(start=st,end=end,link_text=econn[2],subgraph = econn[3], project=self.project, upsert=True)


    def process_test_cases(self, test_path = None):
        '''
        Processes all test cases in default security_tests directory. If you want to specify a custom location,
        you need to provide a absolute path to yaml files with security_tests

        :param test_path: optional

        | process test cases | test_path (optional |

        '''
        if test_path == None:
            test_path = os.path.join(os.getcwd(), "security_tests/")

        with open(test_path + "security_tests.yml", 'r') as testfile:
                testval = testfile.read()

        content = yaml.load(testval)
        if isinstance(content, dict):
            for case, deets in content.items():
                if deets.has_key('tags'):
                    tags = deets['tags'].split(',')
                else:
                    tags = []

                TestCase.objects(short_name = case).update_one(short_name = case, description = deets['description'], case_type = deets['type'], tags = tags, upsert = True)


    def find_or_load_cases_from_directory(self, link_tests = False, case_path = None, test_path = None):
       '''
       Loads cases from the default cases directory and runs through each file of type yml to load user stories, abuser stories, threat models and linked cases
       :param link_tests: optional params. Set to false. If enabled, all the test cases linked to threat model wiill be associated with said model
       :param case_path: default is current working directory + cases. You can change if you want
       :param test_path: default is current working directory + security_tests. You can change if you want

       | find or load cases from directory  | link_tests (optional)  | case_path (optional)  | test_path (optional)

       '''
       if case_path == None:
           case_path = os.path.join(os.getcwd(), "cases/")

       if test_path == None:
           test_path = os.path.join(os.getcwd(), "security_tests/")

       for single in glob(case_path + "*.yml"):
           with open(single, 'r') as casefile:
               caseval = casefile.read()

           content = yaml.load(caseval)
           use_case = next(iter(content))
           abuse_cases = []
           threat_models = []
           UseCase.objects(short_name = use_case).update_one(short_name = use_case, description = content[use_case]['description'], project = self.project, upsert = True)
           if content[use_case].has_key('abuse_cases'):
               all_abuse_cases = content[use_case]['abuse_cases']
               for ab_case,details in all_abuse_cases.items():
                   AbuseCase.objects(short_name = ab_case).update_one(short_name = ab_case, description = details['description'], project = self.project, upsert = True)
                   abuse_cases.append(AbuseCase.objects.get(short_name = ab_case).id)
                   all_threat_models = details['threat_scenarios']
                   print all_threat_models
                   for model, mdeets in all_threat_models.items():
                       if mdeets.has_key('cwe'):
                           if "," in str(mdeets['cwe']):
                               cwes = list(map(int, mdeets['cwe'].split(',')))
                           else:
                               cwes = [mdeets['cwe']]
                       else:
                           cwes = [0]

                       if mdeets['dread'] == None:
                           ThreatModel.objects(name=model).update_one(name=model, description=mdeets['description'],
                                                                     project=self.project, cwe=cwes,
                                                                     upsert=True)
                       else:
                           dread = list(map(int, mdeets['dread'].split(',')))
                           ThreatModel.objects(name=model).update_one(name=model, description=mdeets['description'],
                                                                     project=self.project, cwe=cwes,dread = dread,
                                                                     upsert=True)
                       mytm = ThreatModel.objects.get(name=model)
                       threat_models.append(mytm.id)

                       if link_tests:
                          if not Path(test_path + "security_tests.yml").exists():
                              raise Exception("There are no security tests. Exiting.")
                          else:
                              with open(test_path+"security_tests.yml", 'r') as test_case_file:
                                  all_tests = test_case_file.read()

                              test_cases = yaml.load(all_tests)
                              for case in mdeets['cases']:
                                  if case in test_cases.keys():
                                      loaded = TestCase.objects.get(short_name = case)
                                      if loaded:
                                        if not ThreatModel.objects(name = model, cases = loaded.id):
                                            mytm.cases.append(loaded.id)
                                            mytm.save()
                                        else:
                                            pass
                                      else:
                                          logger.warn("Test Case: {0} not found in DB. Ignoring...".format(case))
                                          pass
                                  else:
                                      logger.warn("Test Case: {0} not found. Ignoring...".format(case))
                                      pass


                   AbuseCase.objects(short_name=ab_case).update_one(models=threat_models, upsert=True)
               UseCase.objects(short_name=use_case).update_one(models=threat_models, abuses=abuse_cases, upsert=True)
           elif content[use_case].has_key('threat_scenarios'):
               for md, deets in content[use_case]['threat_scenarios'].items():
                   if deets.has_key('cwe'):
                       if "," in str(deets['cwe']):
                           cwes = list(map(int, deets['cwe'].split(',')))
                       else:
                           cwes = [deets['cwe']]
                   else:
                       cwes = [0]

                   if deets['dread'] == None:
                       ThreatModel.objects(name=md).update_one(name=md, description=deets['description'],
                                                                  project=self.project, cwe=cwes,
                                                                  upsert=True)
                   else:
                       dread = list(map(int, deets['dread'].split(',')))
                       ThreatModel.objects(name=md).update_one(name=md, description=deets['description'],
                                                                  project=self.project, cwe=cwes, dread=dread,
                                                                  upsert=True)
                   mytm_2 = ThreatModel.objects.get(name=md)
                   threat_models.append(mytm_2.id)

                   if link_tests:
                       if not Path(test_path + "security_tests.yml").exists():
                           raise Exception("There are no security tests. Exiting.")
                       else:
                           with open(test_path + "security_tests.yml", 'r') as test_case_file:
                               all_tests = test_case_file.read()

                           test_cases = yaml.load(all_tests)
                           for case in deets['cases']:
                               if case in test_cases.keys():
                                   loaded = TestCase.objects.get(short_name=case)
                                   if loaded:
                                       if not ThreatModel.objects(name=md, cases=loaded.id):
                                           mytm_2.cases.append(loaded.id)
                                           mytm_2.save()
                                       else:
                                           pass
                                   else:
                                       logger.warn("Test Case: {0} not found in DB. Ignoring...".format(case))
                                       pass
                               else:
                                   logger.warn("Test Case: {0} not found. Ignoring...".format(case))
                                   pass
               UseCase.objects(short_name=use_case).update_one(models=threat_models, upsert=True)
           else:
               raise Exception("Each Use Case needs to have either an Abuser Story or a Threat Model. yours doesnt seem to have either")



    def find_or_create_target(self, name, uri):
        '''
        Creates a target for security testing
        :param name: this needs to be unique
        :param uri: any URI

        | find or create target  | name  | uri  |

        '''
        Target.objects(name = name).update_one(name = name, url = uri, project = self.project, upsert = True)
        # my_target = Target.objects.get(name = name)


    def create_and_link_recon(self, tool, target_name, file_name = None, tags = None):
        '''
        Links recon with the following params
        :param tool: tool name => zap, burp, nmap, etc
        :param target_name: target name, should be already loaded as a target. Name is unique
        :param file_name: file name of the recon results. This is optional
        :param tags: tags of the tool to link by. This will query the tags with the test cases and link the recon to the specific test case.

        | create and link recon  | tool  | target_name  | file_name (optional)  | tags (optional)  |

        '''
        recon = Recon()
        recon.tool = tool
        if file_name:
            recon.result = file_name
        else:
            logger.warn("there's no file. There will be no results stored from your recon results")

        relevant_tests = []
        if tags:
            tags = tags.split(',')
            for single in tags:
                all_tests_for_single = TestCase.objects(tags = single)
                for one in all_tests_for_single:
                    relevant_tests.append(one)


            test_ids = [test.id for test in relevant_tests]

            recon.cases = test_ids


        get_target = Target.objects.get(name = target_name)
        if get_target:
            recon.target = get_target

        recon.session = self.session
        recon.save()


    def parse_zap_json(self, zap_file, target_name):
        '''
        will parse a ZAP JSON file and load  into the DB as vulnerabilities. The Vulnerabilities link with the Threat Models by CWE
        :param zap_file:
        :param target_name:

        | parse zap json  | zap_file  | target_name  |

        '''
        if not target_name:
            raise Exception("No target name specified. Exiting...")
        target = Target.objects.get(name = target_name)
        print(target)
        parse_zap_json_file(zap_file, target=target, session = self.session)


    def generate_mermaid_diagram(self):
        '''
        Generates the process flow diagram based on entities and connections already loaded
        This is not directly a keyword

        '''
        result_path = os.path.join(os.getcwd(), "results/")
        with open(result_path + "process_diagram.mmd", 'w') as mmd:
            mmd.write("graph LR\n")
            all_mappings = EntityMapping.objects(project = self.project)
            for single in all_mappings:
                mmd.write("\t{0}({1})-->|{2}|{3}({4})\n".format(single.start.short, single.start.caption, single.link_text, single.end.short, single.end.caption))

        diagram_file = result_path + "diagram.svg"

        call("mmdc -i {0} -o {1} -b transparent -w 1024 -H 768".format(result_path + 'process_diagram.mmd', diagram_file), shell=True)
        return diagram_file


    def average_dread(self, dread_list):
        return sum(dread_list) / len(dread_list)

    def generate_threat_maps(self):
        '''
        Generates Threat Maps to the threat maps directory within results. Will create it if not already there

        | generate threat maps |

        '''
        result_path = os.path.join(os.getcwd(), "results/")

        if not os.path.exists(result_path + "threat_maps/"):
            os.makedirs(result_path + "threat_maps")

        map_file_path = os.path.join(result_path, "threat_maps/")

        all_uses = UseCase.objects(project=self.project)
        for use in all_uses:
            user_story_file = "{0}.mmd".format(use.short_name.replace(" ",""))
            with open(map_file_path + user_story_file, "w") as mdfile:
                mdfile.write("graph LR\n")
                use_name = use.short_name.replace(" ", "_")
                break_use_description = textwrap.fill(use.description, 30)
                break_use_description = break_use_description.replace("\n", "<br />")
                if use.abuses:
                    for single_abuse in use.abuses:
                        abuse_desc = textwrap.fill(single_abuse.description, 30)
                        abuse_desc = abuse_desc.replace("\n", "<br />")
                        abuse_name = single_abuse.short_name.replace(" ", "_")
                        mdfile.write("\t{0}[{1}]-->{2}[{3}]\n".format(use_name, break_use_description, abuse_name, abuse_desc))
                        if single_abuse.models:
                            for model in single_abuse.models:
                                model_name = model.name.replace(" ", "_")
                                model_desc = textwrap.fill(model.description, 30)
                                model_desc = model_desc.replace("\n", "<br />")
                                mdfile.write("\t{0}[{1}]-->{2}[{3}]\n".format(abuse_name, abuse_desc,
                                                                              model_name, model_desc))
                                if model.cases:
                                    for test_case in model.cases:
                                        test_name = test_case.short_name.replace(" ", "_")
                                        test_desc = textwrap.fill(test_case.description, 30)
                                        test_desc = test_desc.replace("\n", "<br />")
                                        mdfile.write(
                                            "\t{0}[{1}]-->{2}[{3}]\n".format(model_name, model_desc,
                                                                             test_name, test_desc))



                if not use.abuses and use.models:
                    for use_model in use.models:
                        umodel_name = use_model.name.replace(" ", "_")
                        umodel_desc = textwrap.fill(use_model.description, 30)
                        umodel_desc = umodel_desc.replace("\n", "<br />")
                        mdfile.write("\t{0}[{1}]-->{2}[{3}]\n".format(use_name, break_use_description,
                                                                      umodel_name, umodel_desc))
                        if use_model.cases:
                            for u_test_case in use_model.cases:
                                utest_desc = textwrap.fill(u_test_case.description, 30)
                                u_test_case = utest_desc.replace("\n", "<br />")
                                mdfile.write(
                                    "\t{0}[{1}]-->{2}[{3}]\n".format(use_model.name, umodel_desc,
                                                                     u_test_case.short_name.replace(" ", "_"), u_test_case))

            user_story_diagram = "{0}.png".format(use.short_name.replace(" ", ""))
            diagram_file = map_file_path + user_story_diagram

            call("mmdc -i {0} -o {1} -b transparent -w 1024 -H 768".format(map_file_path + user_story_file,
                                                                           diagram_file), shell=True)



    def write_markdown_report(self):
        '''
        Writes a Markdown Report in the results directory of CWD by default
        :return:
        '''
        filename = os.path.join(os.getcwd(), "results/")
        with open(filename + "Report.md", 'w') as mdfile:
            print("in file write loop")
            mdfile.write("# {0}\n".format(self.project.name))
            mdfile.write('## Threat Model for: {0}\n'.format(self.project.name))
            mdfile.write('### Process Flow Diagram\n')
            diagram_file = self.generate_mermaid_diagram()
            mdfile.write("![Flow Diagram]({0})\n".format(diagram_file))

            # Threat Model to Test Case Mapping
            ## Threat Models
            mdfile.write("## Threat Models\n")
            all_uses = UseCase.objects(project=self.project)
            for use in all_uses:
                mdfile.write("### Functionality: {0}\n".format(use.short_name))
                mdfile.write(use.description + "\n")
                if use.abuses:
                    mdfile.write("#### Abuse Cases\n")
                    mdfile.write("\n")

                    for single_abuse in use.abuses:
                        mdfile.write("##### " + single_abuse.description + "\n")
                        if single_abuse.models:
                            for model in single_abuse.models:
                                if model.dread:
                                    avg_dread = self.average_dread(model.dread) or 0
                                    mdfile.write("**{0}, DREAD: {1}**\n".format(model.description, avg_dread))
                                else:
                                    mdfile.write("**{0}**\n".format(model.description))

                                if model.cases:
                                    mdfile.write("##### Test Cases\n")
                                    mdfile.write("| Description | type | tags |\n")
                                    mdfile.write("|----------|:----------:|:--------:|\n")
                                    for test_case in model.cases:
                                        if test_case.case_type == 'A':
                                            case_type = "Automated Test"
                                        elif test_case.case_type == 'M':
                                            case_type = "Manual Test"
                                        else:
                                            case_type = "Recon"

                                        mdfile.write("| {0} | {1} | {2} |\n".format(test_case.description, case_type,
                                                                                    ','.join(test_case.tags)))

                        mdfile.write("\n")
                        mdfile.write("\n")

                    mdfile.write("\n")
                if not use.abuses and use.models:
                    for use_model in use.models:
                        if use_model.dread:
                            avg_dread = self.average_dread(use_model.dread)
                            mdfile.write("**{0}, DREAD: {1}**\n".format(use_model.description, avg_dread))
                            mdfile.write("\n")
                        else:
                            mdfile.write("**{0}**\n".format(use_model.description))
                            mdfile.write("\n")

                        if use_model.cases:
                            mdfile.write("##### Test Cases\n")
                            mdfile.write("| Description | type | tags |\n")
                            mdfile.write("|----------|:----------:|:--------:|\n")
                            for test_case in use_model.cases:
                                if test_case.case_type == 'A':
                                    case_type = "Automated Test"
                                elif test_case.case_type == 'M':
                                    case_type = "Manual Test"
                                else:
                                    case_type = "Recon"

                                mdfile.write("| {0} | {1} | {2} |\n".format(test_case.description, case_type,
                                                                            ','.join(test_case.tags)))
                        mdfile.write("\n")
                        mdfile.write("\n")

                    mdfile.write("\n")
                    mdfile.write("\n")

            ## Vulnerabilities
            mdfile.write("## Vulnerabilities\n")
            mdfile.write("\n")
            all_vuls = Vulnerability.objects(session = self.session)
            for vul in all_vuls:
                mdfile.write("### {0}\n".format(vul.name))
                if vul.severity == 3:
                    severity = "High"
                elif vul.severity == 2:
                    severity = "Medium"
                elif vul.severity == 1:
                    severity = "Low"
                else:
                    severity = "Info"
                mdfile.write("CWE: {0}, Severity: {1}\n".format(vul.cwe, severity))
                mdfile.write("\n")
                if vul.models:
                    mdfile.write("### Linked Threat Models\n")
                    for single_model in vul.models:
                        mdfile.write("* {0}\n".format(single_model.name))
                    mdfile.write("\n")
                mdfile.write("#### Description\n")
                mdfile.write(vul.description + "\n")
                mdfile.write("#### Remediation\n")
                mdfile.write(vul.remediation + "\n")


                mdfile.write("### Evidences\n")
                if vul.evidences:
                    mdfile.write("| URL | Parameter | other info & attack |\n")
                    mdfile.write("|----------|:----------:|:--------:|\n")
                    for single_evidence in vul.evidences:
                        if single_evidence.other_info:
                            other_info = single_evidence.other_info
                        else:
                            other_info = ""
                        if single_evidence.attack:
                            attack = single_evidence.attack
                        else:
                            attack = ""

                        if single_evidence.param:
                            param = single_evidence.param
                        else:
                            param = ""

                        mdfile.write("| {0} | {1} | {2}, {3} |\n".format(single_evidence.url, param, other_info, attack))

            # Recon
            # if write_recon == True:
            mdfile.write("## Reconnaissance\n")
            mdfile.write("\n")
            all_recons = Recon.objects(session = self.session)
            if all_recons:
                for single_recon in all_recons:
                    mdfile.write("### Reconnaissance Tool: {0}\n".format(single_recon.tool))
                    if single_recon.cases:
                        mdfile.write("#### Linked Test Cases\n")
                        for single_case in single_recon.cases:
                            mdfile.write("* {0} - {1}\n".format(single_case.short_name, single_case.description))
                        mdfile.write("\n")

                    mdfile.write("#### Target: {0}\n".format(single_recon.target.name))
                    mdfile.write("\n")
                    if single_recon.result and single_recon.tool == 'nmap':
                        recon_text_string = manage_recon_results(single_recon.result,single_recon.tool)
                        mdfile.write("```\n")
                        mdfile.write("\n")
                        mdfile.write(recon_text_string)
                        mdfile.write("\n")
                        mdfile.write("```\n")
































