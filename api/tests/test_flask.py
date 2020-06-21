import pytest
from tp_api.app import app
import json
import secrets


token = ""
project_name = ""
use_case = ""
abuse_case = ""
threat_scenario = ""
target_name = ""
scan_name = ""
cwe = 89


@pytest.fixture(scope="module")
def client():
    with app.test_client() as c:
        yield c


def test_change_password(client):
    response = client.post(
        "/change-password",
        data=json.dumps(
            {
                "email": "admin@admin.com",
                "old_password": "supersecret",
                "new_password": "supersecret",
                "verify_password": "supersecret",
            }
        ),
        content_type="application/json",
    )
    data = json.loads(response.get_data(as_text=True))

    assert response.status_code == 200
    assert data.get("success")


def test_login(client):
    response = client.post(
        "/login",
        data=json.dumps({"email": "admin@admin.com",
                         "password": "supersecret"}),
        content_type="application/json",
    )
    data = json.loads(response.get_data(as_text=True))
    global token
    token = data.get("data").get("token")

    assert response.status_code == 200
    assert data.get("success")


def test_create_project(client):
    response = client.post(
        "/project/create",
        data=json.dumps(
            {"name": "test-project-{}".format(secrets.token_urlsafe(8))}),
        content_type="application/json",
        headers={"Authorization": token},
    )
    data = json.loads(response.get_data(as_text=True))
    assert response.status_code == 200
    assert data.get("success")
    assert data.get("data").get("name")
    global project_name
    project_name = data.get("data").get("name")


def test_create_feature(client):
    response = client.post(
        "/feature/create",
        data=json.dumps(
            {
                "short_name": "test-feature-{}".format(secrets.token_urlsafe(8)),
                "description": "This is a test description",
                "project": project_name,
            }
        ),
        content_type="application/json",
        headers={"Authorization": token},
    )
    data = json.loads(response.get_data(as_text=True))
    assert response.status_code == 200
    assert data.get("success")
    assert data.get("data").get("short_name")
    global use_case
    use_case = data.get("data").get("short_name")


def test_create_abuser_story(client):
    response = client.post(
        "/abuse-case/create",
        data=json.dumps(
            {
                "short_name": "test-abuser-story-{}".format(secrets.token_urlsafe(8)),
                "description": "This is a test description",
                "feature": use_case,
            }
        ),
        content_type="application/json",
        headers={"Authorization": token},
    )
    data = json.loads(response.get_data(as_text=True))
    assert response.status_code == 200
    assert data.get("success")
    assert data.get("data").get("short_name")
    global abuse_case
    abuse_case = data.get("data").get("short_name")


def test_create_threat_scenario_repo(client):
    response = client.post(
        "/scenario/repo/create",
        data=json.dumps(
            {
                "name": "threat-scenario-{}".format(secrets.token_urlsafe(8)),
                "description": "This is a test description",
                "feature": use_case,
                "abuser_story": abuse_case,
                "vul_name": "SQL Injection",
                "type": "repo",
                "repo_name": "sql_injection"
            }
        ),
        content_type="application/json",
        headers={"Authorization": token},
    )
    data = json.loads(response.get_data(as_text=True))
    assert response.status_code == 200
    assert data.get("success")
    assert data.get("data").get("name")


def test_create_threat_scenario(client):
    response = client.post(
        "/scenario/create",
        data=json.dumps(
            {
                "name": "threat-scenario-{}".format(secrets.token_urlsafe(8)),
                "description": "This is a test description",
                "feature": use_case,
                "abuser_story": abuse_case,
                "vul_name": "SQL Injection",
                "type": "inline"
            }
        ),
        content_type="application/json",
        headers={"Authorization": token},
    )
    data = json.loads(response.get_data(as_text=True))
    assert response.status_code == 200
    assert data.get("success")
    assert data.get("data").get("name")
    global threat_scenario
    threat_scenario = data.get("data").get("name")


