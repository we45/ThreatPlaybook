import pytest
import api.app as service
from api.models import *

token = None


@pytest.fixture
def api():
    # print("Starting tests")
    return service.api


@pytest.fixture(scope='module')
def setup():
    # User.drop_collection()
    # Project.drop_collection()
    # UseCase.drop_collection()
    # AbuseCase.drop_collection()
    yield
    User.drop_collection()
    Project.drop_collection()
    UseCase.drop_collection()
    AbuseCase.drop_collection()
    ThreatModel.drop_collection()
    print("deleted collections")


def test_change_password(api, setup):
    r = api.requests.post("/change-password", json={"email": "abhay@we45.com",
                                                    "old_password": "pl@yb00k1234",
                                                    "new_password": "hegemony86",
                                                    "verify_password": "hegemony86"})
    assert 'success' in r.json()


def test_login(api, setup):
    r = api.requests.post("/login", json={"email": "abhay@we45.com", "password": "hegemony86"})
    assert 'token' in r.json()
    global token
    token = r.json()['token']


def test_create_project(api, setup):
    data = """
        mutation {
          createProject(name: "test project") {
            project {
              name
            }
          }
        }
    """
    r = api.requests.post("/graph", json={"query": data}, headers={"Authorization": token})
    assert 'data' in r.json()
    assert 'createProject' in r.json()['data']

def test_create_dummy_project(api, setup):
    data = """
        mutation {
          createProject(name: "test project 2") {
            project {
              name
            }
          }
        }
    """
    r = api.requests.post("/graph", json={"query": data}, headers={"Authorization": token})
    assert 'data' in r.json()
    assert 'createProject' in r.json()['data']

def test_create_user_story(api, setup):
    data = """
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
    """
    r = api.requests.post("/graph", json={"query": data}, headers={"Authorization": token})
    assert 'data' in r.json()
    assert 'createOrUpdateUserStory' in r.json()['data']
    assert 'userStory' in r.json()['data']['createOrUpdateUserStory']
    assert 'shortName' in r.json()['data']['createOrUpdateUserStory']['userStory']
    assert r.json()['data']['createOrUpdateUserStory']['userStory']['shortName'] == "new feature"

def test_create_dummy_user_story(api, setup):
    data = """
    mutation {
      createOrUpdateUserStory(userstory: {
        description: "New Feature Description"
        shortName: "new feature2"
        project: "test project 2"
        partOf: "core_webservice"
      }) {
        userStory {
          shortName
        }
      }
    }
    """
    r = api.requests.post("/graph", json={"query": data}, headers={"Authorization": token})
    assert 'data' in r.json()
    assert 'createOrUpdateUserStory' in r.json()['data']
    assert 'userStory' in r.json()['data']['createOrUpdateUserStory']
    assert 'shortName' in r.json()['data']['createOrUpdateUserStory']['userStory']
    assert r.json()['data']['createOrUpdateUserStory']['userStory']['shortName'] == "new feature2"


def test_update_user_story(api, setup):
    data = """
    mutation {
      createOrUpdateUserStory(userstory: {
        description: "New Feature Description 123"
        shortName: "new feature"
        project: "test project"
        partOf: "core_webservice"
      }) {
        userStory {
          shortName
        }
      }
    }
    """
    r = api.requests.post("/graph", json={"query": data}, headers={"Authorization": token})
    assert 'data' in r.json()
    assert 'createOrUpdateUserStory' in r.json()['data']
    assert 'userStory' in r.json()['data']['createOrUpdateUserStory']
    # assert 'shortName' in r.json()['data']['createOrUpdateUserStory']['userStory']
    # assert r.json()['data']['createOrUpdateUserStory']['userStory']['shortName'] == "new feature"


