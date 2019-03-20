## Automation and AppSec Test Orchestration with ThreatPlaybook

Previously, ThreatPlaybook used to run as a Robot Framework Library that would only allow users to automate and orchestrate AppSec Testing with Robot Framework libraries like: 
* RoboZap
* RoboBurp2
* RoboNpmAudit
etc

However, with its new GraphQL service, you have the option of using Robot Framework Libraries or your own Test Orchestration Framework with ThreatPlaybook

If you are using your own Test Orchestration Tooling, all you have to do is post Vulnerability entries to the create Vulnerabilities Mutation in ThreatPlaybook and you are off to the races

### Automating with Robot Framework
Please refer to this Github Repo to run the example automation
Please watch this video to understand how you can use the automation

### Automating without Robot Framework
ThreatPlaybook allows you to automate without the Robot Framework also. ThreatPlaybook provides generic vulnerability data structures that allows you to push vulnerabilities from a CI/CD process directly into ThreatPlaybook over its GraphQL endpoint. You'll have to follow the following workflow to perform this operation

1. Login to ThreatPlaybook
2. Create Target if not already created => `createTarget` Mutation

```graphql
mutation {
  createTarget(
    name: "test target"
    project: "test-project"
    url: "https://www.example.com"
  ) {
    target {
      name
    }
  }
}
```
3. Create a new scan object to hold vulnerabilities. A Scan has multiple vulnerabilities for a target. A Target can have multiple scans
```graphql
mutation {
  createScan(target: "test target") {
    scan {
      name
      createdOn
    }
  }
}
```
4. Push vulnerabilities into the Scan with the createVulnerability Mutation. 
    * There are multiple fields in the Vulnerability Object that you can use to push vulnerabilities into
    * 

```graphql
mutation {
  createVulnerability(
    vuln: {
     	name: "Default Admin Access"
      tool: "manual"
      cwe: 521
      description: "Default Admin Credentials"
      project: "test_pro"
      target: "we45"
      scan: "eloquent_haibt-9a20cb09-3305-4eb1-b2ce-a02a71f54e7f"
    }
  ) {
    vulnerability {
      id
      name
    }
  }
}
```
Consider using the Vulnerability Evidence Mutation to push Evidences per vulnerability as well
```graphql
mutation {
  createVulnerabilityEvidence(
    evidence: {
      name: "hello evide"
      url: "www.hello.tld"
      vulnId: "5c5d2f079967cbae31e74eeb"
    }
  ) {
    vulnEvidence {
      name
    }
  }
}
```