import os
from robot.api import logger
import yaml
import json
from base64 import b64decode
from models import *
from mongoengine import *
from sys import exit
from glob import glob
from pathlib import Path
from utils import parse_zap_json_file, manage_burp_xml_file, manage_recon_results, vul_schema, \
    manage_nodejsscan_results, manage_bandit_results, manage_brakeman_results, manage_npm_audit_file
from subprocess import call
import textwrap
from uuid import uuid4
from tinydb import TinyDB, Query

class ThreatPlaybook(object):
    ROBOT_LIBRARY_SCOPE = 'GLOBAL'
    ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

    def __init__(self, project_name, db_name = 'threat_playbook', default_connection = True):
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
                connect(db_name)
            else:
                mongo_user = os.getenv("TP_MONGO_USER", None)
                mongo_pass = os.getenv("TP_MONGO_PASS", None)
                mongo_host = os.getenv("TP_MONGO_HOST", None)
                mongo_port = os.getenv("TP_MONGO_PORT", None)
                connect(db = db_name, username = mongo_user, password = mongo_pass, host=mongo_host, port = mongo_port)

        except:
            logger.error("Unable to connect to DB. Disconnecting")
            exit(1)

        if ' ' in project_name:
            logger.warn('You have whitespaces in your project name, it will be substituted with '
                        '`_` values and lower cased')
            project_name = project_name.replace(' ', '_').lower()
        else:
            logger.warn(
                'Your project name will be lower cased')
            project_name = project_name.lower()

        Project.objects(name = project_name).update_one(name = project_name, upsert = True)
        self.project = Project.objects.get(name = project_name)
        shelve_path = os.path.join(self.ROOT_DIR, 'repo.json')
        self.rdb = TinyDB(shelve_path)
        self.Repo = Query()
        new_session = Session(project = self.project)
        new_session.name = str(uuid4())
        new_session.save()
        self.session = new_session
        self.entity_info = None


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

        # reserved_special_chars = (')', '(', '-', '>', '[', ']')
        if isinstance(self.entity_info, dict):
            for short, deets in self.entity_info['entities'].iteritems():
                new_entity = Entity.objects(short = short).update_one(description = deets['description'], short = short, caption=deets['caption'], project = self.project, upsert=True)



    def find_or_connect_entities(self):
        '''
        Finds or Connect Entities. Does not duplicate entities, unless they have changed in someway from a previous occasion
        | find or connect entities |

        '''
        for short, deets in self.entity_info['entities'].iteritems():
            if 'connections' in deets:
                for connection in deets['connections']:
                    if isinstance(connection, dict):
                        end_var, transmission = connection.items()[0]
                        st = Entity.objects.get(short = short)
                        end = Entity.objects.get(short = end_var)
                        EntityMapping.objects(start=st.id, end=end.id, link_text=transmission,
                                              project=self.project).update_one(start=st, end=end, link_text=transmission,
                                                                               project=self.project, upsert=True)



    def create_vulnerability(self, vul_obj):
        '''
        | create vulnerability  | vul_obj (dictionary with required & optional fields) |

        required attributes for the vulnerability:
        name (str), tool (str), cwe (int), description (int), target_name (str), severity

        optional attributes
        observation(str), remediation (str), evidence (obj):
                                                    name (str):
                                                    log (str)
                                                    data (str)
                                                    url (str)
                                                    param (str)
                                                    attack (str)
                                                    evidence (str)
                                                    other_info (str)

        '''
        validated = vul_schema.validate(vul_obj)
        target = Target.objects.get(name = validated['target_name'])
        if not target:
            raise Exception("Target not Found. Please provide the name for a valid target")

        validated.pop('target_name')


        vul = Vulnerability(**validated)
        if 'cwe' in validated:
            linked_tms = ThreatModel.objects(cwe = validated['cwe'])
            rel_tms = ThreatModel.objects(cwe = validated['cwe'])
            if len(linked_tms) > 0:
                rel_models = []
                [rel_models.append(one) for one in linked_tms]
                model_ids = [model.id for model in rel_models]
                vul.models.extend(model_ids)
            if len(rel_tms) > 0:
                slink_models = []
                [slink_models.append(one) for one in rel_tms]
                s_model_ids = [model.id for model in slink_models]
                vul.models.extend(s_model_ids)
        vul.session = self.session
        vul.target = target
        vul.save()



    def load_threat_scenarios(self, all_threat_models):
        threat_models = []
        for model, mdeets in all_threat_models.items():
            if 'type' in mdeets:
                if mdeets['type'] == 'repo':
                    if 'reference' in mdeets:
                        vul_name = mdeets['reference']['name']
                        vul_find = self.rdb.get(self.Repo.repo_id == vul_name)
                        if vul_find:
                            risks = []
                            vul_cases = []
                            if 'mitigations' in vul_find:
                                mitigations = vul_find['mitigations']
                            else:
                                mitigations = None
                            if 'related_cwes' in vul_find:
                                related_cwes = vul_find['related_cwes']
                            else:
                                related_cwes = None
                            if 'test-cases' in vul_find:
                                if isinstance(vul_find['test-cases'], list):
                                    for single in vul_find['test-cases']:
                                        case = TestCase()
                                        case.name = single['name']
                                        case.test = single['test']
                                        case.type = single['type']
                                        if 'tools' in single:
                                            if isinstance(single['tools'],list):
                                                case.tools = single['tools']
                                        vul_cases.append(case)
                            else:
                                vul_cases = None

                            if 'categories' in vul_find:
                                if isinstance(vul_find['categories'], list):
                                    categories = vul_find['categories']
                            else:
                                categories = None

                            if 'risks' in vul_find:
                                if isinstance(vul_find['risks'], list):
                                    for single_risk in vul_find['risks']:
                                        risks.append(Risk(consequence = single_risk['consequence'],risk_type = single_risk['type']))

                            if 'severity' in mdeets['reference']:
                                if isinstance(mdeets['reference']['severity'],int):
                                    if int(mdeets['reference']['severity']) < 4:
                                        severity = mdeets['reference']['severity']
                            else:
                                severity = None

                            ThreatModel.objects(name = model).update_one(name = model, vul_name = vul_name,
                                                                         description = vul_find['description'],
                                                                         mitigations = mitigations,
                                                                         cwe = vul_find['cwe'],
                                                                         related_cwes = related_cwes, severity = severity,
                                                                         project = self.project, cases = vul_cases,
                                                                         categories = categories, upsert=True)
                            mytm = ThreatModel.objects.get(name=model)
                            threat_models.append(mytm.id)

                elif mdeets['type'] == 'inline':
                    inline_cases = []
                    if 'vul_name' in mdeets:
                        vul_name = mdeets['vul_name']
                    if 'cwe' in mdeets:
                        cwe = mdeets['cwe']
                    else:
                        cwe = 0
                    if 'severity' in mdeets:
                        if isinstance(mdeets['severity'], int):
                            if int(mdeets['severity']) < 4:
                                severity = mdeets['severity']
                    else:
                        severity = None
                    if 'test-cases' in mdeets:
                        if isinstance(mdeets['test-cases'], list):
                            for single in mdeets['test-cases']:
                                case = TestCase()
                                case.name = single['name']
                                case.test = single['test']
                                case.type = single['type']
                                if 'tools' in single:
                                    if isinstance(single['tools'], list):
                                        case.tools = single['tools']
                                inline_cases.append(case)
                    else:
                        inline_cases = None

                    ThreatModel.objects(name=model).update_one(name = model, vul_name = vul_name, cwe = cwe,
                                                               severity = severity, cases = inline_cases,
                                                               upsert=True)
                    mytm = ThreatModel.objects.get(name=model)
                    threat_models.append(mytm.id)

        return threat_models



    def find_or_load_cases_from_directory(self, case_path = None):
       '''
       Loads cases from the default cases directory and runs through each file of type yml to load user stories, abuser stories, threat models and linked cases
       :param case_path: default is current working directory + cases. You can change if you want

       | find or load cases from directory  | case_path (optional)  |

       '''
       if case_path == None:
           case_path = os.path.join(os.getcwd(), "cases/")

       # if test_path == None:
       #     test_path = os.path.join(os.getcwd(), "security_tests/")

       for single in glob(case_path + "*.yml"):
           with open(single, 'r') as casefile:
               caseval = casefile.read()

           content = yaml.load(caseval)
           use_case = next(iter(content))
           abuse_cases = []
           threat_models = []
           UseCase.objects(short_name = use_case).update_one(short_name = use_case,
                                                             description = content[use_case]['description'],
                                                             project = self.project, upsert = True)
           if 'abuse_cases' in content[use_case]:
               all_abuse_cases = content[use_case]['abuse_cases']
               for ab_case,details in all_abuse_cases.items():
                   AbuseCase.objects(short_name = ab_case).update_one(short_name = ab_case,
                                                                      description = details['description'],
                                                                      project = self.project, upsert = True)
                   abuse_cases.append(AbuseCase.objects.get(short_name = ab_case).id)
                   all_threat_models = details['threat_scenarios']
                   threat_models = self.load_threat_scenarios(all_threat_models)
                   AbuseCase.objects(short_name=ab_case).update_one(models=threat_models, upsert=True)

               UseCase.objects(short_name=use_case).update_one(models=threat_models, abuses=abuse_cases,
                                                                   upsert=True)
           # elif 'threat_scenarios' in content[use_case]:
           #     direct_threat_models = self.load_threat_scenarios(content[use_case]['threat_scenarios'])
           #     UseCase.objects(short_name=use_case).update_one(models=direct_threat_models, upsert=True)
           else:
               raise Exception(
                   "Each Use Case needs to have an Abuser Story")


    def find_or_create_target(self, name, uri):
        '''
        Creates a target for security testing
        :param name: this needs to be unique
        :param uri: any URI

        | find or create target  | name  | uri  |

        '''
        Target.objects(name = name).update_one(name = name, url = uri, project = self.project, upsert = True)
        # my_target = Target.objects.get(name = name)


    def create_and_link_recon(self, tool, target_name, file_name = None):
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

        try:
            all_tests_for_single = ThreatModel.objects(cases__tools = tool)
            for one in all_tests_for_single:
                relevant_tests.append(one.id)
        except Exception as e:
            logger.error(e)

        recon.models = relevant_tests
        get_target = Target.objects.get(name = target_name)
        if get_target:
            recon.target = get_target

        recon.session = self.session
        recon.save()


    def parse_zap_json(self, zap_file, target_name, target_uri):
        '''
        will parse a ZAP JSON file and load  into the DB as vulnerabilities. The Vulnerabilities link with the Threat Models by CWE
        :param zap_file:
        :param target_name:

        | parse zap json  | zap_file  | target_name  |

        '''
        if not target_name:
            raise Exception("No target name specified. Exiting...")
        target = Target.objects.get(name = target_name)
        parse_zap_json_file(zap_file, target=target, session = self.session, uri = target_uri)


    def parse_burp_xml(self, burp_file, target_name, target_uri):
        '''
        will parse a Burp XML file and load  into the DB as vulnerabilities. The Vulnerabilities link with the Threat Models by CWE
        :param burp_file:
        :param target_name:

        | parse burp xml  | burp_file  | target_name  |

        '''
        if not target_name:
            raise Exception("No target name specified. Exiting...")
        target = Target.objects.get(name = target_name)
        manage_burp_xml_file(burp_file, target=target, session = self.session, uri = target_uri)

    def parse_nodejsscan_result(self, json_file, target_name):
        '''
                will parse a NodeJSScan JSON file and load  into the DB as vulnerabilities.
                As NodeJSScan does not provide a CWE, there will be NO link with Threat Models
                :param json_file for NodeJS Scan:
                :param target_name:

                | parse nodejsscan result  | json_file  | target_name  |

        '''

        if not target_name:
            raise Exception("No target name specified. Exiting...")
        target = Target.objects.get(name = target_name)
        manage_nodejsscan_results(json_file, target=target, session = self.session)


    def parse_bandit_scan_result(self, json_file, target_name):
        '''
                will parse a Bandit JSON file and load  into the DB as vulnerabilities.
                As Bandit does not provide a CWE, there will be NO link with Threat Models
                :param json_file for Bandit Scan:
                :param target_name:

                | parse bandit scan result  | json_file  | target_name  |

        '''

        if not target_name:
            raise Exception("No target name specified. Exiting...")
        target = Target.objects.get(name = target_name)
        manage_bandit_results(json_file, target=target, session=self.session)


    def parse_brakeman_scan_result(self, json_file, target_name):
        '''
                will parse a Brakeman JSON file and load  into the DB as vulnerabilities.
                As Brakeman does not provide a CWE, there will be NO link with Threat Models
                :param json_file for Brakeman Scan:
                :param target_name:

                | parse brakeman scan result  | json_file  | target_name  |

        '''

        if not target_name:
            raise Exception("No target name specified. Exiting...")
        target = Target.objects.get(name = target_name)
        manage_brakeman_results(json_file, target=target, session=self.session)

    def parse_npmaudit_scan_result(self, json_file, target_name):
        '''
        will parse a NPM Audit JSON file and load  into the DB as vulnerabilities.
        :param json_file for NPM Audit Scan:
        :param target_name:

        | parse npmaudit scan result  | json_file  | target_name  |
        '''

        if not target_name:
            raise Exception("No target name specified. Exiting...")
        target = Target.objects.get(name=target_name)
        manage_npm_audit_file(json_file, target=target, session=self.session)


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
                mmd.write("\t{0}({1})-->|{2}|{3}({4})\n".format(single.start.short, single.start.short, single.link_text, single.end.short, single.end.short))

        diagram_file = result_path + "diagram.svg"

        call("mmdc -i {0} -o {1} -b transparent -w 1280 -H 780".format(result_path + 'process_diagram.mmd', diagram_file), shell=True)
        return diagram_file


    # def average_dread(self, dread_list):
    #     return sum(dread_list) / len(dread_list)

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
                        if single_abuse.description:
                            abuse_desc = textwrap.fill(single_abuse.description, 30)
                            abuse_desc = abuse_desc.replace("\n", "<br />")
                        else:
                            abuse_desc = "No Abuse Description"
                        abuse_name = single_abuse.short_name.replace(" ", "_")
                        mdfile.write("\t{0}[{1}]-->{2}[{3}]\n".format(use_name, break_use_description, abuse_name, abuse_desc))
                        if single_abuse.models:
                            for model in single_abuse.models:
                                model_name = model.name.replace(" ", "_")
                                if model.description:
                                    model_desc = textwrap.fill(model.description, 30)
                                    model_desc = model_desc.replace("\n", "<br />")
                                    mdfile.write("\t{0}[{1}]-->{2}[{3}]\n".format(abuse_name, abuse_desc,
                                                                              model_name, model_desc))
                                else:
                                    model_desc = "-"
                                    mdfile.write("\t{0}[{1}]-->{2}[{3}]\n".format(abuse_name, abuse_desc,
                                                                                  model_name, model_desc))
                                if model.cases:
                                    for test_case in model.cases:
                                        test_name = test_case.name.replace(" ", "_")
                                        if test_case.test:
                                            test_desc = textwrap.fill(test_case.test, 30)
                                            test_desc = test_desc.replace("\n", "<br />")
                                            mdfile.write(
                                                "\t{0}[{1}]-->{2}[{3}]\n".format(model_name, model_desc,
                                                                             test_name, test_desc))
                                        else:
                                            mdfile.write(
                                                "\t{0}[{1}]-->{2}[{3}]\n".format(model_name, model_desc,
                                                                                 test_name, "-"))

            user_story_diagram = "{0}.png".format(use.short_name.replace(" ", ""))
            diagram_file = map_file_path + user_story_diagram

            call("mmdc -i {0} -o {1} -b transparent -w 1024 -H 768".format(map_file_path + user_story_file,
                                                                           diagram_file), shell=True)


    def write_markdown_report(self, gen_diagram="True", gen_threat_model="True"):
        '''
        Writes a Markdown Report in the results directory of CWD by default
        :return:
        '''

        if(gen_diagram == "True"):
            gen_diagram = True
        else:
            gen_diagram = False
        if(gen_threat_model == "True"):
            gen_threat_model = True
        else:
            gen_threat_model = False

        filename = os.path.join(os.getcwd(), "results/")
        with open(filename + "Report.md", 'w') as mdfile:
            mdfile.write("# {0}\n".format(self.project.name))
            mdfile.write('## Threat Model for: {0}\n'.format(self.project.name))
            if gen_diagram:
                mdfile.write('### Process Flow Diagram\n')
                diagram_file = self.generate_mermaid_diagram()
                mdfile.write("![Flow Diagram]({0})\n".format(diagram_file))

            # Threat Model to Test Case Mapping
            ## Threat Models
            if gen_threat_model:
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
                                    if model.severity:
                                        if model.severity == 3:
                                            str_severity = "High"
                                        elif model.severity == 2:
                                            str_severity = "Medium"
                                        elif model.severity == 1:
                                            str_severity = "Low"
                                        else:
                                            str_severity = "Informational"
                                        mdfile.write("**{0}, Severity: {1}**\n".format(model.description, str_severity))
                                    else:
                                        mdfile.write("**{0}**\n".format(model.description))

                                    if model.cases:
                                        mdfile.write("##### Test Cases\n")
                                        mdfile.write("| Description | type | tags |\n")
                                        mdfile.write("|----------|:----------:|:--------:|\n")
                                        for test_case in model.cases:
                                            mdfile.write("| {0} | {1} | {2} |\n".format(test_case.name, test_case.test,
                                                                                        test_case.type))

                            mdfile.write("\n")
                            mdfile.write("\n")

                        mdfile.write("\n")

            ## Vulnerabilities
            if Vulnerability.objects.first() != None:
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
                    mdfile.write("CWE: {0}, Severity: {1}, Tool: {2}\n".format(vul.cwe, severity, vul.tool))
                    mdfile.write("\n")
                    if gen_threat_model:
                        if vul.models:
                            mdfile.write("### Linked Threat Models\n")
                            for single_model in vul.models:
                                mdfile.write("* {0}\n".format(single_model.description))
                            mdfile.write("\n")
                    if vul.description:
                        mdfile.write("#### Description\n")
                        mdfile.write(vul.description + "\n")
                    if vul.remediation:
                        mdfile.write("#### Remediation\n")
                        mdfile.write(vul.remediation + "\n")


                    mdfile.write("### Evidences\n")
                    mdfile.write('\n')
                    if vul.evidences:
                        for single_evidence in vul.evidences:
                            if single_evidence.url:
                                mdfile.write("#### URL/File/Ref: {}\n".format(single_evidence.url))
                            if single_evidence.param:
                                mdfile.write("#### Param/Path: {}\n".format(single_evidence.param))
                            if single_evidence.other_info:
                                mdfile.write("#### Other Info: {}\n".format(single_evidence.other_info))
                            if single_evidence.attack:
                                mdfile.write("#### Attack: {}\n".format(single_evidence.attack))
                            if single_evidence.log:
                                mdfile.write("#### Raw Input\n".format(single_evidence.attack))
                                mdfile.write("```\n")
                                mdfile.write("\n")
                                mdfile.write(b64decode(single_evidence.log))
                                mdfile.write("\n")
                                mdfile.write("```\n")

            # Recon
            # if write_recon == True:
            if Recon.objects.first() != None:
                mdfile.write("## Reconnaissance\n")
                mdfile.write("\n")
                all_recons = Recon.objects(session = self.session)
                if all_recons:
                    for single_recon in all_recons:
                        mdfile.write("### Reconnaissance Tool: {0}\n".format(single_recon.tool))
                        # if single_recon.models:
                        #     mdfile.write("#### Linked Test Cases\n")
                        #     for single_case in single_recon.cases:
                        #         mdfile.write("* {0} - {1}\n".format(single_case.short_name, single_case.description))
                        #     mdfile.write("\n")

                        mdfile.write("#### Target: {0}\n".format(single_recon.target.name))
                        mdfile.write("\n")
                        if single_recon.result:
                            recon_text_string = manage_recon_results(single_recon.result,single_recon.tool)
                            mdfile.write("```\n")
                            mdfile.write("\n")
                            mdfile.write(recon_text_string)
                            mdfile.write("\n")
                            mdfile.write("```\n")
































