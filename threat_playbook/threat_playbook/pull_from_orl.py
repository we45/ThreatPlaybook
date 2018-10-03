from pymongo import MongoClient
import yaml
import os

base_cwes = [89,94,79,611,639,295,319,502,284,287]
YAML_PATH = '/Users/abhaybhargav/Documents/Code/Python/ThreatPlaybook/threat_playbook/vul_repo'

client = MongoClient('localhost', 27017)
db = client.orl_db
orl = db.vulns

def write_to_yaml_file(cwe, vul_dict):
    file_name = '{}/{}.yaml'.format(YAML_PATH, cwe)
    with open(file_name, 'w') as yfile:
        yfile.write(yaml.dump(vul_dict, default_flow_style=False))

for single in base_cwes:
    vuln = orl.find_one({'cwe': single}, {'aliases': 0, 'examples': 0, 'indexed': 0, 'intro_time': 0,
                                          'owasp': 0, 'name': 0, 'affected_users': 0,
                                          'discoverability': 0, 'exploitability': 0, 'damage': 0,
                                          'reproducibility': 0, 'cvss': 0, '_id': 0, 'languages': 0})
    single_vul_dict = {}
    single_vul_dict['description'] = str(vuln['description'])
    single_vul_dict['risk_comps'] = [str(s) for s in vuln['risk_technology']]
    single_vul_dict['risk'] = [dict([(str(k), str(v)) for k, v in one.items()]) for one in vuln['risk']]
    single_vul_dict['mitigations'] = [dict([(str(k), str(v)) for k, v in one.items()]) for one in vuln['mitigations']]
    write_to_yaml_file(single, single_vul_dict)