def test_create_abuser_story(api, setup):
    data = """
    mutation {
      createOrUpdateAbuserStory(
        description: "Compromise Admin credentials"
        shortName: "admin cred compromise"
        userStory: "new feature"
        project: "test project"
      ) {
        abuserStory {
          shortName
          description
        }
      }
    }
    """
    r = api.requests.post("/graph", json={"query": data}, headers={"Authorization": token})
    assert 'data' in r.json()
    assert 'createOrUpdateAbuserStory' in r.json()['data']
    assert 'abuserStory' in r.json()['data']['createOrUpdateAbuserStory']
    assert 'shortName' in r.json()['data']['createOrUpdateAbuserStory']['abuserStory']
    assert r.json()['data']['createOrUpdateAbuserStory']['abuserStory']['shortName'] == "admin cred compromise"


def test_update_abuser_story(api, setup):
    data = """
    mutation {
      createOrUpdateAbuserStory(
        description: "Compromise Admin credentials 1234"
        shortName: "admin cred compromise"
        userStory: "new feature"
        project: "test project"
      ) {
        abuserStory {
          shortName
          description
        }
      }
    }
    """
    r = api.requests.post("/graph", json={"query": data}, headers={"Authorization": token})
    print(r.json())
    assert 'data' in r.json()
    assert 'createOrUpdateAbuserStory' in r.json()['data']
    assert 'abuserStory' in r.json()['data']['createOrUpdateAbuserStory']
    # assert 'shortName' in r.json()['data']['createOrUpdateAbuserStory']['abuserStory']
    # assert r.json()['data']['createOrUpdateAbuserStory']['abuserStory']['shortName'] == "admin cred compromise"


def test_create_threat_scenario(api, setup):
    data = """
    mutation {
      createOrUpdateThreatModel(
        tModel: {
          name: "default admin password"
          vulName: "Default Administrative Password"
          description: "Attacker can compromise admin console with admin,admin credentials"
          cwe: 521
          severity: 3
          abuserStories: "admin cred compromise"
          project: "test project"
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
    """
    r = api.requests.post("/graph", json={"query": data}, headers={"Authorization": token})
    assert 'data' in r.json()
    assert 'createOrUpdateThreatModel' in r.json()['data']
    assert 'threatModel' in r.json()['data']['createOrUpdateThreatModel']
    assert 'vulName' in r.json()['data']['createOrUpdateThreatModel']['threatModel']
    assert r.json()['data']['createOrUpdateThreatModel']['threatModel']['vulName'] == "Default Administrative Password"


def test_delete_user_story(api, setup):
    data = """
        mutation {
          deleteUserStory(shortName: "new feature2") {
            ok
          }
        }
        """
    r = api.requests.post("/graph", json={"query": data}, headers={"Authorization": token})
    assert 'data' in r.json()
    assert 'deleteUserStory' in r.json()['data']
    assert r.json()['data']['deleteUserStory']['ok']

def test_delete_abuser_story(api, setup):
    data = """
        mutation {
          deleteAbuserStory(shortName: "admin cred compromise") {
            ok
          }
        }
        """
    r = api.requests.post("/graph", json={"query": data}, headers={"Authorization": token})
    assert 'data' in r.json()
    assert 'deleteAbuserStory' in r.json()['data']
    assert r.json()['data']['deleteAbuserStory']['ok']

def test_delete_threat_scenario(api, setup):
    data = """
        mutation {
          deleteThreatScenario(name: "default admin password") {
            ok
          }
        }
        """
    r = api.requests.post("/graph", json={"query": data}, headers={"Authorization": token})
    assert 'data' in r.json()
    assert 'deleteThreatScenario' in r.json()['data']
    assert r.json()['data']['deleteThreatScenario']['ok']



def test_delete_project(api, setup):
    data = """
        mutation {
          deleteProject(name: "test project 2") {
            ok
          }
        }
        """
    r = api.requests.post("/graph", json={"query": data}, headers={"Authorization": token})
    assert 'data' in r.json()
    assert 'deleteProject' in r.json()['data']
    assert r.json()['data']['deleteProject']['ok']


