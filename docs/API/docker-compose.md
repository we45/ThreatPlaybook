## Docker Compose Instructions

To deploy ThreatPlaybook's API painlessly over Docker, we have provided for a Docker-Compose file. 

Here are the instructions (code comments) on the options and how you should be using it

```yaml
version: '3'
services:
  nginx:
    image: nginx:latest
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/conf.d/app.conf
    depends_on:
      - api
      - frontend
    links:
      - api
      - frontend
  mongo_db:
    image: bitnami/mongodb:latest
    user: root
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
  api:
    image: we45/threatplaybook-api:latest
    expose:
      - "5042"
    environment:
      - MONGO_HOST=mongo_db
      - MONGO_USER=threatplaybook
      - MONGO_PASS=password123
      - MONGO_PORT=27017
      - MONGO_DB=threat_playbook
      - SUPERUSER_EMAIL=admin@admin.com
      - SUPERUSER_PASS=supersecret
      - JWT_PASS=VGCxqDnhsN6vNQVqmXtrNVVe1AS36ZMQKTq6lYpj0ygHiuWunMOkFi2j17cHSbG-WId9x_yJpeSqy0TTFjs06Q
    links:
      - mongo_db
    depends_on:
      - mongo_db
    command: sh -c "./wait-for mongo_db:27017 -- /usr/local/bin/python3.6 /threatplaybook/app.py"
  frontend:
    image: we45/threatplaybook-frontend:4.0
    expose:
      - "8080"
    environment:
      - API_URL=http://api:5042
    links:
      - api
    depends_on:
      - api
```