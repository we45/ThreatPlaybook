from models import *
import json
from base64 import b64encode
from schema import Schema, And, Use, Optional
import lxml.etree as xml
import os
import re

# script_dir = os.path.dirname(__file__)
# file_path = os.path.join(script_dir, 'burp_db.json')
cwe_dict = json.load(open("burp_db.json",'r'))

vul_schema = Schema(
    {
        'cwe': And(Use(int)),
        'name': And(str, len),
        'tool': And(str, len),
        'severity': And(Use(int), lambda n: 0 <= n <= 3),
        'description': And(str, len),
        'target_name': And(str, len),
        Optional('observation'): And(str, len),
        Optional('remediation'): And(str, len),
    },
    ignore_extra_keys=False
)

def parse_zap_json_file(zap_file, target, session):
    with open(zap_file, 'r') as zapfile:
        zap_data = json.loads(zapfile.read())

        alerts = zap_data['Report']['Sites']['Alerts']['AlertItem']
        if alerts:
            for alert in alerts:
                vul = Vulnerability()
                vul.tool = 'zap'
                vul.target = target
                vul.name = alert['Alert']
                if alert['RiskDesc'] == 'High':
                    vul.severity = 3
                elif alert['RiskDesc'] == 'Medium':
                    vul.severity = 2
                elif alert['RiskDesc'] == 'Low':
                    vul.severity = 1
                else:
                    vul.severity = 0
                vul.description = alert['Desc']
                vul.cwe = alert['CWEID']
                vul.remediation = alert['Solution']

                evidence = VulnerabilityEvidence()
                if isinstance(alert['Item'], dict):
                    evidence.url = alert['Item'].get('URI', None)
                    evidence.param = alert['Item'].get('Param', None)
                    evidence.attack = alert['Item'].get('Attack', None)
                    evidence.evidence = alert['Item'].get('Evidence', None)
                    evidence.other_info = alert['Item'].get('OtherInfo', None)
                    vul.evidences.append(evidence)
                elif isinstance(alert['Item'], list):
                    for item in alert['Item']:
                        evidence.url = item.get('URI', None)
                        evidence.param = item.get('Param', None)
                        evidence.attack = item.get('Attack', None)
                        evidence.evidence = item.get('Evidence', None)
                        evidence.log = b64encode(
                            "{0}{1} {2}{3}".format(item.get('RequestHeader', None), item.get('RequestBody', None),
                                                   item.get('ResponseHeader', None), item.get('ResponseBody', None)))
                        evidence.other_info = item.get('OtherInfo', None)
                        vul.evidences.append(evidence)

                all_linked_models = ThreatModel.objects(cwe = alert['CWEID'])
                if len(all_linked_models) > 0:
                    rel_models = []
                    [rel_models.append(one) for one in all_linked_models]
                    model_ids = [model.id for model in rel_models]
                    vul.models = model_ids

                vul.session = session
                vul.target = target
                vul.save()



def manage_recon_results(recon_file, tool):
    content = ""
    if tool == 'nmap':
        with open(recon_file, 'r') as nmapfile:
            content = nmapfile.read()
    elif tool == "wfuzz":
        with open(recon_file, 'r') as wfuzzfile:
            wfuzz_dict = json.loads(wfuzzfile.read())
        if isinstance(wfuzz_dict, list):
            for single in wfuzz_dict:
                content += "{0} - {1}\n".format(single['code'], single['url'])

    return content

