*** Settings ***
Library  Playbot  ${PROJECT}  ${TARGET}  ${ThreatPlaybook_API}


*** Variables ***

# ThreatPlaybook

${ThreatPlaybook_API}  http://127.0.0.1:5042
${EMAIL}  abhay@we45.com
${PASSWORD}  hegemony86
${PROJECT}  test project
${TARGET}  TestTargets
${TEST_PATH}  /Users/abhaybhargav/Documents/Code/Python/ThreatPlaybook/robot/test/scan_reports/
${TARGET_URL}  104.236.85.150
${BANDIT_FILE}  ${TEST_PATH}bandit.json
${NODEJSSCAN_FILE}  ${TEST_PATH}nodejsscan.json
${NPM_AUDIT_FILE}  ${TEST_PATH}npm_audit.json
${ZAP_FILE}  ${TEST_PATH}zap_wecare.json
${BRAKEMAN_FILE}  ${TEST_PATH}brakeman.json

*** Test Cases ***

Login
    login  ${EMAIL}  ${PASSWORD}

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
