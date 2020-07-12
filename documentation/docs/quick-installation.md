---
id: installation
title: Install Server
sidebar_label: Install Server
---

##### Download docker-compose file
```
git clone https://github.com/we45/ThreatPlaybook.git
```

##### `cd` into the downloaded directory
```
cd ThreatPlaybook
```

> For Linux users, you might have to add another set of permissions for the MongoDB to work correctly. 
> 
> `sudo chown -R 1001 $PWD/playbook`

##### Run the Playbook server
```
docker-compose up -d
```






