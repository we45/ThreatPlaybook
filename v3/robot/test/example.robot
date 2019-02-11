*** Settings ***
Library  ThreatPlaybook  ${PROJECT}  ${TARGET}  ${ThreatPlaybook_API}


*** Variables ***

# ThreatPlaybook

${ThreatPlaybook_API}  http://127.0.0.1:5042
${EMAIL}  email@test.com
${PASSWORD}  Test@1234
${PROJECT}  TestProjects
${TARGET}  TestTargets
${TARGET_URL}  104.236.85.150
${BANDIT_FILE}  scan_reports/bandit.json
${NODEJSSCAN_FILE}  scan_reports/nodejsscan.json
${NPM_AUDIT_FILE}  scan_reports/npm_audit.json
${ZAP_FILE}  scan_reports/zap_wecare.json
${BRAKEMAN_FILE}  scan_reports/brakeman.json

*** Test Cases ***

Create User
   create user  ${EMAIL}  ${PASSWORD}

Login
    login  ${EMAIL}  ${PASSWORD}

Create Project
    create project

Target
    create target  ${TARGET_URL}

Bandit
    manage bandit results  ${BANDIT_FILE}

NodeJsScan
    manage nodejsscan results  ${NODEJSSCAN_FILE}

NpmAudit
    manage npmaudit results  ${NPM_AUDIT_FILE}

ZAP
    manage zap results  ${ZAP_FILE}  ${TARGET_URL}

Brakeman
    manage brakeman results  ${BRAKEMAN_FILE}
