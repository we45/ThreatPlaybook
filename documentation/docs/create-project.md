---
id: create-project
title: Create Project
sidebar_label: Create Project
---

```
playbook apply project -n test-project
```
>**Note:** `test-project` is the name of the project.

### Create a single Feature with Threat Model

* Now you'll be loading a story-driven threat model. It starts with the Feature/User-Story. 
* Each Feature/UserStory can have multiple Abuser Stories. 
* Each Abuser Story can have multiple Threat Scenarios
* Each Threat Scenario can have multiple Test Cases and Mitigations


#### Download example feature
```
wget -O feature.yaml https://raw.githubusercontent.com/we45/ThreatPlaybook-ClientV3/master/create-upload.yaml
```

#### Upload the features into `test-project`
```
playbook apply feature -f feature.yaml -p test-project
```

And that's it! You've created your first every Threat Model in ThreatPlaybook.

##### Of course, this is not all that ThreatPlaybook has to offer. It has: 
* A useful WebUI for viewing the Features/UserStories -> Abuser Stories -> Threat Models, Scans and more
* Features for processing and managing Vulnerability Results









