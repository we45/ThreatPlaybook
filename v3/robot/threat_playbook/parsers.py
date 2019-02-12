from utils import clean_string
from base64 import b64encode
from utils import create_vulnerability, create_evidence, _post_query
from validations import validate_vulnerability_response_name, validate_vulnerability_response_id, \
    validate_evidence_response


def parse_bandit_file(threatplaybook, vul_result, project, target, scan):
    severity_dict = {'LOW': 1, 'MEDIUM': 2, 'HIGH': 3}

    vul_dict = {
        'name': str(vul_result.get('test_name', '')),
        'tool': 'bandit',
        'description': str(vul_result.get('issue_text', '')),
        'project': str(project),
        'target': str(target),
        'scan': str(scan),
        'cwe': int(vul_result.get('cwe', 0)),
        'observation': str(vul_result.get('observation', '')),
        'severity': int(severity_dict.get(vul_result.get('issue_severity', 'MEDIUM'))),
        'remediation': str(vul_result.get('remediation', '')),
    }
    create_vulnerability_query = create_vulnerability(vul_dict=vul_dict)
    if create_vulnerability_query:
        response = _post_query(threatplaybook=threatplaybook, query=create_vulnerability_query)
        if response:
            cleaned_response_name = validate_vulnerability_response_name(content=response)
            vulnId = validate_vulnerability_response_id(content=response)
            evidence = {
                'name': str(clean_string('File :{}, Line no:{}'.format(vul_result.get('filename'),
                                                                       vul_result.get('line_number')))),
                'url': str(clean_string(vul_result.get('filename'))),
                'vulnId': str(vulnId),
                'log': str(clean_string(vul_result.get('code')))
            }
            create_evidence_query = create_evidence(evidence=evidence)
            if create_evidence_query:
                evidence_response = _post_query(threatplaybook=threatplaybook, query=create_evidence_query)
                if evidence_response:
                    cleaned_evidence_response = validate_evidence_response(content=evidence_response)
                    if cleaned_evidence_response:
                        print('Evidence Created: {}'.format(cleaned_evidence_response))
                else:
                    return {'error': 'Error while creating Vulnerability Evidence'}
            else:
                return {'error': 'Error while creating Vulnerability Evidence Query'}

            return {'success': cleaned_response_name}
        else:
            return {'error': 'Error while creating Vulnerability'}
    else:
        return {'error': 'Error while creating Vulnerability Query'}


def parse_nodejsscan_file(threatplaybook, vul_result, project, target, scan):
    vul_dict = {
        'name': str(vul_result.get('title')),
        'tool': 'NodeJsScan',
        'description': str(vul_result.get('description')),
        'project': str(project),
        'target': str(target),
        'scan': str(scan),
        'cwe': int(vul_result.get('cwe', 0)),
        'observation': str(vul_result.get('observation', '')),
        'remediation': str(vul_result.get('remediation', ''))
    }
    create_vulnerability_query = create_vulnerability(vul_dict=vul_dict)
    if create_vulnerability_query:
        response = _post_query(threatplaybook=threatplaybook, query=create_vulnerability_query)
        if response:
            cleaned_response_name = validate_vulnerability_response_name(content=response)
            vulnId = validate_vulnerability_response_id(content=response)
            evidence = {
                'name': str(clean_string('File: {}, Line no: {}'.format(vul_result.get('path'),
                                                                        vul_result.get('line')))),
                'url': str(clean_string(vul_result.get('filename'))),
                'vulnId': str(vulnId),
                'log': str(clean_string(vul_result.get('lines'))),
                }
            create_evidence_query = create_evidence(evidence=evidence)
            if create_evidence_query:
                evidence_response = _post_query(threatplaybook=threatplaybook, query=create_evidence_query)
                if evidence_response:
                    cleaned_evidence_response = validate_evidence_response(content=evidence_response)
                    if cleaned_evidence_response:
                        print('Evidence Created: {}'.format(cleaned_evidence_response))
                    else:
                        print('No Vulnerability Evidence')
            else:
                return {'error': 'Error while creating Vulnerability Evidence Query'}
            return {'success': cleaned_response_name}
        else:
            return {'error': 'Error while creating Vulnerability'}
    else:
        return {'error': 'Error while creating Vulnerability Query'}


def parse_npmaudit_file(threatplaybook, vul_result, project, target, scan):
    severity_dict = {'moderate': 2, 'low': 1, 'critical': 3}

    vul_dict = {
        'name': str(clean_string(vul_result.get('title'))),
        'tool': 'Npm Audit',
        'description': str(clean_string(vul_result.get('overview'))),
        'project': str(project),
        'target': str(target),
        'scan': str(scan),
        'cwe': int(vul_result.get('cwe', '').split('-')[-1]),
        'observation': str(clean_string(vul_result.get('observation'))),
        'severity': int(severity_dict.get(vul_result.get('severity'), 0)),
        'remediation': str(clean_string(vul_result.get('recommendation')))
    }
    create_vulnerability_query = create_vulnerability(vul_dict=vul_dict)
    if create_vulnerability_query:
        response = _post_query(threatplaybook=threatplaybook, query=create_vulnerability_query)
        if response:
            cleaned_response_name = validate_vulnerability_response_name(content=response)
            vulnId = validate_vulnerability_response_id(content=response)
            for finding in vul_result.get('findings'):
                for path in finding.get('paths'):
                    evidence = {
                        'name': str(clean_string('File: {0}'.format(path))),
                        'url': str(clean_string(vul_result.get('module_name'))),
                        'vulnId': str(vulnId)
                    }
                    create_evidence_query = create_evidence(evidence=evidence)
                    if create_evidence_query:
                        evidence_response = _post_query(threatplaybook=threatplaybook, query=create_evidence_query)
                        if evidence_response:
                            cleaned_evidence_response = validate_evidence_response(content=evidence_response)
                            if cleaned_evidence_response:
                                print('Evidence Created: {}'.format(cleaned_evidence_response))
                            else:
                                print('No Vulnerability Evidence')
                    else:
                        return {'error': 'Error while creating Vulnerability Evidence Query'}
            return {'success': cleaned_response_name}
        else:
            return {'error': 'Error while creating Vulnerability'}
    else:
        return {'error': 'Error while creating Vulnerability Query'}


