# ThreatPlaybook API (GraphQL) Usage

All CRUD calls in ThreatPlaybook require you to be authenticated and authorized. While there's no granular RBAC (yet), each GraphQL request will require you to be authenticated and transmit a JWT in the HTTP `Authorization` header.

## Data Objects and Structure
Please refer to `models.py` in the API code for a more detailed view. However, at a high-level, these are the data objects

```
Project (ThreatPlaybook can have multiple projects. Think of these as apps)
    Feature/UserStory/UseCase (the feature that you are threat modeling)
        Abuser Story/Abuse Case (high level abuse possibilities for the feature/user story)
            Threat Scenario (technical threat scenario for the abuser story)
                Test Case (Security Test Case(s) to test for the Threat Scenario)
                Mitigations (Security Controls for Threat Scenario)
    
    Target (A host/application that will be tested to identify security flaws)
        Scan (A container to house Vulnerabilities identified by a particular tool)
            Vulnerability (Weakness identified by a tool/manual process in an application)
                Vulnerability Evidence (Evidence from tool/manual process for vulnerability)

```

## GraphQL Queries and Expected Response
### Create Project

```
mutation {
  createProject(name: "test project") {
    project {
      name
    }
  }
}
```

* Creates Project with the name `test project`

### Get all Projects

```
query {
  projects {
    id
    name
  }
}
```

### Create User Story/Feature/UseCase

```
mutation {
  createOrUpdateUserStory(
    description: "This is a Feature Description"
    shortName: "feature short"
    project: "test project"
  ) {
    userStory {
      shortName
      description
    }
  }
}
```
* This operation is in `createOrUpdate` mode. Therefore, if you need to update it, you use the same query. If it finds an existing object with the same `shortName`, it updates it
* Project reference must be provided by project name and NOT ID

### Fetch all User Stories

```
query {
  userStories {
    shortName
    description
  }
}
```
* This query can be further cascaded to fetch all child objects as well

### Create Abuser Story

```
mutation {
  createOrUpdateAbuserStory(
    description: "This is an Abuse Case"
    shortName: "abuse case short"
    userStory: "feature short"
    project: "test project"
  ) {
    abuserStory {
      shortName
      description
    }
  }
}
```
* References to `userStory` and `project` are by name and NOT ID
* Works on the create-or-update mode, same as with user stories

### Get all Abuser Stories

```
query {
  abuserStories {
    shortName
    description
  }
}
```

### Create Threat Scenario
* This is a complex query with some mandatory and optional fields
* Mandatory Fields: 
    * Name
    * vulName
    * description
* Other fields are useful to have
* If you are using the cli and using the repo, then you can skip adding many of these fields

```

mutation {
  createOrUpdateThreatModel(
    tModel: {
      name: "PII with SQL Injection"
      vulName: "SQL Injection"
      description: "Someone can steal PII with SQL Injection"
      cwe: 89
      severity: 3
    }
  ) {
    threatModel {
      name
      cwe
      severity
      vulName
    }
  }
}

```
* Works on create-or-update mode
* Consider including non mandatory fields for better coverage