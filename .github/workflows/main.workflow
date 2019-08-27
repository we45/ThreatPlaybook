workflow "Build and Publish" {
    on = "push"
    resolves = "Publish"
}

action "Build" {
    uses = "actions/checkout@v1"
    runs = "cd $GITHUB_WORKSPACE/api/ && docker build . --file Dockerfile --tag we45/threatplaybook-api"
}

action "Docker Login" {
    needs = ["Build"]
    uses = "actions/docker/login@master"
    secrets = ["DOCKER_LOGIN_USER", "DOCKER_LOGIN_PASS"]
}

action "Publish" {
  needs = ["Docker Login"]
  uses = "actions/action-builder/docker@master"
  runs = "make"
  args = "publish"
}