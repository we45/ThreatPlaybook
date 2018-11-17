from models import *
import json
from base64 import b64encode
from schema import Schema, And, Use, Optional
import lxml.etree as xml
import re
import sys

vul_schema = Schema(
    {
        'cwe': And(Use(int)),
        'name': basestring,
        'tool': basestring,
        'severity': And(Use(int), lambda n: 0 <= n <= 3),
        'description': basestring,
        'target_name': basestring,
        Optional('observation'): basestring,
        Optional('remediation'): basestring,
    },
    ignore_extra_keys=False
)


def parse_zap_json_file(zap_file, target, session, uri):
    with open(zap_file, 'r') as zapfile:
        zap_data = json.loads(zapfile.read())
        alerts = None
        pre_alerts = zap_data['Report']['Sites']
        if isinstance(pre_alerts, list):
            for pre in pre_alerts:
                if uri in pre['Host']:
                    alerts = pre
        if isinstance(pre_alerts, dict):
            alerts = pre_alerts
        
        alerts = alerts['Alerts']['AlertItem']
        if alerts:
            if isinstance(alerts, dict):
                alerts = [alerts]
            if isinstance(alerts, list):
                for alert in alerts:
                    vul = Vulnerability()
                    vul.tool = 'zap'
                    vul.target = target
                    vul.name = alert['Alert']
                    vul.severity = {
                        'High': 3,
                        'Medium': 2,
                        'Low': 1
                    }.get(alert['RiskDesc'], 0)
                    vul.description = alert['Desc']
                    vul.cwe = alert['CWEID']
                    vul.remediation = alert['Solution']
                    vul.evidences += _map_alert_to_evidence(alert)

                    all_linked_models = ThreatModel.objects(cwe=alert['CWEID'])
                    second_link_models = ThreatModel.objects(related_cwes=alert['CWEID'])
                    if len(all_linked_models) > 0:
                        rel_models = []
                        [rel_models.append(one) for one in all_linked_models]
                        model_ids = [model.id for model in rel_models]
                        vul.models.extend(model_ids)
                    if len(second_link_models) > 0:
                        slink_models = []
                        [slink_models.append(one) for one in second_link_models]
                        s_model_ids = [model.id for model in slink_models]
                        vul.models.extend(s_model_ids)
                    vul.session = session
                    vul.target = target
                    vul.save()
            else:
                raise Exception('Unable to parse alerts in report.')


def pp_json(file_content):
    return json.dumps(json.loads(file_content), indent=4, sort_keys=True)


def manage_nikto_xml_file(xml_file):
    try:
        nreport = xml.parse(xml_file)   
        root_elem = nreport.getroot()				
        scans = root_elem.findall('niktoscan/scandetails')
        report_content = ''
        for scan in scans:
            report_content += _format_scan_result(scan)
        return report_content

    except BaseException as e:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        print('Error: {0} {1}'.format(e, exc_traceback.tb_lineno))


def manage_testssl_json_file(json_file):
    try:
        with open(json_file, 'r') as testssl_json:
            testssl_report = json.loads(testssl_json.read())
            req_key = [
                'Invocation',
                'at',
                'version',
                'openssl',
                'startTime',
                'scanTime'
            ]
            header = ''
            for key in req_key:
                header += '{lbl}: {v}\n'.format(lbl=key.capitalize(), v=str(testssl_report.get(key, '')))
            header += '\n\n'

            scan_results_str = ''
            scan_results = testssl_report['scanResult']
            for target in scan_results:
                scan_results_str += _format_target(target)
            return header + scan_results_str
 
    except BaseException as e:
        print('Unable to parse JSON File')
        exc_type, exc_value, exc_traceback = sys.exc_info()
        print('Error: {0} {1}'.format(e, exc_traceback.tb_lineno))


def manage_recon_results(recon_file, tool):
    content = ""
    if tool in ['nmap', 'wfuzz']:
        with open(recon_file, 'r') as plainfile:
            content = plainfile.read()
    elif tool in ['sslyze', 'shodan']:
        with open(recon_file, 'r') as json_file:
            content = pp_json(json_file.read())
    elif tool == 'nikto':
        content = manage_nikto_xml_file(recon_file)
    elif tool == 'testssl':
        content = manage_testssl_json_file(recon_file)
    return content


