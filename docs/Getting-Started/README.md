# Getting Started with ThreatPlaybook

### Understanding the "Why?"
ThreatPlaybook allows you to do these things: 
* Perform Story-Driven Threat Modeling for multiple applications(projects). You can go right from the Feature --> Abuser Story --> Threat Scenario --> Mitigations and Security Test Cases
* Codify these threat models in YAML files
* Load and Reload them into the system (ThreatPlaybook server) like you would, a Kubernetes Pod
* Finally, ThreatPlaybook has an automation library that allows you to run and integrate various tools. This allows you to: 
    * Run a completely automated Application-Security Automation Pipeline, as we have support for many SAST, DAST and SCA tools. 
    * Combine a view of the world, in which Threat Models can be seen with Vulnerabilities (correlated). Why? you ask: 
        * It finally answers the question - "What is the coverage of your Threat Model?"
        * It helps you understand - "Which Threat Scenarios have actually come to life (in the form of vulnerabilities)?"
* Finally, it allows you to push results (threat models and vulnerabilities/scans) into Orchestron, our powerful Vulnerability Correlation and Management System

Please consider watching my talk from OWASP AppSecUSA 2018 to understand the need and motivation behind this work

[ThreatPlaybook Talk at AppSecUSA](https://www.youtube.com/embed/fT2-JuvK428 ':include :type=iframe')

### Using ThreatPlaybook
[Using ThreatPlaybook](https://fast.wistia.net/embed/playlists/qrp35atjad ':include :type=iframe')

### Setting up the Server
We highly recommend that you use the Docker Compose file given in the repo. Its easier than every other type of deployment. Please check out the [Docker Compose Docs](/API/docker-compose.md) to get an understanding of all the components and the env-vars, etc.

Once you're ready. You can run `docker-compose up`. This will load the stack for you. 

Your server should be running on `http://<IP Address>` unless you've changed the options for this. You'll need to use an addressable IP Address to access the API and Frontend

Once your server is up and running, you'll need to download and run the client. The client is a CLI app that you can `pip install` and get running with

### Setting up the Client and getting it work with the server
* `mkdir <some folder for your project and its files>`
* create virtualenv here. You can use either `pipenv` or standard `virtualenv`. Be advised that you'll need Python 3.6 and above for this
* Run: `pip install ThreatPlaybook-Client` or `pipenv install ThreatPlaybook-Client` if you use `pipenv`
* Now, your allows you to run the `playbook` command to interact with the cli

```bash
$ playbook
Usage:
    playbook init <project_name>
    playbook set project <project_name>
    playbook login
    playbook create [--file=<tm_file>] [--dir=<tm_dir>]
    playbook get feature [--name=<name>] [--json | --table]
    playbook configure
    playbook change-password
    playbook (-h | --help)
    playbook --version
```

* You'll have to first configure the client to talk to the right server

```bash
$ python playbook.py configure
Enter Host Information. Defaults to http://localhost if nothing is entered. eg: http://threat-playbook
Enter port information, port defaults to 5042 if nothing is entered
[+] Successfully set host to: http://localhost and port to: 5042
```

* You'll have to change the default password for your superadmin, which is in the `SUPERUSER_PASS` in your Docker-Compose File

> Please note: You can't do anything without changing the default password. This applies to all users. Not just superusers

```bash
playbook change-password
Email: <whatever's in your SUPERUSER_EMAIL in docker compose file>
Enter old/default password:
Enter new password:
Verify new password:
```

* Now, you can login and start performing actions on ThreatPlaybook's API

```bash
$ playbook login
Please enter your email: someuser@gmail.com
Please enter your password:
[+] Successfully logged in
```

## Let's create a Project. 
If you want to create a new project to start threat modeling and vulnerability assessing, you'll need to initialize a project. 

A `Project` is the `Application` you are threat modeling

> Initializing a project, will automatically set that project in context. All threat models that you load, etc will be tagged to that project. If you want to change project, you'll need to `set project <project_name>` for that

> We recommend using project names with no spaces. While you can still do `"this project name"` if you need, its a pain using it with the client as you'll need to put in double quotes everytime

```bash
python playbook.py init test_project
There's already a project here. Are you sure you want to re-initialize? It will overwrite existing project info Y
[+] Project: test_project successfully created in API
[+] Boilerplate directories `cases` and `robot` generated
```

* As you can see, I had another project loaded previously in my context. However, by initializing project, I will overwrite my project context and set this project in its place. You can always set the project back to another project with the `set project` command. 
* ThreatPlaybook will create boilerplate directories `cases` for your Threat Models and `robot` for your automation

### Set Project
As mentioned 👆this command allows you to change the context based on project. 
Example you have two projects in your ThreatPlaybook API, `acme` and `xyz`. You have written some threat models for ACME, and now you want to write some for `xyz`, all you have to do is run `playbook set project xyz` and it changes the context of the project for you. All work henceforth on your device will be tagged to project `xyz` until you change it

```bash
$ python playbook.py set project someother_project
[+] Project someother_project has been set successfully
```

### Create
The *most* important command in the Client is the `create` command. ThreatPlaybook allows you to load a Threat Model (YAML file) for your `Feature/UseCase/User Story/Whatever else you want to call it` into ThreatPlaybook. 

ThreatPlaybook's Story-Driven Threat Modeling approach allows you to capture: 
* Feature a.k.a UseCase, UserStory
    * Abuse Case a.k.a Abuser Story
        * Threat Scenario (how the abuse case can come to life)
            * Mitigation for the Threat Scenario
            * Test Cases for the Threat Scenario
    * other features that the feature interacts with (data flows), both internal and external
    * `part_of` to capture Trust Boundary. Example, login is part of the core webservice, where as AWS S3 might be an external component


The YAML file looks like this: 
> Please read code comments below carefully

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

* When you are ready with this story-threat model, you need to use the `create` option. 
* you can provide two types of args to the `create` option: 
    1. `--file` where you need to give it a specific `.yaml` file
    2. `--dir` where you can refer to a dir (rel and abs path) and it will try and process all the `.yaml` files in that directory

```bash
python playbook.py create --dir=/Users/abhaybhargav/Documents/Code/Python/ThreatPlaybook/v3/cli/cases/
[+] Created/Updated Feature/UserStory: `login_user`
[+] Added interaction with create_expense
[+] Added interaction with upload_expense
[+] Added interaction with logout
[+] Added interaction with user
[+] Created/Updated Abuser Story: `external_attacker_account_takeover`
[+] Created/Updated Threat Scenario:`sql injection user account access`
	 [+] Created/Updated Test Case:`automated-vulnerability-scanning`
	 [+] Created/Updated Test Case:`manual`
	 [+] Created/Updated Test Case:`exploit`
	 [+] Created/Updated Test Case:`source-composition-scanning`
	 [+] Created/Updated Test Case:`static-analysis`
[+] Created/Updated Threat Scenario:`end user weak password`
	 [+] Created/Updated Test Case:`automated-vulnerability-scanning`
[+] Created/Updated Threat Scenario: `end user default password`
	 [+] Created/Updated Security Test Case:`automated-vulnerability-scanning`
```