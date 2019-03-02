import os
from robot.api import logger
import json
from sys import exit
from validations import validate_project_response, validate_target_response, validate_scan_response
from parsers import parse_bandit_file, parse_nodejsscan_file, parse_npmaudit_file, parse_zap_file, \
    parse_brakeman_file
from utils import threatplaybook_con, _post_req, _post_query, config_file, create_scan


class ThreatPlaybook(object):
    ROBOT_LIBRARY_SCOPE = 'GLOBAL'
    ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

    def __init__(self, project, target, threatplaybook='http://127.0.0.1:5042'):
        """
        Initialize Threatplaybook API Connection
        :param project: Project Name
        :param target: Target Name
        :param threatplaybook: URL of ThreatPlaybook API Server. [default: http://127.0.0.1:5042]
        """
        self.threatplaybook = threatplaybook
        if threatplaybook_con(threatplaybook=self.threatplaybook):
            logger.info(msg='Connection Successful!')
        else:
            logger.warn(msg='ThreatPlaybook API connection failed.')
            exit(1)
        if ' ' in project:
            logger.warn(msg='You have whitespaces in your project name, it will be substituted with '
                            '`_` values and lower cased')
            project = project.replace(' ', '_').lower()
        else:
            logger.warn(msg='Your project name will be lower cased')
            project = project.lower()
        self.project = project
        self.target = target
        logger.info(msg=project)

    def create_user(self, email, password):
        url = '{}/create-user'.format(self.threatplaybook)
        response = _post_req(url=url, email=email, password=password)
        if response:
            if response.get('success'):
                logger.info(msg='Successfully created user: {}'.format(response.get('success')))
            elif response.get('error'):
                logger.warn(msg='Error while creating user: {}'.format(response.get('error')))
                exit(1)
            else:
                logger.warn(msg='Error while creating a user')
                exit(1)
        else:
            logger.warn(msg='Error while creating a user')
            exit(1)

    def login(self, email, password):
        try:
            url = '{}/login'.format(self.threatplaybook)
            response = _post_req(url=url, email=email, password=password)
            if response:
                if response.get('success'):
                    self.token = response.get('token')
                    logger.info(msg='Login Success: {}'.format(response.get("token")))
                elif response.get('error'):
                    raise Exception("Invalid response while attempting to login: {}".format(response.get('error')))
                else:
                    raise Exception("Invalid response while attempting to login")
            else:
                logger.warn(msg='Error while logging in')
                raise Exception("Invalid response while attempting to login")
        except BaseException:
            raise Exception("Exception while attempting to login")

    def create_project(self):
        create_project_query = """
                mutation {
                    createProject(name: "%s") {
                        project {
                            name
                                }
                            }
                        }""" % self.project
        response = _post_query(threatplaybook=self.threatplaybook, token=self.token, query=create_project_query)
        if response:
            cleaned_response = validate_project_response(content=response)
            if cleaned_response:
                logger.info(msg='Project created: {}'.format(cleaned_response))
            else:
                logger.warn(msg='Error while creating project: {}'.format(response))
                raise Exception("Invalid response while attempting to create project")
        else:
            logger.warn(msg='Error while creating project')
            raise Exception("Invalid response while attempting to create project")

    def create_target(self, url):
        create_target_query = """
            mutation{
            createTarget(name: "%s",
                        project:"%s", 
                        url: "%s"){ 
            target {
                name
                project
                url
                    }
                }
            }""" % (self.target, self.project, url)
        response = _post_query(threatplaybook=self.threatplaybook, token=self.token, query=create_target_query)
        if response:
            cleaned_response = validate_target_response(content=response)
            logger.info(cleaned_response)
            if cleaned_response:
                logger.info(msg='Target Created: {}'.format(cleaned_response))
            else:
                logger.warn(msg='Error while creating target: {}'.format(response))
                raise Exception("Invalid response while attempting to create target")
        else:
            logger.warn(msg='Error while creating target')
            raise Exception("Invalid response while attempting to create target")

    def manage_bandit_results(self, result_file):
        results = json.load(open(result_file, 'r'))
        if results:
            create_scan_query = create_scan(self.target)
            if create_scan_query:
                create_scan_response = _post_query(threatplaybook=self.threatplaybook, token=self.token,
                                                   query=create_scan_query)
                scan = validate_scan_response(content=create_scan_response)
                if scan:
                    for vul_result in results.get('results', []):
                        bandit_results = parse_bandit_file(threatplaybook=self.threatplaybook, vul_result=vul_result,
                                                           project=self.project, target=self.target, scan=scan,
                                                           token=self.token)
                        if bandit_results:
                            logger.info(msg=bandit_results)
                        else:
                            logger.warn(msg='Error while parsing Bandit results')
                else:
                    logger.warn(msg='Error while creating Scan')
            else:
                logger.warn(msg='Error while creating Scan Query')
        else:
            logger.warn(msg="Could not fetch results from file")
            exit(1)

    def manage_nodejsscan_results(self, result_file):
        results = json.load(open(result_file, 'r'))
        if results:
            create_scan_query = create_scan(self.target)
            if create_scan_query:
                create_scan_response = _post_query(threatplaybook=self.threatplaybook, token=self.token,
                                                   query=create_scan_query)
                scan = validate_scan_response(content=create_scan_response)
                if scan:
                    for vul_type, vul_list in results.get('sec_issues').items():
                        for individual_vul_details in vul_list:
                            nodejsscan_results = parse_nodejsscan_file(threatplaybook=self.threatplaybook,
                                                                       vul_result=individual_vul_details,
                                                                       project=self.project, target=self.target,
                                                                       scan=scan, token=self.token)
                            if nodejsscan_results:
                                logger.info(msg=nodejsscan_results)
                            else:
                                logger.warn(msg='Error while parsing NodeJsScan results')
                else:
                    logger.warn(msg='Error while creating Scan')
            else:
                logger.warn(msg='Error while creating Scan Query')
        else:
            logger.warn(msg="Could not fetch results from file")
            exit(1)

    def manage_npmaudit_results(self, result_file):
        results = json.load(open(result_file, 'r'))
        if results:
            create_scan_query = create_scan(self.target)
            if create_scan_query:
                create_scan_response = _post_query(threatplaybook=self.threatplaybook, token=self.token,
                                                   query=create_scan_query)
                scan = validate_scan_response(content=create_scan_response)
                if scan:
                    all_advisories = results.get('advisories')
                    for key, advisory in all_advisories.items():
                        npmaudit_results = parse_npmaudit_file(threatplaybook=self.threatplaybook, vul_result=advisory,
                                                               project=self.project, target=self.target, scan=scan,
                                                               token=self.token)
                        if npmaudit_results:
                            logger.info(msg=npmaudit_results)
                        else:
                            logger.warn(msg='Error while parsing NpmAudit results')
                else:
                    logger.warn(msg='Error while creating Scan')
            else:
                logger.warn(msg='Error while creating Scan Query')
        else:
            logger.warn(msg='Could not fetch results from file')
            exit(1)

    def manage_zap_results(self, result_file, target_url):
        results = json.load(open(result_file, 'r'))
        if results:
            create_scan_query = create_scan(self.target)
            if create_scan_query:
                create_scan_response = _post_query(threatplaybook=self.threatplaybook, token=self.token,
                                                   query=create_scan_query)
                scan = validate_scan_response(content=create_scan_response)
                if scan:
                    alerts = None
                    pre_alerts = results['Report']['Sites']
                    if isinstance(pre_alerts, list):
                        for pre in pre_alerts:
                            if target_url in pre['Host']:
                                alerts = pre
                    if isinstance(pre_alerts, dict):
                        alerts = pre_alerts
                    alerts = alerts['Alerts']['AlertItem']
                    if alerts:
                        if isinstance(alerts, dict):
                            alerts = [alerts]
                        if isinstance(alerts, list):
                            for alert in alerts:
                                zap_results = parse_zap_file(threatplaybook=self.threatplaybook, vul_result=alert,
                                                             project=self.project, target=self.target, scan=scan,
                                                             token=self.token)
                                if zap_results:
                                    logger.info(msg=zap_results)
                                else:
                                    logger.warn(msg='Error while parsing ZAP results')
                    else:
                        logger.warn(msg='No Vulnerability data in file')
                else:
                    logger.warn(msg='Error while creating Scan')
            else:
                logger.warn(msg='Error while creating Scan Query')
        else:
            logger.warn(msg='Could not fetch results from file')
            exit(1)

    def manage_brakeman_results(self, result_file):
        results = json.load(open(result_file, 'r'))
        if results:
            create_scan_query = create_scan(self.target)
            if create_scan_query:
                create_scan_response = _post_query(threatplaybook=self.threatplaybook, token=self.token,
                                                   query=create_scan_query)
                scan = validate_scan_response(content=create_scan_response)
                if scan:
                    vuls = results.get('warnings', [])
                    for vul in vuls:
                        brakeman_results = parse_brakeman_file(threatplaybook=self.threatplaybook, vul_result=vul,
                                                               project=self.project, target=self.target, scan=scan,
                                                               token=self.token)
                        if brakeman_results:
                            logger.info(msg=brakeman_results)
                        else:
                            logger.warn(msg='Error while parsing Brakeman results')
                else:
                    logger.warn(msg='Error while creating Scan')
            else:
                logger.warn(msg='Error while creating Scan Query')
        else:
            logger.warn(msg='Could not fetch results from file')
            exit(1)
