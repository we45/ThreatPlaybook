*** Settings ***
Library  /Users/abhaybhargav/Documents/Code/Python/ThreatPlaybook/threat_playbook/ThreatPlaybook.py  Cut The Funds
Library  Collections

*** Variables ***
${TARGET_NAME}  CRM_Application
${TARGET_URI}  localhost:5050
${TARGET_HOST}  localhost
#CONFIG
${RESULTS_PATH}  /Users/abhaybhargav/Documents/Code/Python/ThreatPlaybook/example/results

#WFUZZ
${WFUZZ_FILE}  directory_brute.json

#ZAP
${ZAP_PATH}  /Applications/OWASP_ZAP.app/Contents/Java/
${APPNAME}  Flask API
${CONTEXT}  Flask_API
${REPORT_TITLE}  Flask API Test Report - ZAP
${REPORT_FORMAT}  json
${ZAP_REPORT_FILE}  flask_api.json
${REPORT_AUTHOR}  Abhay Bhargav
${SCANPOLICY}  Light



*** Test Cases ***
Manage Entities
    [Tags]  ThreatModeling
    load entity file  filepath=/Users/abhaybhargav/Documents/Code/Python/ThreatPlaybook/example/entities/new_entities.yml
    find or create entities
    find or connect entities
    generate mermaid diagram

load_test_cases
    process test cases

generate threat models
    find or load cases from directory  link_tests=True