import pyjq


def validate_project_response(content):
    return pyjq.first('.data.createProject.project.name', content)


def validate_target_response(content):
    return pyjq.first('.data.createTarget.target.name', content)


def validate_vulnerability_response_name(content):
    return pyjq.first('.data.createVulnerability.vulnerability.name', content)


def validate_vulnerability_response_id(content):
    return pyjq.first('.data.createVulnerability.vulnerability.id', content)


def valid_evidence_response(content):
    return pyjq.first('.data.createVulnerabilityEvidence.vulnEvidence.name', content)

def valid_scan_response(content):
    return pyjq.first('.data.createScan.scan', content)