def manage_nodejsscan_results(nfile, target, session):
    results = json.load(open(nfile, 'r'))
    default_dict = {}
    for vul_type, vul_list in results.get('sec_issues').items():
        for individual_vul_details in vul_list:
            default_dict[(individual_vul_details.get('title'))] = {'description': '', 'evidences': []}
            evidence = {'url': individual_vul_details.get('filename'),
                        'name': 'File: {0}, Line no: {1}'.format(individual_vul_details.get('path'),
                                                                 individual_vul_details.get('line')),
                        'log': individual_vul_details.get('lines')}
            default_dict[(individual_vul_details.get('title'))]['evidences'].append(evidence)
            default_dict[(individual_vul_details.get('title'))]['description'] = individual_vul_details.get(
                'description')
    for individual_vul_title, individual_vul_detail in default_dict.items():
        vul_dict = Vulnerability()
        vul_dict.name = individual_vul_title
        vul_dict.tool = 'NodeJsScan'
        vul_dict.severity = 2
        vul_dict.target = target
        vul_dict.description = individual_vul_detail.get('description', '')
        all_evidences = individual_vul_detail.get('evidences', [])
        vul_evidences = []
        if len(all_evidences) > 0:
            for single_evidence in all_evidences:
                vul_evid = VulnerabilityEvidence()
                vul_evid.url = single_evidence.get('url', "")
                vul_evid.name = single_evidence.get('name', "")
                vul_evid.log = b64encode(single_evidence.get("log", ""))
                vul_evidences.append(vul_evid)

        vul_dict.session = session
        vul_dict.save()


def manage_bandit_results(json_file, target, session):
    results = json.load(open(json_file, 'r'))
    default_dict = {}
    sev_con_dict = {
        "LOW": 1,
        "MEDIUM": 2,
        "HIGH": 3
    }
    for vul_result in results.get('results', []):
        default_dict[(vul_result.get('test_id'))] = {'description': '', 'evidences': [], 'vul_name': '',
                                                     'confidence': 2, 'severity': 2}
        evidence = {
            'url': vul_result.get('filename', ''),
            'name': 'File :{0}, Line no:{1}'.format(vul_result.get('filename', ''), vul_result.get('line_number', '')),
            'log': vul_result.get('code', '')}
        default_dict[(vul_result.get('test_id'))]['description'] = vul_result.get('issue_text', '')
        default_dict[(vul_result.get('test_id'))]['evidences'].append(evidence)
        default_dict[(vul_result.get('test_id'))]['vul_name'] = vul_result.get('test_name', '')
        default_dict[(vul_result.get('test_id'))]['confidence'] = sev_con_dict.get(
            vul_result.get('issue_confidence', 'MEDIUM'))
        default_dict[(vul_result.get('test_id'))]['severity'] = sev_con_dict.get(
            vul_result.get('issue_severity', 'MEDIUM'))

    for individual_vul_id, individual_vul_detail in default_dict.items():
        vul_dict = Vulnerability()
        vul_dict.name = individual_vul_detail.get('vul_name', ''),
        vul_dict.tool = 'Bandit'
        vul_dict.severity = individual_vul_detail.get('severity', 2),
        vul_dict.target = target
        vul_dict.description = individual_vul_detail.get('description', '')
        all_evidences = individual_vul_detail.get('evidences', [])
        vul_evidences = []
        if len(all_evidences) > 0:
            for single_evidence in all_evidences:
                vul_evid = VulnerabilityEvidence()
                vul_evid.url = single_evidence.get('url', "")
                vul_evid.name = single_evidence.get('name', "")
                vul_evid.log = b64encode(single_evidence.get("log", ""))
                vul_evidences.append(vul_evid)

        vul_dict.session = session
        vul_dict.save()

