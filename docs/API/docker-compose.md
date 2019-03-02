## Docker Compose Instructions

To deploy ThreatPlaybook's API painlessly over Docker, we have provided for a Docker-Compose file. 

Here are the instructions (code comments) on the options and how you should be using it

```yaml
version: '3'
services:
  frontend:
    image: we45/threatplaybook-frontend
    # this is the front-end service, it runs on port 5000
    expose:
      - "5000"
    ports:
      - "5000:5000"
    environment:
      - API_URL=http://192.168.1.24:5042
      # the API_URL needs to be externally referencible by the front-end
    links:
      - api
    depends_on:
      - api
  api:
    image: we45/threatplaybook-api
    expose:
      - "5042"
    ports:
      - "5042:5042"
    environment:
      - MONGO_HOST=mongo_db
      - MONGO_USER=threatplaybook
      - MONGO_PASS=password123
      - MONGO_PORT=27017
      - MONGO_DB=threat_playbook
      - JWT_PASS=VGCxqDnhsN6vNQVqmXtrNVVe1AS36ZMQKTq6lYpj0ygHiuWunMOkFi2j17cHSbG-WId9x_yJpeSqy0TTFjs06Q
      #these options are initialized as env-vars that are used by the server
      # please use a strong JWT Password, as someone can easily bruteforce weak JWT passwords and bypass authentication
    links:
      - mongo_db
    depends_on:
      - mongo_db
  mongo_db:
    image: bitnami/mongodb:latest
    environment:
      - MONGODB_USERNAME=threatplaybook
      - MONGODB_PASSWORD=password123
      - MONGODB_DATABASE=threat_playbook
    expose:
      - "27017"
    ports:
      - "27017:27017"
    volumes:
      - ./threatplaybook_db:/bitnami
```