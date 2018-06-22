from models import *
import json
from base64 import b64encode
from schema import Schema, And, Use, Optional
import lxml.etree as xml
import os
import re

# script_dir = os.path.dirname(__file__)
# file_path = os.path.join(script_dir, 'burp_db.json')
# cwe_dict = json.load(open("burp_db.json",'r'))

burp_dict_string = '''
{
	"1050112": ["643", "XPath injection"],
	"6292992": ["200", "Robots.txt file"],
	"5244416": ["16", "Cookie without HttpOnly flag set"],
	"6291712": ["548", "Directory listing"],
	"7340288": ["524", "Cacheable HTTPS response"],
	"5244928": ["200", "Password field with autocomplete enabled"],
	"5243136": ["601", "Open redirection"],
	"5245953": ["116", "Ajax request header manipulation (reflected DOM-based)"],
	"16778240": ["16", "Mixed content"],
	"2097937": ["79", "Cross-site scripting (reflected DOM-based)"],
	"2097936": ["79", "Cross-site scripting (DOM-based)"],
	"2097938": ["79", "Cross-site scripting (stored DOM-based)"],
	"2098176": ["942", "Flash cross-domain policy"],
	"1049088": ["89", "SQL injection"],
	"3146272": ["918", "External service interaction (SMTP)"],
	"2097408": ["79", "Cross-site scripting (stored)"],
	"5246210": ["400", "Denial of service (stored DOM-based)"],
	"2098944": ["352", "Cross-site request forgery"],
	"5246465": ["20", "HTML5 web message manipulation (reflected DOM-based)"],
	"5243648": ["16", "Cookie scoped to parent domain"],
	"5246464": ["20", "HTML5 web message manipulation (DOM-based)"],
	"1051904": ["94", "Server-side JavaScript code injection"],
	"5246466": ["20", "HTML5 web message manipulation (stored DOM-based)"],
	"4196608": ["502", "Serialized object in HTTP message"],
	"2098017": ["79", "Client-side XPath injection (reflected DOM-based)"],
	"2098016": ["79", "Client-side XPath injection (DOM-based)"],
	"4197632": ["20", "Suspicious input transformation (reflected)"],
	"2097928": ["116", "Client-side template injection"],
	"5246977": ["20", "Link manipulation (reflected DOM-based)"],
	"2097920": ["79", "Cross-site scripting (reflected)"],
	"2098018": ["79", "Client-side XPath injection (stored DOM-based)"],
	"1052672": ["94", "Unidentified code injection"],
	"1052448": ["917", "Expression Language injection"],
	"4194576": ["16", "X-Forwarded-For dependent response"],
	"8389376": ["16", "HTML uses unrecognized charset"],
	"4195840": ["642", "ASP.NET ViewState without MAC enabled"],
	"6292816": ["200", "Private key disclosed"],
	"5246208": ["400", "Denial of service (DOM-based)"],
	"5246209": ["400", "Denial of service (reflected DOM-based)"],
	"5245440": ["16", "HTTP TRACE method is enabled"],
	"8388864": ["436", "Multiple content types specified"],
	"5246976": ["20", "Link manipulation (DOM-based)"],
	"1048832": ["77", "OS command injection"],
	"5243392": ["614", "SSL cookie without secure flag set"],
	"2098000": ["73", "Local file path manipulation (DOM-based)"],
	"2098001": ["73", "Local file path manipulation (reflected DOM-based)"],
	"2098002": ["73", "Local file path manipulation (stored DOM-based)"],
	"2097953": ["94", "JavaScript injection (reflected DOM-based)"],
	"2097952": ["94", "JavaScript injection (DOM-based)"],
	"5243154": ["601", "Open redirection (stored DOM-based)"],
	"5243153": ["601", "Open redirection (reflected DOM-based)"],
	"5243152": ["601", "Open redirection (DOM-based)"],
	"2097954": ["94", "JavaScript injection (stored DOM-based)"],
	"5245344": ["693", "Frameable response (potential Clickjacking)"],
	"134217728": ["0", "Extension generated issue"],
	"6292480": ["200", "Social security numbers disclosed"],
	"1052160": ["94", "Perl code injection"],
	"4195072": ["598", "Password submitted using GET method"],
	"6291968": ["200", "Email addresses disclosed"],
	"2098432": ["942", "Silverlight cross-domain policy"],
	"5246722": ["20", "HTML5 storage manipulation (stored DOM-based)"],
	"5246721": ["20", "HTML5 storage manipulation (reflected DOM-based)"],
	"5246720": ["20", "HTML5 storage manipulation (DOM-based)"],
	"5247232": ["20", "Document domain manipulation (DOM-based)"],
	"5247233": ["20", "Document domain manipulation (reflected DOM-based)"],
	"2098033": ["79", "Client-side JSON injection (reflected DOM-based)"],
	"2098032": ["79", "Client-side JSON injection (DOM-based)"],
	"2098034": ["79", "Client-side JSON injection (stored DOM-based)"],
	"5247489": ["20", "DOM data manipulation (reflected DOM-based)"],
	"5247488": ["20", "DOM data manipulation (DOM-based)"],
	"1049600": ["611", "XML external entity injection"],
	"3145984": ["319", "Cleartext submission of password"],
	"16777728": ["326", "Unencrypted communications"],
	"5245184": ["287", "Password value set in cookie"],
	"5244160": ["829", "Cross-domain script include"],
	"2097664": ["113", "HTTP response header injection"],
	"4197888": ["20", "Suspicious input transformation (stored)"],
	"4194592": ["16", "User agent-dependent response"],
	"8389632": ["16", "Content type incorrectly stated"],
	"4194816": ["204", "Password returned in later response"],
	"2097970": ["89", "Client-side SQL injection (stored DOM-based)"],
	"4195328": ["598", "Password returned in URL query string"],
	"2099200": ["93", "SMTP header injection"],
	"5245698": ["565", "Cookie manipulation (stored DOM-based)"],
	"4194560": ["16", "Referer-dependent response"],
	"8389888": ["16", "Content type is not specified"],
	"5245696": ["565", "Cookie manipulation (DOM-based)"],
	"5245697": ["565", "Cookie manipulation (reflected DOM-based)"],
	"1050368": ["91", "XML injection"],
	"1052928": ["96", "SSI injection"],
	"5247234": ["20", "Document domain manipulation (stored DOM-based)"],
	"5245360": ["16", "Browser cross-site scripting filter disabled"],
	"4197376": ["116", "Input returned in response (reflected)"],
	"1052432": ["94", "Python code injection"],
	"1049856": ["90", "LDAP injection"],
	"2098691": ["942", "Cross-origin resource sharing: all subdomains trusted"],
	"2098690": ["942", "Cross-origin resource sharing: unencrypted origin trusted"],
	"2097960": ["16", "Path-relative style sheet import"],
	"4195584": ["16", "Cross-domain POST"],
	"4197120": ["116", "Input returned in response (stored)"],
	"2097968": ["89", "Client-side SQL injection (DOM-based)"],
	"2097969": ["89", "Client-side SQL injection (reflected DOM-based)"],
	"1049104": ["89", "SQL injection (second order)"],
	"8389120": ["16", "HTML does not specify charset"],
	"6292736": ["200", "Credit card numbers disclosed"],
	"5247490": ["20", "DOM data manipulation (stored DOM-based)"],
	"6291584": ["15", "Database connection string disclosed"],
	"1049216": ["10", "ASP.NET tracing enabled"],
	"7340544": ["310", "Base64-encoded data in parameter"],
	"1050624": ["11", "ASP.NET debugging enabled"],
	"6292224": ["200", "Private IP addresses disclosed"],
	"5245312": ["434", "File upload functionality"],
	"4195456": ["598", "SQL statement in request parameter"],
	"2098688": ["942", "Cross-origin resource sharing"],
	"2098689": ["942", "Cross-origin resource sharing: arbitrary origin trusted"],
	"5244672": ["200", "Session token in URL"],
	"3146240": ["918", "External service interaction (DNS)"],
	"16777984": ["523", "Strict transport security not enforced"],
	"1049344": ["22", "File path traversal"],
	"1051392": ["73", "File path manipulation"],
	"5245952": ["116", "Ajax request header manipulation (DOM-based)"],
	"5245954": ["116", "Ajax request header manipulation (stored DOM-based)"],
	"4196096": ["776", "XML entity expansion"],
	"1051648": ["94", "PHP code injection"],
	"1051136": ["610", "Out-of-band resource load (HTTP)"],
	"4196864": ["16", "Duplicate cookies set"],
	"1052416": ["94", "Ruby code injection"],
	"3146256": ["918", "External service interaction (HTTP)"],
	"5246978": ["20", "Link manipulation (stored DOM-based)"],
	"5243904": ["200", "Cross-domain Referer leakage"],
	"16777472": ["295", "SSL certificate"],
	"4196352": ["698", "Long redirection response"],
	"2097984": ["441", "WebSocket hijacking (DOM-based)"],
	"2097985": ["441", "WebSocket hijacking (reflected DOM-based)"],
	"2097986": ["441", "WebSocket hijacking (stored DOM-based)"],
	"6291632": ["18", "Source code disclosure"],
	"1050880": ["650", "HTTP PUT method is enabled"],
	"1052800": ["94", "Server-side template injection"]
}
'''

cwe_dict = json.loads(burp_dict_string)

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

                all_linked_models = ThreatModel.objects(cwe=alert['CWEID'])
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
        vul.name = re.sub('<[^<]+?>', '', vul_name)
        vul.tool = "Burp"
        vul.severity = severity
