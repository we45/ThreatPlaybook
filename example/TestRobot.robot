*** Settings ***
Library  /Users/abhaybhargav/Documents/Code/Python/ThreatPlaybook/threat_playbook/ThreatPlaybook.py  Cut The Funds
Library  Collections
Library  RoboZap  http://127.0.0.1:8090/  8090
Library  RoboNmap
Library  RoboWFuzz  /Users/abhaybhargav/Documents/Code/Python/RoboWFuzz/lists/directory-list-1.0.txt
Library  RequestsLibrary

*** Variables ***
${TARGET_NAME}  CRM_Application
${TARGET_URI}  localhost:5050
${TARGET_HOST}  localhost
#CONFIG
${RESULTS_PATH}  /Users/abhaybhargav/Documents/Code/Python/ThreatPlaybook/example/results

#WFUZZ
${WFUZZ_FILE}  directory_brute.txt

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
#Manage Entities
#    load entity file
#    find or create entities
#    find or connect entities
#
#load_test_cases
#    process test cases
#
#generate threat models
#    find or load cases from directory  link_tests=True
#
#Create Targets
#    find or create target  ${TARGET_NAME}  ${TARGET_URI}
#
#
#Port Scan and Service Enumeration
#    nmap default scan  ${TARGET_HOST}  file_export=${RESULTS_PATH}/flask.txt
#    nmap print results
#    create and link recon  nmap  ${TARGET_NAME}  tags=nmap,
#
##Bruteforcing Directories
##    [Timeout]  15 seconds
##    brute_directories  http://${TARGET_URI}/FUZZ  concur=3  file_name=${RESULTS_PATH}/${WFUZZ_FILE}
##    create and link recon  wfuzz  ${TARGET_NAME}  file_name=${RESULTS_PATH}/${WFUZZ_FILE}  tags=wfuzz,
##
#Initialize ZAP
#    [Tags]  zap_init
#    start gui zap  ${ZAP_PATH}
#    sleep  10
#    zap open url  http://${TARGET_URI}
#
#WebService Walk Operations
#    Authenticate to Web Service ZAP
#    Get Customer by ID
#    Post Customer By ID
#    Search Customer by Username
#
#ZAP Contextualize
#    [Tags]  zap_context
#    ${contextid}=  zap define context  ${CONTEXT}  http://${TARGET_URI}
#    set suite variable  ${CONTEXT_ID}  ${contextid}
#
#ZAP Active Scan
#    [Tags]  zap_scan
#    ${scan_id}=  zap start ascan  ${CONTEXT_ID}  http://${TARGET_URI}  ${SCANPOLICY}
#    set suite variable  ${SCAN_ID}  ${scan_id}
#    zap scan status  ${scan_id}
#
#ZAP Generate Report
#    [Tags]  zap_generate_report
#    zap export report  ${RESULTS_PATH}/${ZAP_REPORT_FILE}  ${REPORT_FORMAT}  ${REPORT_TITLE}  ${REPORT_AUTHOR}
#
#ZAP Die
#    [Tags]  zap_kill
#    zap shutdown
#    sleep  3

Write ZAP Results to DB
    parse zap json  ${RESULTS_PATH}/${ZAP_REPORT_FILE}  ${TARGET_NAME}
    write markdown report


*** Keywords ***
Authenticate to Web Service ZAP
    [Tags]  authenticate_web_service
    ${proxies}=  create dictionary  http=http://127.0.0.1:8090  https=http://127.0.0.1:8090
    ${def_headers}=  create dictionary  Content-Type=application/json
    ${auth_data}=  create dictionary  username=admin  password=admin123
    create session  flask_api  http://${TARGET_URI}  proxies=${proxies}
    ${resp}=  post request  flask_api  login  headers=${def_headers}  data=${auth_data}
    should be equal as strings  ${resp.status_code}  200
    set suite variable  ${AUTH_TOKEN}  ${resp.headers['Authorization']}
    set to dictionary  ${def_headers}  Authorization=${AUTH_TOKEN}
    set suite variable  ${AUTH_HEADERS}  ${def_headers}

Get Customer By ID
    [Tags]  get_customer_by_id
    ${resp}=  get request  flask_api  get/2  headers=${AUTH_HEADERS}
    should be equal as strings  ${resp.status_code}  200

Post Customer By ID
    [Tags]  post_customer_by_id
    ${post_cust_id}=  create dictionary  id=3
    ${resp}=  post request  flask_api  fetch/customer  headers=${AUTH_HEADERS}  data=${post_cust_id}
    should be equal as strings  ${resp.status_code}  200


Search Customer by Username
    [Tags]  search_customer_by_username
    ${post_cust_search}=  create dictionary  search=dleon
    ${resp}=  post request  flask_api  search  headers=${AUTH_HEADERS}  data=${post_cust_search}
    should be equal as strings  ${resp.status_code}  200