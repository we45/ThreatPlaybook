# Building your Threat Model with ThreatPlaybook
* Please go over the [Getting Started](../Getting-Started/README.md) if you haven't already
* Please go over the [Client Operations Guide](../Client/README.md) to understand how you should use the client

## Building your Threat Model
* The Client typically creates a `cases` directory for you. This is where your threat models go. Alternatively, you can store/reference your threat models in any directory.

ThreatPlaybook allows you to capture "Story-Driven Threat Models" where: 
* You are threat modeling one feature/user-story at a time
* You are doing the above, iteratively

The overall structure of the Story-Driven Threat Modeling Process looks something like this: 
![Process](../img/story-process.png)

The fields and objects you have available to you are as follows (hierarchically): 

* User Story:
    * shortName: Name of your User Story/Feature
    * Description: description of your user story/feature
    * Abuse Cases/Abuser Stories: 
        * shortName: name
        * Description: description
        * Threat Scenario: 
            * name
            * vul_name: Name of the vulnerability identified in the threat scenario
            * type: (repo/inline)
            * description: description
            * severity: (3/2/1/0) 3 for High, 2 for Medium, 1 for Low, 0 for Info
            * cwe: CWE ID for the Vulnerability
            * mitigations: JSON object with mitigations
            * Test Cases:
                * name
                * test: Description of the test case
                * tools: List of tools used to perform test case
                * type: (discovery(dast)/sast/sca/recon/manual/exploit)
    
    * internal_interactions: list of components with which this feature interacts with, internally
    * external_interactions: list of components with which this feature interacts with, externally
    * part_of: component for trust boundary formation 

This is what an example Threat Model (YAML) looks like: 

```yaml
objectType: Feature
# this is a mandatory declaration
name: login_user
# unique name for a feature, mandatory
description: As an employee of the organization, I would like to login to the Expense Management application to submit and upload expense information
# desc is mandatory
abuse_cases:
# list of abuse cases under the feature
    - name: external_attacker_account_takeover #unique name
      description: As an external attacker, I would compromise a single/multiple user accounts to gain access to sensitive corporate information, like expenses #mandatory
      threat_scenarios:
        # list of threat scenarios under each abuse-case
      - name: sql injection user account access #name
        type: repo 
        # template vulnerability where other metadata is pulled from the repository
        # repo vuls will ensure that everything from mitigations and test-cases is pulled into your threat model, directly from the repo instead of you having to create that again
        description: External Attacker may be able to gain access to user accounts by successfully performing SQL Injection Attacks against some of the unauthenticated pages in the application
        reference: {name: sql_injection, severity: 3} # referenced from repo by name

      - name: end user weak password
        type: repo
        description: External attacker compromises a user password, using a weak password
        reference: {name: weak-default-password, severity: 2}

      - name: end user default password
        type: inline #not repo, you'll need to declare meta-data right here
        vul_name: Default Passwords
        description: External attacker may be able to bypass user authentication by compromising default passwords of users
        severity: 2
        cwe: 284 #recommended
        test-cases: #since its inline, you are declaring test-cases. optional, but recommended
        - name: automated-vulnerability-scanning
          test: run automated vulnerability discovery tools and bruteforce against the application
          tools: [zap,burpsuite,arachni,acunetix,netsparker,appspider,w3af]
          type: discovery

      - name: auth token hijacking mitm
        type: repo
        description: Attacker attempts to compromise auth token by gaining access to the end user's auth token by performing Man in the Middle Attacks
        reference: {name: plaintext-transmission, severity: 3}

internal_interactions: # data flows with other internal components
- create_expense: "HTTP GET Request"
#each item is represented as "name of feature: data shared with feature"
- upload_expense: "HTTP GET Request"
- logout: "HTTP GET Request"
external_interactions:
- user: "credentials"
part_of: core_webservice # to denote trust boundary. 
```