def test_create_test_case(client):
    response = client.post(
        "/test/create",
        data=json.dumps(
            {
                "name": "test-case-{}".format(secrets.token_urlsafe(8)),
                "test_case": "some test case",
                "threat_scenario": threat_scenario,
            }
        ),
        content_type="application/json",
        headers={"Authorization": token},
    )
    data = json.loads(response.get_data(as_text=True))
    assert response.status_code == 200
    assert data.get("success")
    assert data.get("data").get("name")


def test_create_target(client):
    response = client.post(
        "/target/create",
        data=json.dumps(
            {
                "name": "test-target-{}".format(secrets.token_urlsafe(8)),
                "url": "http://example.com",
                "project": project_name,
            }
        ),
        content_type="application/json",
        headers={"Authorization": token},
    )
    data = json.loads(response.get_data(as_text=True))
    assert response.status_code == 200
    assert data.get("success")
    assert data.get("data").get("name")
    global target_name
    target_name = data.get('data').get('name')


def test_create_scan(client):
    response = client.post(
        "/scan/create",
        data=json.dumps(
            {
                "tool": "ZAP",
                "target": target_name,
                "scan_type": "DAST"
            }
        ),
        content_type="application/json",
        headers={"Authorization": token},
    )
    data = json.loads(response.get_data(as_text=True))
    assert response.status_code == 200
    assert data.get("success")
    assert data.get("data").get("name")
    global scan_name
    scan_name = data.get('data').get('name')


def test_create_vulnerability(client):
    response = client.post(
        "/vulnerability/create",
        data=json.dumps(
            {
                "name": "SQL Injection",
                "scan": scan_name,
                "vul_name": "SQL Injection",
                "cwe": 89,
                "severity": 3,
                "description": "Test Description",
                "evidences": [
                    {
                        "log": "test log",
                        "url": "attack.php",
                        "param": "vulnId",
                        "info": "Found this param by Vulnerability Scanning"
                    }
                ]
            }
        ),
        content_type="application/json",
        headers={"Authorization": token},
    )
    data = json.loads(response.get_data(as_text=True))
    assert response.status_code == 200
    assert data.get("success")
    assert data.get("data").get("name")


def test_get_project(client):
    response = client.get("/project/read", headers={"Authorization": token})
    data = json.loads(response.get_data(as_text=True))
    assert response.status_code == 200
    assert data.get("success")


def test_get_project_specific(client):
    response = client.post(
        "/project/read",
        data=json.dumps(
            {"name": project_name}
        ),
        content_type="application/json",
        headers={"Authorization": token},
    )
    data = json.loads(response.get_data(as_text=True))
    assert response.status_code == 200
    assert data.get("success")


def test_get_feature_by_project(client):
    response = client.post(
        "/feature/read",
        data=json.dumps(
            {"project": project_name}
        ),
        content_type="application/json",
        headers={"Authorization": token},
    )
    data = json.loads(response.get_data(as_text=True))
    assert response.status_code == 200
    assert data.get("success")


def test_get_abuse_case_specific(client):
    response = client.post(
        "/abuses/read",
        data=json.dumps(
            {"user_story": use_case}
        ),
        content_type="application/json",
        headers={"Authorization": token},
    )
    data = json.loads(response.get_data(as_text=True))
    assert response.status_code == 200
    assert data.get("success")


def test_get_threat_scenario(client):
    response = client.post(
        "/scenarios/read",
        data=json.dumps(
            {"abuser_story": abuse_case}
        ),
        content_type="application/json",
        headers={"Authorization": token},
    )
    data = json.loads(response.get_data(as_text=True))
    assert response.status_code == 200
    assert data.get("success")


def test_get_test_case(client):
    response = client.post(
        "/test/read",
        data=json.dumps(
            {"scenario": threat_scenario}
        ),
        content_type="application/json",
        headers={"Authorization": token},
    )
    data = json.loads(response.get_data(as_text=True))
    assert response.status_code == 200
    assert data.get("success")


