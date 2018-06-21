from models import *
import json
from base64 import b64encode
from schema import Schema, And, Use, Optional

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