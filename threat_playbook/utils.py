from models import *
import json
from base64 import b64encode


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

