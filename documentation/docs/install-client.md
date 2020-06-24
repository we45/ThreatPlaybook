---
id: client-install
title: Install Client
sidebar_label: Install Client
---

##### Mac

```
wget -O playbook https://github.com/we45/ThreatPlaybook-ClientV3/raw/master/dist/playbook_darwin64 && chmod +x playbook && mv playbook /usr/local/bin
```

##### Linux

```
wget -O https://github.com/we45/ThreatPlaybook-ClientV3/raw/master/dist/playbook_linux64 playbook && chmod +x playbook && mv playbook /usr/bin
```

##### Windows

```
https://github.com/we45/ThreatPlaybook-ClientV3/raw/master/dist/playbook_windows64.exe
```

> Please note that the CLI hasn't been tested on Windows OS 



#### Verify the cli installation

```
playbook -h
```
