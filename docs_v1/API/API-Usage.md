# ThreatPlaybook API (GraphQL) Usage

>> You will NOT need to use raw GraphQL queries for most operations as they have been provided in the Client. Please refer to the Client Documentation. This is just an additional reference

All CRUD calls in ThreatPlaybook require you to be authenticated and authorized. While there's no granular RBAC (yet), each GraphQL request will require you to be authenticated and transmit a JWT in the HTTP `Authorization` header.

We recommend the use of the [Insomnia Client](https://insomnia.rest/) for GraphQL queries.

## Data Objects and Structure
Please refer to `models.py` in the API code for a more detailed view. However, at a high-level, these are the data objects

* Project (ThreatPlaybook can have multiple projects. Think of these as apps)
  * Feature/UserStory/UseCase (the feature that you are threat modeling)
    * Abuser Story/Abuse Case (high level abuse possibilities for the feature/user story)
      * Threat Scenario (technical threat scenario for the abuser story)
        * Test Case (Security Test Case(s) to test for the Threat Scenario)
        * Mitigations (Security Controls for Threat Scenario)
    
  * Target (A host/application that will be tested to identify security flaws)
    * Scan (A container to house Vulnerabilities identified by a particular tool)
      * Vulnerability (Weakness identified by a tool/manual process in an application)
        * Vulnerability Evidence (Evidence from tool/manual process for vulnerability)


## Create Additional Users
* You should have created a super-user by now. Please make sure you do that first.
* You have to login to the API as a super-user to create other users. There's no access restrictions or RBAC for other users

```bash
curl --request POST \
  --url http://localhost:5042/login \
  --header 'content-type: application/json' \
  --data '{
	"email": "someuser@gmail.com",
	"password": "somepass"
}'
```

* Once you login successfully, you get a response with an auth token

```json
{
  "success": "login",
  "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJlbWFpbCI6ImFiaGF5QHdlNDUuY29tIn0.jcLCGiAitouZwZxZendLAL_zGw5c4FIx9ejwoaQWmEE"
}
```
> You'll need to use this token in the Authorization header for all requests

* Now you can create a user (User create is restricted to SuperUser)

```bash
curl --request POST \
  --url http://localhost:5042/create-user \
  --header 'content-type: application/json' \
  --data '{
	"email": "someuser@email.com",
	"password": "threatM0deling1sAwesome"
}'
```

## GraphQL Queries and Expected Response
### Create Project

```graphql
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

```graphql
query {
  projects {
    id
    name
  }
}
```

### Create User Story/Feature/UseCase

```graphql
mutation {
  createOrUpdateUserStory(userstory: {
    description: "New Feature Description"
    shortName: "new feature"
    project: "test project"
    partOf: "core_webservice"
  }) {
    userStory {
      shortName
    }
  }
}
```
* This operation is in `createOrUpdate` mode. Therefore, if you need to update it, you use the same query. If it finds an existing object with the same `shortName`, it updates it
* Project reference must be provided by project name and NOT ID

### Fetch all User Stories

```graphql
query {
  userStories {
    shortName
    description
  }
}
```
* This query can be further cascaded to fetch all child objects as well

### Create Abuser Story

```graphql
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

```graphql
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

```graphql

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