def manage_nodejsscan_results(nfile, target, session):
    results = json.load(open(nfile, 'r'))
    default_dict = {}
    for vul_type, vul_list in results.get('sec_issues').items():
        for individual_vul_details in vul_list:
            title = individual_vul_details.get('title', '')
            default_dict[title] = {
                'description': individual_vul_details.get('description'),
                'evidences': []
            }
            evidence = {'url': individual_vul_details.get('filename'),
                        'name': 'File: {0}, Line no: {1}'.format(individual_vul_details.get('path'),
                                                                 individual_vul_details.get('line')),
                        'log': individual_vul_details.get('lines')}
            default_dict[title]['evidences'] = [evidence]
    for individual_vul_title, individual_vul_detail in default_dict.items():
        vul_dict = Vulnerability()
        vul_dict.name = individual_vul_title
        vul_dict.tool = 'NodeJsScan'
        vul_dict.severity = 2
        vul_dict.target = target
        vul_dict.description = individual_vul_detail['description']
        all_evidences = individual_vul_detail['evidences']
        vul_evidences = []
        if len(all_evidences) > 0:
            for single_evidence in all_evidences:
                vul_evid = VulnerabilityEvidence()
                vul_evid.url = single_evidence.get('url', '')
                vul_evid.name = single_evidence.get('name', '')
                vul_evid.log = b64encode(single_evidence.get('log', ''))
                vul_evidences.append(vul_evid)

        vul_dict.evidences = vul_evidences

        vul_dict.session = session
        vul_dict.save()