def test_threat_scenario_severity(client):
    response = client.get("/scenario/severity",
                          headers={"Authorization": token})
    data = json.loads(response.get_data(as_text=True))
    assert response.status_code == 200
    assert data.get("success")


def test_vulnerability_severity(client):
    response = client.get("/vulnerability/severity",
                          headers={"Authorization": token})
    data = json.loads(response.get_data(as_text=True))
    assert response.status_code == 200
    assert data.get("success")


def test_get_scan(client):
    response = client.get("/scan/read",
                          headers={"Authorization": token})
    data = json.loads(response.get_data(as_text=True))
    assert response.status_code == 200
    assert data.get("success")


def test_get_threat_scenario_by_project(client):
    response = client.post(
        "/scenarios/project",
        data=json.dumps(
            {"project": project_name}
        ),
        content_type="application/json",
        headers={"Authorization": token})
    data = json.loads(response.get_data(as_text=True))
    assert response.status_code == 200
    assert data.get("success")


def test_get_vulnerability(client):
    response = client.get(
        "/vulnerability/read",
        headers={"Authorization": token})
    data = json.loads(response.get_data(as_text=True))
    assert response.status_code == 200
    assert data.get("success")


def test_get_vulnerability_by_project(client):
    response = client.post(
        "/vulnerability/project",
        data=json.dumps(
            {"project": project_name}
        ),
        content_type="application/json",
        headers={"Authorization": token})
    data = json.loads(response.get_data(as_text=True))
    assert response.status_code == 200
    assert data.get("success")


def test_get_scan_by_project(client):
    response = client.post(
        "/scan/project",
        data=json.dumps(
            {"project": project_name}
        ),
        content_type="application/json",
        headers={"Authorization": token})
    data = json.loads(response.get_data(as_text=True))
    assert response.status_code == 200
    assert data.get("success")


def test_get_user_story_tree_by_project(client):
    response = client.post(
        "/user-story/project",
        data=json.dumps(
            {"project": project_name}
        ),
        content_type="application/json",
        headers={"Authorization": token})
    data = json.loads(response.get_data(as_text=True))
    assert response.status_code == 200
    assert data.get("success")


def test_get_abuser_story_tree_by_project(client):
    response = client.post(
        "/abuser-story/project",
        data=json.dumps(
            {"project": project_name}
        ),
        content_type="application/json",
        headers={"Authorization": token})
    data = json.loads(response.get_data(as_text=True))
    assert response.status_code == 200
    assert data.get("success")


def test_get_threat_scenario_tree_by_project(client):
    response = client.post(
        "/threat-scenario/project",
        data=json.dumps(
            {"project": project_name}
        ),
        content_type="application/json",
        headers={"Authorization": token})
    data = json.loads(response.get_data(as_text=True))
    assert response.status_code == 200
    assert data.get("success")


def test_get_threatmap_by_project(client):
    response = client.post(
        "/threatmap/project",
        data=json.dumps(
            {"project": project_name}
        ),
        content_type="application/json",
        headers={"Authorization": token})
    data = json.loads(response.get_data(as_text=True))
    assert response.status_code == 200
    assert data.get("success")


def test_get_individual_scan_vuls(client):
    response = client.post(
        "/scan-vuls/project",
        data=json.dumps(
            {"name": scan_name}
        ),
        content_type="application/json",
        headers={"Authorization": token})
    data = json.loads(response.get_data(as_text=True))
    assert response.status_code == 200
    assert data.get("success")


def test_get_asvs_vuls(client):
    response = client.post(
        "/asvs",
        data=json.dumps(
            {"cwe": cwe}
        ),
        content_type="application/json",
        headers={"Authorization": token})
    data = json.loads(response.get_data(as_text=True))
    assert response.status_code == 200
    assert data.get("success")
