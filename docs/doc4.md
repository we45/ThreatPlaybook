---
id: doc4
title: Guide - ThreatPlaybook CLI Reference
---

# ThreatPlaybook Client

> version 3.0.0b1

## Commands
### Install Client
#### Mac
```bash
wget <github-url>/playbook_darwin64 -o playbook && chmod +x playbook && mv playbook /usr/local/bin
```

#### Linux
```bash
wget <github-url>/playbook_linux64 -o playbook && chmod +x playbook && mv playbook /usr/bin
```
#### Windows
> ThreatPlaybook has not been tested on win* OS
* Download the binary exe from github to a path of your choice

### Configure the CLI

```bash
playbook configure --help
```

> This creates a `.cred` file in the current directory with some config parameters

### Change Default Password first

```bash
playbook change-password -e admin@admin.com -u localhost -p 9000 
```
* You might have to replace the email with the one you have setup
* Once you run this command, you will be prompted for a password that you will need to enter to authenticate to ThreatPlaybook

### Login

```bash
playbook login --help
```

* The `configure` command also behaves like a login. This is not required unless your deployment changes or your token is invalid

### Create a Project

> A Project is typically an application that you want to Threat Model. In the case of a micro-service, you may want to use either a single project or multiple projects if they are modeled and managed separately

```bash
playbook apply project -n name-of-project
```
If your project name has whitespace you'll need to use double quotes eg: `"name of project"`

### Create a Story-Driven Threat Model

In ThreatPlaybook, each user-story/feature is captured "as-code" in a single YAML file. 

The YAML file typically has a structure of: 
* Feature/User-Story
    * Abuser-Stories under the Feature/User-Story
        * Threat Scenarios under the Abuser Story
            * Test Cases for the Threat Scenario

```bash
playbook apply feature -f /path/to/feature.yml
```
You should see some success messages if everything has gone well. If you see error messages, it means that a particular object has not been stored in ThreatPlaybook


### Retrieve a Feature

There are two ways to retrieve a feature/user-story:

1. Basic - Just retrieve the `name`, `project` and `description` of the user story as a ascii table or JSON

As ASCII Table 
```bash
playbook get userStory -n create_upload_expense -p my-new-test
+-----------------------+--------------------------------+-------------+
|         NAME          |          DESCRIPTION           |   PROJECT   |
+-----------------------+--------------------------------+-------------+
| create_upload_expense | As a user, I am able to        | my-new-test |
|                       | create and upload expenses     |             |
|                       | within project limit that      |             |
|                       | have been incurred by me       |             |
|                       | for processing/payment by      |             |
|                       | my manager, so I can get       |             |
|                       | reimbursed                     |             |
+-----------------------+--------------------------------+-------------+
```
This can also be fetched in JSON with the following command

```bash
playbook get userStory --name create_upload_expense --project my-new-test --format json
```

You can also do a "cascading" fetch of: 
* Feature/User Story
    * Abuser Stories of User Story
        * Threat Scenarios of Abuser Stories
            * Test Cases of Threat Scenarios

in a single request

```bash
playbook get userStory --name create_upload_expense --project my-new-test --cascade
```

This fetches all the child objects under Feature/User-Story in a single JSON

### Delete Capability

You can delete any of these objects with the CLI: 
* Project (cascading-deletes all the objects below)
* User-Story/Feature (cascading-deletes all the objects below)
* Abuser Story (cascading-deletes all the objects below)
* Threat Scenario (cascading-deletes all the objects below)
* Test Case

When you delete, you'll need to refer to: 
* identify the object-type
* identify the name of the object
* identify the parent of the object (if applicable)

#### Delete Project

```bash
playbook delete -o project -n my-new-test
```
> * The `-o` refers to the `object` of type `project`
> * The `-n` refers to the object `my-new-test` which is of type `project`
> * Since project doesnt have any parent objects, there's no need to refer to a parent object

#### Delete UserStory/Feature

```bash
playbook delete -o feature -n create_upload_exense -p my-new-test
```
> Here, the `-p` refers to the parent object, which is the project named `my-new-test`

#### Delete Abuser Story

```bash
playbook delete -o abuser-story -n "manipulate expense information" -p create_upload_expense
```
> Here, the `-p` refers to the feature/user-story with the name `create_upload_expense`

#### Delete Threat Scenario

```bash
playbook delete -o scenario -n "sql injection change user" -p tag-expense-to-someone-else
```

> Here, the `-p` refers to the abuser story with the name `tag-expense-to-someone-else`

#### Delete Test Case

```bash
playbook delete -o test -n exploit -p "sql injection change user"
```

> Here, the `-p` refers to the threat scenario with the name `sql injection change user`