def manage_bandit_results(json_file, target, session):
    results = json.load(open(json_file, 'r'))
    default_dict = {}
    sev_con_dict = {
        'LOW': 1,
        'MEDIUM': 2,
        'HIGH': 3
    }
    for vul_result in results.get('results', []):
        default_dict[(vul_result.get('test_id'))] = {'description': '', 'evidences': [], 'vul_name': '',
                                                     'confidence': 2, 'severity': 2}
        evidence = {
            'url': vul_result.get('filename', ''),
            'name': 'File :{0}, Line no:{1}'.format(vul_result.get('filename', ''), vul_result.get('line_number', '')),
            'log': vul_result.get('code', '')
        }
        test_id = vul_result.get('test_id')
        default_dict[test_id]['description'] = vul_result.get('issue_text', '')
        default_dict[test_id]['evidences'].append(evidence)
        default_dict[test_id]['vul_name'] = vul_result.get('test_name', '')
        default_dict[test_id]['confidence'] = sev_con_dict.get(
            vul_result.get('issue_confidence', 'MEDIUM'))
        default_dict[test_id]['severity'] = sev_con_dict.get(
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
        if all_evidences:
            for single_evidence in all_evidences:
                vul_evid = VulnerabilityEvidence()
                vul_evid.url = single_evidence.get('url', '')
                vul_evid.name = single_evidence.get('name', '')
                vul_evid.log = b64encode(single_evidence.get('log', ''))
                vul_evidences.append(vul_evid)

        vul_dict.evidences = vul_evidences
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
            code += 'code - {0}'.format(vul.get('code', '') or '')
            evid_desc = 'File :{0}, Line :{1}'.format(filename, line_num)
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
            vul_dict.severity = data.get('severity', 1),
            vul_dict.target = target
            vul_dict.description = data.get('description', '')
            all_evidences = data.get('evids', [])
            vul_evidences = []
            if len(all_evidences) > 0:
                for single_evidence in all_evidences:
                    vul_evid = VulnerabilityEvidence()
                    vul_evid.url = single_evidence.get('url', "")
                    vul_evid.name = single_evidence.get('name', "")
                    vul_evid.log = b64encode(single_evidence.get("log", ""))
                    vul_evidences.append(vul_evid)

            vul_dict.evidences = vul_evidences
            vul_dict.session = session
            vul_dict.save()


def manage_burp_xml_file(xml_file,  target, session, uri):
    try:
        nreport = xml.parse(xml_file)
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
        for v in vuls:
            obj = root_elem.xpath(p, name=v)
            # url_param_list = []
            all_evidences = []
            parent_obj = None
            for u in obj:
                parent_obj = u.getparent()
                req = parent_obj.find('requestresponse/request')
                res = parent_obj.find('requestresponse/response')
                request = response = b64encode('')
                if req is not None:
                    is_base64_encoded = True if req.get('base64') == 'true' else False
                    if is_base64_encoded:
                        request = req.text.decode('base64')
                    else:
                        request = req.text
                    is_base64_encoded = True if res.get('base64') == 'true' else False
                    if is_base64_encoded:
                        response = res.text.decode('base64')
                    else:
                        response = res.text
                log = b64encode(request + '\n\n\n' + response.split('\r\n\r\n')[0] + '\n\n')
                url = '%s%s' % (parent_obj.findtext('host', default=target), parent_obj.findtext('path', default=''))
                all_evidences.append({
                    'url': url,
                    'log': log,
                    'param': parent_obj.findtext('location', default=''),
                    'attack':  parent_obj.findtext('issueDetail', default=''),
                    'evidence': request + '\n\n\n' + response.split('\r\n\r\n')[0]    
                })
            # TODO: Is this really the last parent_obj from the loop? Seems a bit arbitrary...
            if not parent_obj:
                return
            vul_name = parent_obj.findtext('name', default='')
            severity = parent_obj.findtext('severity', '')
            if severity:
                severity = severity_dict.get(severity)
            desc = parent_obj.findtext('issueBackground', default='')
            solution = parent_obj.findtext('remediationBackground', default='')

            vul_dict = Vulnerability()
            vul_dict.name = re.sub('<[^<]+?>', '', vul_name)
            vul_dict.tool = "Burp"
            vul_dict.severity = severity
            vul_dict.description = re.sub('<[^<]+?>', '', desc)
            vul_dict.observation = ''  # TODO: Is there really nothing else to put in here?
            vul_dict.remediation = re.sub('<[^<]+?>', '', solution)
            vul_dict.target = target
            vul_evidences = []
            for single_evidence in all_evidences:
                vul_evid = VulnerabilityEvidence()
                vul_evid.url = single_evidence.get('url', '')
                vul_evid.log = single_evidence.get('log', '')
                vul_evid.param = single_evidence.get('param', '')
                vul_evid.attack = single_evidence.get('attack', '')
                vul_evid.evidence = single_evidence.get('evidence', '')
                print(vul_evid)
                vul_evidences.append(vul_evid)
            vul_dict.evidences = vul_evidences
            vul_dict.session = session
            vul_dict.save()

    except BaseException as e:
        print('Unable to parse XML File')
        exc_type, exc_value, exc_traceback = sys.exc_info()
        print('Error: {0} {1}'.format(e, exc_traceback.tb_lineno))
    

def manage_npm_audit_file(json_file, target, session):
    results = json.load(open(json_file, 'r'))
    all_advisories = results.get('advisories', [])
    severity_dict = {
        'moderate': 2,
        'low': 1,
        'critical': 3
    }
    default_dict = {}
    for advisory in all_advisories:
        title = all_advisories.get(advisory).get('title')
        default_dict[title] = {
            'description': '',
            'evidences': [],
            'remediation': '',
            'severity': 2
        }
        for finding in all_advisories.get(advisory).get('findings'):
            for path in finding.get('paths'):
                advisory = all_advisories.get(advisory, {})
                evidence = {
                    'url': all_advisories.get(advisory).get('module_name'),
                    'name': 'File: {0}'.format(path)
                }
                default_dict[title]['evidences'] = [evidence]
                default_dict[title]['description'] = advisory.get('overview')
                default_dict[title]['cwe'] = int(advisory.get('cwe', '').split('-')[-1])
                default_dict[title]['remediation'] = advisory.get('recommendation')
                default_dict[title]['severity'] = severity_dict.get(advisory.get('severity'), 2)

    for individual_vul_title, individual_vul_detail in default_dict.items():
        vul_dict = Vulnerability()
        vul_dict.name = individual_vul_title
        vul_dict.tool = 'Npm Audit'
        vul_dict.severity = individual_vul_detail['severity']
        vul_dict.target = target
        vul_dict.cwe = individual_vul_detail.get('cwe', None)
        vul_dict.description = individual_vul_detail['description']
        vul_dict.remediation = individual_vul_detail['remediation']
        all_evidences = individual_vul_detail['evidences']
        vul_evidences = []
        for single_evidence in all_evidences:
            vul_evid = VulnerabilityEvidence()
            vul_evid.url = single_evidence['url']
            vul_evid.name = single_evidence['name']
            vul_evidences.append(vul_evid)

        vul_dict.session = session
        vul_dict.save()
        saved_vul = Vulnerability.objects.get(id = vul_dict.id)
        all_linked_models = ThreatModel.objects(cwe=individual_vul_detail.get('cwe'))
        second_link_models = ThreatModel.objects(related_cwes=individual_vul_detail.get('cwe'))
        if len(all_linked_models) > 0:
            rel_models = []
            [rel_models.append(one) for one in all_linked_models]
            model_ids = [model.id for model in rel_models]
            saved_vul.models.extend(model_ids)
        if len(second_link_models) > 0:
            slink_models = []
            [slink_models.append(one) for one in second_link_models]
            s_model_ids = [model.id for model in slink_models]
            saved_vul.models.extend(s_model_ids)
        saved_vul.save()


def _map_alert_to_evidence(alert):
    """
    Maps a list of alerts to a collection of evidence objects

    :param      list|dict   alert: Alert dictionary or list of alert dictionaries

    :return:    list(VulnerabilityEvidence) Evidence collection translated from alerts
    """

    evidence_collection = []
    include_log = True
    key_map = {
        'URI': 'url',
        'Param': 'param',
        'Attack': 'attack',
        'Evidence': 'evidence',
        'OtherInfo': 'other_info',
    }
    if isinstance(alert['Item'], dict):
        alert['Item'] = [alert['Item']]
        include_log = False
    for item in alert['Item']:
        evidence = VulnerabilityEvidence()
        # Copy alert data into evidence object
        for ak, ek in key_map.items():
            setattr(evidence, ek, item.get(ak))
        # Log is only included if we got a list of alerts
        evidence.log = b64encode(
            '{0}\n{1}\n\n{2}'.format(
                item.get('RequestHeader', ''),
                item.get('RequestBody', ''),
                item.get('ResponseHeader', '').encode('UTF-8')
            )
        ) if include_log else None
        evidence_collection.append(evidence)
    return evidence_collection


def _format_scan_result(scan):
    """
    Formats a scan result into a text block

    :param      xml.Element     scan:   A scan result
    :return:    str             A text representation of the result
    """
    target_map = {
        'Target IP': 'targetip',
        'Target Hostname': 'targethostname',
        'Target Port': 'targetport',
        'HTTP Server': 'targetbanner',
        'Start Time': 'starttime',
        'Site Link(name)': 'sitename',
        'Site Link (IP)': 'siteip',
    }
    target = ''
    for lbl, k in target_map.items():
        target += '{0}: {1}\n'.format(lbl, scan.get(k, ''))
    target += '\n'
    for it in scan.findall('item'):
        target += _format_item(it)


def _format_item(item):
    """
    Formats an item as attached to
    :param      xml.Element item: XML-Element to extract data from
    :return:    str     String representation of item details
    """
    return '''URI: {uri}
HTTP Method: {method}
Description: {description}
Test Link:   {namelink}
\t\t\t{iplink}
OSVDB Link:  {osvdblink}

'''.format(
        uri=item.findtext('uri', default=''),
        method=item.get('method', default=''),
        description=item.findtext('description', default=''),
        namelink=item.findtext('namelink', default=''),
        iplink=item.findtext('iplink', default=''),
        osvdblink=item.get('osvdblink', default='')
    )


def _format_target(target):
    """
    Formats a target into a text block

    :param      xml.Element     target:   A scan result
    :return:    str             String representation of the result
    """
    target_map = {
        'Target IP': 'targetip',
        'Target Host': 'target host',
        'IP': 'ip',
        'Port': 'port',
        'Service': 'service',
    }
    target_str = 'Target Info:\n\n'
    for lbl, k in target_map.items():
        target_str += '{0}: {1}\n'.format(lbl, target.get(k, ''))
    target_str += '\n'
    target_str += _format_key_data(target)
    return target_str


def _format_key_data(target):
    """
    Formats key data

    :param  dict    target: Data dictionary to be formatted into a string

    :return:    str     String representation of target
    """
    key_data = [
        'protocols',
        'grease',
        'ciphers',
        'pfs',
        'serverPreferences',
        'serverDefaults',
        'headerResponse',
        'cipherTests',
        'browserSimulations'
    ]
    key_details = {
        'ID': 'id',
        'Severity': 'severity',
        'CVE': 'cve',
        'CWE': 'cwe',
        'Finding': 'finding'
    }
    report = ''
    for key in key_data:
        results = target.get(key)
        if not results:
            break
        report += key.capitalize() + ': ' + '\n\n'
        for result in results:
            for lbl, k in key_details.items():
                report += '{lbl}: {r}\n'.format(lbl=lbl, r=result.get(k, ''))
        report += '\n\n'
    return report
