---
id: doc1
title: Quick Start
sidebar_label: Quick Start
---

This page details a quick-start example for how you can get started with ThreatPlaybook in under a few minutes

## Step 1: Install and Deploy the Server

### Requirements: 
* Docker and Docker-Compose
* ThreatPlaybook Container Images: 
    * API Container Image - Python Flask
    * MongoDB Container Image
    * VueJS Front-end Container Image
    * Traefik Reverse Proxy


### Steps to Deploy

#### Download the install bash script

```bash
wget https://<github-raw-url>/install-playbook-server.sh
```

#### Run the install script

##### Notes
* Initially, the MongoDB volume persists on `/tmp`. We advise that you change it when using it more permanently (or in prod). This can be done in line number X in the install bash script
* You can change the values of the superuser email and password in the bash script when deploying it to a more permanent environment
* Traefik Reverse proxy runs on port 9090, both the API and the Front-end on port 9090

```bash
install-playbook-server.sh
```

#### Check if server has been deployed

You can do this by running `docker ps` and seeing if 4 containers have been launched, pertaining to: 
* traefik web server
* mongodb
* python-flask
* front-end nodejs (vuejs) app

#### Check if you can access the ThreatPlaybook App

Even if you have deployed the app on your local machine (`localhost`), you'll be unable to access the application over the localhost loopback interface. 

> You'll have to use your Addressable IP Address on the browser and API requests to access the app

> Example: http://192.168.1.24:9090/app/login

If you've been able to do all this, it means that your ThreatPlaybook server is up and running. 

## Step 2: Install and deploy the client

### Installing the ThreatPlaybook CLI

#### Mac

```
wget <github-url>/playbook_darwin64 -o playbook && chmod +x playbook && mv playbook /usr/local/bin
```

#### Linux

```
wget <github-url>/playbook_linux64 -o playbook && chmod +x playbook && mv playbook /usr/bin
```

#### Windows
> Please note that the CLI hasn't been tested on WinOS 

Download the `.exe` from this path to the directory of your choice

## Step 3: Setup and Run the Test Project

### Create a Project Directory and configure the CLI

```bash
mkdir -p /your/project/directory
cd /your/project/directory

playbook configure -e <your-email> -u <host-info> -p <port>
```

> Please ensure that you substitute the following: 
>   * `your-email` for your actual email or for the super-admin email from the step 1
>   * `host-info` for your addressable IP Address
>   * `port` for the traefik port, example: 9090

After this, the CLI prompts you for a password, which is the super-admin password that you've setup in Step 1

### Create the test project

```bash
playbook apply project -n test-project
```
> `test-project` is the name of the project, in this case

### Create a single Feature with Threat Model

* Now you'll be loading a story-driven threat model. It starts with the Feature/User-Story. 
    * Each Feature/UserStory can have multiple Abuser Stories. 
        * Each Abuser Story can have multiple Threat Scenarios
            * Each Threat Scenario can have multiple Test Cases and Mitigations

> Please read more on this here

```bash
wget <yamlfilepath> -o feature.yaml

playbook apply feature -f <absolute path to file> -p test-project
```

> You'll need to provide the absolute (full) path to the yaml file. Relative paths wont work

And that's it! You've created your first every Threat Model in ThreatPlaybook.

Of course, this is not all that ThreatPlaybook has to offer. It has: 
* A useful WebUI for viewing the Features/UserStories -> Abuser Stories -> Threat Models, Scans and more
* Features for processing and managing Vulnerability Results