def parse_zap_file(threatplaybook, vul_result, project, target, scan):
    severity_dict = {'High': 3, 'Medium': 2, 'Low': 1}
    vul_dict = {
        'name': str(clean_string(vul_result.get('Alert'))),
        'tool': 'zap',
        'description': str(clean_string(vul_result.get('Desc'))),
        'project': str(project),
        'target': str(target),
        'scan': str(scan),
        'cwe': int(vul_result.get('CWEID')),
        'observation': str(clean_string(vul_result.get('observation'))),
        'severity': int(severity_dict.get(vul_result.get('RiskDesc'), 0)),
        'remediation': str(clean_string(vul_result.get('Solution')))
    }
    create_vulnerability_query = create_vulnerability(vul_dict=vul_dict)
    if create_vulnerability_query:
        response = _post_query(threatplaybook=threatplaybook, query=create_vulnerability_query)
        if response:
            cleaned_response_name = validate_vulnerability_response_name(content=response)
            vulnId = validate_vulnerability_response_id(content=response)
            if isinstance(vul_result['Item'], dict):
                vul_result['Item'] = [vul_result['Item']]
            for item in vul_result['Item']:
                evidence = {
                    'name': str(item.get('name', 'None')),
                    'url': str(clean_string(item.get('URI'))),
                    'vulnId': str(vulnId),
                    'param': str(clean_string(item.get('Param'))),
                    'log': str(b64encode('RequestHeader: {}  RequestBody: {}  ResponseHeader: {}'.format(
                                        item.get('RequestHeader', ''),
                                        item.get('RequestBody', ''),
                                        item.get('ResponseHeader', '')).encode('UTF-8'))),
                    'attack': str(clean_string(item.get('Attack'))),
                    'otherInfo': str(clean_string(item.get('OtherInfo'))),
                    'evidence': str(clean_string(item.get('Evidence'))),
                    }
                create_evidence_query = create_evidence(evidence=evidence)
                if create_evidence_query:
                    evidence_response = _post_query(threatplaybook=threatplaybook, query=create_evidence_query)
                    cleaned_evidence_response = validate_evidence_response(content=evidence_response)
                    if cleaned_evidence_response:
                        print('Evidence Created: {}'.format(cleaned_evidence_response))
                    else:
                        print('No Vulnerability Evidence')
                else:
                    return {'error': 'Error while creating Vulnerability Evidence Query'}
            return {'success': cleaned_response_name}
        else:
            return {'error': 'Error while creating Vulnerability'}
    else:
        return {'error': 'Error while creating Vulnerability Query'}


def parse_brakeman_file(threatplaybook, vul_result, project, target, scan):
    confidence_dict = {"High": 3, "Medium": 2, "Low": 1}
    vul_dict = {
        'name': str(clean_string(vul_result.get('warning_type', 'Unknown'))),
        'tool': 'Brakeman',
        'description': str(clean_string(vul_result.get('message', ''))),
        'project': str(project),
        'target': str(target),
        'scan': str(scan),
        'cwe': int(vul_result.get('cwe', 0)),
        'observation': str(clean_string(vul_result.get('observation', ''))),
        'severity': int(confidence_dict.get(vul_result.get('confidence', 'Low'), 1)),
        'remediation': str(clean_string(vul_result.get('remediation', '')))
    }
    create_vulnerability_query = create_vulnerability(vul_dict=vul_dict)
    if create_vulnerability_query:
        response = _post_query(threatplaybook=threatplaybook, query=create_vulnerability_query)
        if response:
            cleaned_response_name = validate_vulnerability_response_name(content=response)
            vulnId = validate_vulnerability_response_id(content=response)
            file = clean_string(vul_result.get('file', ''))
            line_num = clean_string(vul_result.get('line', ''))
            location = vul_result.get('location', {})
            code = ''
            if location is not None:
                for key, value in location.items():
                    code += '{0} - {1}'.format(key, value)
            code += 'code - {0}'.format(vul_result.get('code', '') or '')
            evid_desc = 'File :{0}, Line :{1}'.format(file, line_num)
            evidence = {
                'name': str(evid_desc),
                'url': str(file),
                'vulnId': str(vulnId),
                'log': str(clean_string(code))
                }
            create_evidence_query = create_evidence(evidence=evidence)
            if create_evidence_query:
                evidence_response = _post_query(threatplaybook=threatplaybook, query=create_evidence_query)
                cleaned_evidence_response = validate_evidence_response(content=evidence_response)
                if cleaned_evidence_response:
                    print('Evidence Created: {}'.format(cleaned_evidence_response))
                else:
                    print('No Vulnerability Evidence')
            else:
                return {'error': 'Error while creating Vulnerability Evidence Query'}
            return {'success': cleaned_response_name}
        else:
            return {'error': 'Error while creating Vulnerability'}
    else:
        return {'error': 'Error while creating Vulnerability Query'}