def manage_brakeman_results(json_file, target, session):
    confidence_dict = {
        "High": 3,
        "Medium": 2,
        "Low": 1
    }
    with open(json_file) as data_file:
        data = json.load(data_file)
        vuls = data.get('warnings', [])
        default_dict = {}
        for vul in vuls:
            vul_name = vul.get('warning_type', 'Unknown')
            if vul_name not in default_dict:
                default_dict[vul_name] = {
                    'description': vul.get('message', ''),
                    'severity': confidence_dict.get(vul.get('confidence', 'Low'), 1),
                    'evids': []
                }
            filename = vul.get('file', '')
            line_num = vul.get('line', '')
            location = vul.get('location', {})
            code = ''
            if location is not None:
                for key, value in location.items():
                    code += '{0} - {1} \n'.format(key, value)
            code += "code - {0}".format(vul.get('code', '') or '')
            evid_desc = "File :{0}, Line :{1}".format(filename, line_num)
            default_dict[vul_name]['evids'].append(
                {
                    'url': filename,
                    'name': evid_desc,
                    'log': code
                }
            )
        for name, data in default_dict.items():
            vul_dict = Vulnerability()
            vul_dict.name = name,
            vul_dict.tool = 'Brakeman'
            vul_dict.severity = data.get('severity',1),
            vul_dict.target = target
            vul_dict.description = data.get('description','')
            all_evidences = data.get('evids',[])
            vul_evidences = []
            if len(all_evidences) > 0:
                for single_evidence in all_evidences:
                    vul_evid = VulnerabilityEvidence()
                    vul_evid.url = single_evidence.get('url', "")
                    vul_evid.name = single_evidence.get('name', "")
                    vul_evid.log = b64encode(single_evidence.get("log", ""))
                    vul_evidences.append(vul_evid)

            vul_dict.session = session
            vul_dict.save()

def manage_burp_xml_file(xml_file, target, session):
    try:
        nreport = xml.parse(xml_file)
    except (xml.XMLSyntaxError, xml.ParserError):
        raise Exception("Unable to parse XML")
    root_elem = nreport.getroot()
    reg_path = r'issue/name'
    uniq_objs = root_elem.xpath(reg_path)
    vuls = set([i.text for i in uniq_objs])
    p = '{0}[text() = $name]'.format(reg_path)
    severity_dict = {
        'Information': 0,
        'Low': 1,
        'Medium': 2,
        'High': 3
    }
    burp_confidence_dict = {
        "Certain": 3,
        "Firm": 2,
        "Tentative": 1,
    }
    for v in vuls:
        obj = root_elem.xpath(p, name=v)
        url_param_list = []
        for u in obj:
            parent_obj = u.getparent()
            req = parent_obj.find('requestresponse/request')
            res = parent_obj.find('requestresponse/response')
            request = response = b64encode('')
            if req is not None:
                is_base64_encoded = True if req.get('base64') == 'true' else False
                if is_base64_encoded:
                    request = req.text
                else:
                    request = b64encode(req.text)
            if res is not None:
                is_base64_encoded = True if res.get('base64') == 'true' else False
                if is_base64_encoded:
                    response = res.text
                else:
                    response = b64encode(res.text)
            url = 'http:/%s' % (parent_obj.findtext('path', default=''))
            url_param_list.append({
                'url': parent_obj.findtext('location', default=''),
                # 'name':parent_obj.findtext('path',default=''),
                'attack': parent_obj.findtext('issueDetailItems/issueDetailItem', default=''),
                'name': parent_obj.findtext('issueDetailItems/issueDetailItem', default=''),
                'request': request,
                'response': response,
            })
        vul_name = parent_obj.findtext('name', default='')
        severity = parent_obj.findtext('severity', '')
        issue_type = parent_obj.findtext('type', '8389632')
        if severity:
            severity = severity_dict.get(severity)
        cwe_present = cwe_dict.get(issue_type, [])
        cwe = 0
        if cwe_present:
            cwe = cwe_present[0]
        desc = parent_obj.findtext('issueBackground', default='')
        solution = parent_obj.findtext('remediationBackground', default='')
        observation = parent_obj.find('issueDetail')
        confidence = parent_obj.findtext('confidence', default='')
        if confidence:
            confidence = burp_confidence_dict.get(confidence)
        if observation is not None:
            s = '''You should manually examine the application behavior and attempt to identify any unusual input validation or other obstacles that may be in place.'''
            obs = observation.text.replace(s, '')
        else:
            obs = ''

        vul = Vulnerability()
        vul.name = re.sub('<[^<]+?>', '',vul_name)
        vul.tool = "Burp"
        vul.severity = severity
