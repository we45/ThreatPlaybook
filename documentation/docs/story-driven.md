---
id: story-driven
title: Story-Driven Threat Modeling with ThreatPlaybook
sidebar_label: Story-Driven Threat Modeling
---

## Objective
In this tutorial, you will learn how you can create a story-driven threat model with ThreatPlaybook

## What is a Story-Driven Threat Model?
### User-Story Driven Threat Modeling
Story-Driven Threat Modeling is different from System-Driven Threat Modeling that we are largely used to. Story-driven threat modeling starts with modeling user-stories (or feature definitions). The primary reasons behind story-driven threat modeling are: 
* **Speed** - Your Threat Models are able to keep pace with the Engineering Team's SDLC rather than a long-drawn system-wide threat model being performed on a periodic basis
* **Focus** - The focus of your threat model in case of a story-driven threat model is the user-story itself. You waste little/no time on analyzing too many tangents
* **Iterative** - Story-driven threat modeling evolves with the story. If the story changes, the threat model might change. It lends itself to more scalability and elasticity

#### User Story/Feature
The User Story is a Description of the Functionality. This concept is very popular in the world of Agile Development, where an Agile Team picks a bunch of user stories to get done in a sprint. It is a Unit of Work to be completed in a sprint. A user story typically looks like this
> As a user (salesperson), I should be able to access my customer's profile to be able to log call information with the customer 

#### Abuser Story
An Abuser Story is an "evil user's version" of a user story. An Abuser Story captures (at a high level) WHAT a threat actor can do to abuse the feature enumerated in the User Story. For example
> As a rival salesperson, I will access other salespeople's customers in the application to poach customers from my colleagues

#### Threat Model/Scenario
A Threat Model/Scenario is a description of HOW a threat actor can bring the abuser story to life. This is a scenario detailing the Attack Vector (primary technique for attack) and approach to bringing the Abuser Story to life. One can use STRIDE as an approach to capture various threats and use DREAD/CVSSv3 to capture impact of said attack. For example: 

> Abuser Story: As a rival salesperson, I will access other salespeople's customers in the application to poach customers from my colleagues
> 
> Threat Models: 
> * Attacker performs SQL Injection, to gain access to the Database of other customers in the System
> * Attacker attempts to perform Insecure Direct Object Reference attacks, by incrementing the customer's ID value, gaining access to another customer's account
> * Attacker steals a rival's session tokens by performing a Man-in-the-Middle Attack
> ....

## Story-Driven Threat Modeling with ThreatPlaybook

### Start by making sure that you have your Server and CLI setup

> Follow Steps 1 and 2 in the Quick Start Guide here

### Let's configure the CLI first

> Currently, the CLI or the REST API are the only ways that data can be loaded into ThreatPlaybook. WebUI is view-only

##### Create a Project Directory
```
mkdir -p /your/project/directory
```

##### `cd` into your project directory
```
cd /your/project/directory
```

##### Configure

```
playbook configure -e <your-email> -u <host-info> -p <port>
```

> Please ensure that you substitute the following: 
>   * `your-email` enter any email address, eample: admin@admin.com
>   * `host-info` for your addressable IP Address, example: 192.168.1.17
>   * `port` for the nginx port, example: 80

After this, the CLI prompts you for a password, which is the super-admin password that you've setup in Step 1

### Let's create a Project

> A Project is typically an application that you want to Threat Model. In the case of a micro-service, you may want to use either a single project or multiple projects if they are modeled and managed separately

```bash
playbook apply project -n test-project
```
> `test-project` is the name of the project, in this case

### Let's create our User-Story/Feature YAML file

In ThreatPlaybook, each user-story/feature is captured "as-code" in a single YAML file. 

The YAML file typically has a structure of: 
* Feature/User-Story
    * Abuser-Stories under the Feature/User-Story
        * Threat Scenarios under the Abuser Story
            * Test Cases for the Threat Scenario

Let's look at a sample user-story/feature yaml

```yaml
objectType: Feature #this is the user story
name: create_upload_expense
description: As a user, I am able to create and upload expenses within project limit that have been incurred by me for processing/payment by my manager, so I can get reimbursed
abuse_cases:
  - name: manipulate expense information #this is an abuser story
    description: As a malicious user, I will manipulate expense management process to get larger or bogus expenses into the system.
    threat_scenarios: # these are the list of threat scenarios for the abuser story
    - name: sql injection expense limit bypass
      type: repo # repo type threat scenario
      description: Perform SQL Injection to compromise the Database, and raise project budget limits or bypass expense controls
      reference: {name: sql_injection, severity: 3}
    - name: upload-malware
      type: inline # inline type threat scenario
      description: I will upload malware as an expense to the system and compromise the application and create a DoS condition
      type: inline
      vul_name: Malicious File Upload
      severity: 3
      cwe: 434
      test-cases:
      - name: manual-pentesting
        test: upload files with reverse-shell and CSV injection payloads and attempt to trigger remote code execution on Project Manager's Computer
        type: exploit
        tools: manual
```

#### Let's examine this YAML file in more detail and some tips

* ThreatPlaybook is name-based, so its important that you name your features/abuser-stories/threat-scenarios uniquely
* Threat Scenarios can either be `repo` type or `inline` type: 
    * **Repo Type**: ThreatPlaybook has a list of canned Vulnerability Definitions already pre-loaded in the system. Of course, you can create your own definitions as well. These form a repository or `repo`. So, when you want to declare a threat scenario is a `repo` type threat scenario, all you have to do is refer to the name of your canned vulnerability, and ThreatPlaybook automatically enumerates the following from the repo: 
        * CWE
        * Mitigations
        * Test cases
        * other metadata fields
    * **Inline type**: When you declare and use inline threat scenarios, you are defining and declaring the threat scenario `inline` with the YAML. In this case, there's no canned vulnerability and you are declaring that vulnerability definition on the fly. Here, you need to declare all these attributes yourself: 
        * name
        * cwe
        * vul_name
        * test-cases
        * severity
        * description
        * test cases

### Push YAML to ThreatPlaybook server

When you're done defining your YAML, all you have to do is to push the Story-driven threat model to the ThreatPlaybook Server. This can be done with: 

```bash
playbook apply feature -f <path to the yaml file> -p test-project
```

> You'll need to provide the absolute (full) path to the yaml file. Relative paths wont work

If everything has worked, you should see a string of success messages of having created objects in ThreatPlaybook