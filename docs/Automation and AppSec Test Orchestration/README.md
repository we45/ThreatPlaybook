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