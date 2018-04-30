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
from utils import parse_zap_json_file
from subprocess import call

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
        :return:
        '''
        if not filepath:
            filepath = os.path.join(os.getcwd(), "entities/entities_connections.yml")

        with open(filepath, 'r') as yfile:
            edata = yfile.read()

        self.entity_info = yaml.safe_load(edata)


    def find_or_create_entities(self):
        '''
        Find or Create Entities. Does not duplicate entities, unless they have changed in someway from a previous occasion
        :return:
        '''
        if isinstance(self.entity_info, dict):
            for short, deets in self.entity_info['entities'].iteritems():
                new_entity = Entity.objects(short = short).update_one(name = deets['name'], description = deets['description'], short = short, caption=deets['caption'], project = self.project, upsert=True)


    def find_or_connect_entities(self):
        '''
        Finds or Connect Entities. Does not duplicate entities, unless they have changed in someway from a previous occasion
        :return:
        '''
        for econn in self.entity_info['connections']:
            st = Entity.objects.get(short = econn[0])
            end = Entity.objects.get(short = econn[1])
            if len(econn) == 3:
                EntityMapping.objects(start = st.id, end = end.id, link_text = econn[2], project = self.project).update_one(start = st, end = end, link_text = econn[2], project = self.project, session = self.session, upsert=True)
            elif len(econn) == 4:
                EntityMapping.objects(start=st.id, end=end.id, link_text=econn[2], subgraph = econn[3], project=self.project).update_one(start=st,end=end,link_text=econn[2],subgraph = econn[3], project=self.project, upsert=True)


    def process_test_cases(self, test_path = None):
        '''
        Processes all test cases in default security_tests directory. If you want to specify a custom location,
        you need to provide a absolute path to yaml files with security_tests

        :param test_path:
        :return:
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
       :return:
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
                   all_threat_models = details['threat_models']
                   print all_threat_models
                   for model, mdeets in all_threat_models.items():
                      if mdeets['dread'] == None:
                          ThreatModel.objects(name=model).update_one(name=model, description=mdeets['description'],
                                                                     project=self.project, cwe=mdeets['cwe'],
                                                                     upsert=True)
                      else:
                          dread = list(map(int, mdeets['dread'].split(',')))
                          ThreatModel.objects(name=model).update_one(name=model, description=mdeets['description'],
                                                                     project=self.project, cwe=mdeets['cwe'],dread = dread,
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
           elif content[use_case].has_key('threat_models'):
               for md, deets in content[use_case]['threat_models'].items():
                   if deets['dread'] == None:
                       ThreatModel.objects(name=model).update_one(name=model, description=mdeets['description'],
                                                                  project=self.project, cwe=mdeets['cwe'],
                                                                  upsert=True)
                   else:
                       dread = list(map(int, mdeets['dread'].split(',')))
                       ThreatModel.objects(name=model).update_one(name=model, description=mdeets['description'],
                                                                  project=self.project, cwe=mdeets['cwe'], dread=dread,
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
        :return:
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
        :return:
        '''
        recon = Recon()
        recon.tool = tool
        if file_name:
            logger.warn("In File Loop")
            with open(file_name, 'r') as result_file:
                results = b64encode(result_file.read())

            logger.warn(results)
            recon.result = results
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
        :return:
        '''
        if not target_name:
            raise Exception("No target name specified. Exiting...")
        target = Target.objects.get(name = target_name)
        print(target)
        parse_zap_json_file(zap_file, target=target, session = self.session)


    def generate_mermaid_diagram(self):
        '''
        Generates the process flow diagram based on entities and connections already loaded
        :return:
        '''
        result_path = os.path.join(os.getcwd(), "results/")
        with open(result_path + "process_diagram.mmd", 'w') as mmd:
            mmd.write("graph LR\n")
            all_mappings = EntityMapping.objects(project = self.project)
            for single in all_mappings:
                mmd.write("\t{0}({1})-->|{2}|{3}({4})\n".format(single.start.short, single.start.caption, single.link_text, single.end.short, single.end.caption))

        diagram_file = result_path + "diagram.png"

        call("mmdc -i {0} -o {1} -b transparent".format(result_path + 'process_diagram.mmd', diagram_file), shell=True)
        return diagram_file

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
            ## Threat Models
            mdfile.write("## User Story to Threat Model Mapping\n")
            all_uses = UseCase.objects(project = self.project)
            for use in all_uses:
                mdfile.write("### {0}\n".format(use.short_name))
                mdfile.write(use.description + "\n")
                mdfile.write("#### Abuse Cases\n")
                mdfile.write("\n")

                for single_abuse in use.abuses:
                    mdfile.write("##### " + single_abuse.description + "\n")
                    if single_abuse.models:
                        for model in single_abuse.models:
                            if model.dread:
                                mdfile.write("* {0}, DREAD: {1}\n".format(model.description, ", ".join(str(d) for d in model.dread)))
                            else:
                                mdfile.write("* {0}\n".format(model.description))
                    mdfile.write("\n")

            ## Vulnerabilities
            mdfile.write("## Vulnerability - Information\n")
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
























