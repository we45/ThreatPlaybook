---
id: tutorial
title: Tutorial - Installation, Configuration and Extension
sidebar_label: Installation and Configuration
---

##### Download docker-compose file
```
git clone https://github.com/we45/ThreatPlaybook.git
```

##### `cd` into the downloaded directory
```
cd ThreatPlaybook
```

The ThreatPlaybook `docker-compose.yml` file has been written to get you up and running quickly. However, its not the best/most ideal configuration for running ThreatPlaybook, especially in prod.

> Its meant only for experimental deployments on user's local machine

### Analyzing the Docker-Compose File

```yml
version: '3'
services:
  nginx:
    image: we45/threatplaybook-nginx:latest
    ports:
        - "80:80"
    depends_on:
        - api
    links:
        - api
  mongo_db:
    image: 'docker.io/bitnami/mongodb:4.2-debian-10'
    volumes:
      - '/tmp/playbook:/bitnami/mongodb'
    environment:
      - MONGODB_USERNAME=threatplaybook
      - MONGODB_PASSWORD=password123
      - MONGODB_DATABASE=threat_playbook
    expose:
      - "27017"
  api:
    image: we45/threatplaybook-server:latest
    expose:
      - "5000"
    environment:
      - MONGO_HOST=mongo_db
      - MONGO_USER=threatplaybook
      - MONGO_PASS=password123
      - MONGO_PORT=27017
      - MONGO_DB=threat_playbook
      - SUPERUSER_EMAIL=admin@admin.com
      - SUPERUSER_PASS=supersecret
      - JWT_PASS=VGCxqDnhsN6vNQVqmXtrNVVe1AS36ZMQKTq6lYpj0ygHiuWunMOkFi2j17cHSbG-WId9x_yJpeSqy0TTFjs06Q
      - WAIT_HOSTS=mongo_db:27017
    links:
      - mongo_db
    depends_on:
      - mongo_db
    command: sh -c "/app/wait-for mongo_db:27017 -- /usr/local/bin/python /app/app.py"
  frontend:
    image: we45/threatplaybook-frontend:latest
    environment:
      - VUE_APP_API_URL=http://api
    links:
      - api
    depends_on:
      - api
```

### Change the Default Password!

* The value set in the `SUPERUSER_EMAIL` and `SUPERUSER_PASS` are the values that ThreatPlaybook uses as the default values for the Superuser Account within ThreatPlaybook.

> This is clearly a default password that you SHOULD NOT use as a permanent password to access the super-admin account on ThreatPlaybook. 
> 
> Please use `playbook change-password` feature in the CLI to change your default password. You have been warned!

### Logs

There's a single output log that is generated in the `/app` directory within the container. If you want the logs to persist on a more permanent file-system, you'll need to volume mount a src path on your machine to the `/app/logs` path within the container. 

```
# inside the container
/app/logs # cat output.log 
2020-06-21 10:41:01.282 | INFO     | __main__:login:158 - User 'admin@admin.com' successfully logged in
2020-06-21 10:41:27.442 | INFO     | __main__:create_project:191 - Successfully created project my-new-test
2020-06-21 10:41:40.753 | INFO     | __main__:create_user_story:236 - Successfully created user-story/feature 'create_upload_expense'
```