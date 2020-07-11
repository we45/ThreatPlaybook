from flask import Flask, jsonify, request
import jwt
from secrets import token_urlsafe
from os import getenv
from utils import (
    logger,
    connect_db,
    load_reload_asvs_db,
    load_reload_repo_db,
    initialize_superuser,
    respond,
)
from models import *
import bcrypt
from functools import wraps
import json
from flask_cors import CORS
import uuid
from flasgger import Swagger, swag_from

JWT_PASSWORD = getenv("JWT_PASS", token_urlsafe(16))
items_per_page = 20
db = connect_db()
load_reload_repo_db()
load_reload_asvs_db()
initialize_superuser()


app = Flask(__name__)
swagger = Swagger(app)

CORS(app)


def validate_user(f):
    @wraps(f)
    def inner(*args, **kwargs):
        if "Authorization" not in request.headers and not request.headers.get(
            "Authorization"
        ):
            no_auth = respond(False, True, message="No Authentication data")
            return no_auth, 403
        else:
            try:
                token = request.headers.get("Authorization")
                decoded = jwt.decode(token, JWT_PASSWORD, algorithms=["HS256"])
                ref_user = User.objects.get(email=decoded["email"])
                return f(*args, **kwargs)
            except Exception as e:
                logger.exception(e)
                token_err = respond(False, True, message="Invalid Token or User")
                return token_err, 403

    return inner


# swagger done
@app.route("/api/change-password", methods=["POST"])
@swag_from("swagger/change-password.yml")
def change_password():
    if request.method == "POST":
        pass_data = request.get_json()
        if pass_data:
            if (
                "email" not in pass_data
                and "old_password" not in pass_data
                and "verify_password" not in pass_data
            ):
                return (
                    jsonify(
                        {
                            "success": False,
                            "error": True,
                            "message": "Mandatory values in request unavailable",
                        }
                    ),
                    400,
                )
            else:
                try:
                    ref_user = User.objects.get(email=pass_data["email"])
                except DoesNotExist:
                    return (
                        jsonify(
                            {
                                "success": False,
                                "error": True,
                                "message": "No user found",
                            }
                        ),
                        403,
                    )
                verify_pass = bcrypt.checkpw(
                    pass_data["old_password"].encode(), str(ref_user.password).encode()
                )
                if verify_pass and (
                    pass_data["new_password"] == pass_data["verify_password"]
                ):
                    hash_pass = bcrypt.hashpw(
                        pass_data.get("new_password").encode(), bcrypt.gensalt()
                    ).decode()
                    ref_user.update(password=hash_pass, default_password=False)
                    logger.info(
                        "Changed password for user {}".format(pass_data["email"])
                    )
                    return jsonify(
                        {
                            "success": True,
                            "error": False,
                            "message": "Successfully changed password for user {}".format(
                                pass_data["email"]
                            ),
                        }
                    )
                else:
                    logger.error(
                        "Change password exception. User passwords dont match OR old password is wrong for user {}".format(
                            pass_data["email"]
                        )
                    )
                    return (
                        jsonify(
                            {
                                "success": False,
                                "error": True,
                                "message": "Unable to change password for user {}".format(
                                    pass_data["email"]
                                ),
                            }
                        ),
                        403,
                    )

        else:
            invalid_data = respond(
                False, True, message="Unable to decode request payload"
            )
            return jsonify(invalid_data), 400


# swagger done
@app.route("/api/login", methods=["POST"])
def login():
    if request.method == "POST":
        login_data = request.get_json()
        if "email" not in login_data and "password" not in login_data:
            input_error = respond(False, True, message="Input Validation Error")
            return input_error, 400
        else:
            try:
                ref_user = User.objects.get(email=login_data["email"])
            except DoesNotExist:
                user_not_exists = respond(False, True, message="Invalid credentials")
                return user_not_exists, 403

            verify_pass = bcrypt.checkpw(
                login_data["password"].encode(), str(ref_user.password).encode()
            )
            if verify_pass:
                logger.info("User '{}' successfully logged in".format(ref_user.email))
                token = jwt.encode(
                    {"email": ref_user.email}, key=JWT_PASSWORD, algorithm="HS256"
                ).decode()
                success_message = respond(
                    True, False, message="Logged in successfully", data={"token": token}
                )
                return success_message

            else:
                invalid_credentials = respond(
                    False, True, message="Invalid credentials"
                )
                return invalid_credentials, 403


# swagger done
@app.route("/api/project/create", methods=["POST"])
@validate_user
def create_project():
    data = request.get_json()
    if "name" not in data and not data.get("name"):
        logger.error("Input Validation Error - no 'name' param in request")
        inval_err = respond(False, True, "Mandatory param not in request")
        return inval_err, 400
    else:
        try:
            Project(name=data.get("name")).save()
            success = respond(
                True,
                False,
                message="successfully saved project",
                data={"name": data.get("name")},
            )
            logger.info("Successfully created project {}".format(data.get("name")))
            return success
        except Exception as e:
            logger.exception(e)
            exc = respond(False, True, "unable to save Project to DB")
            return exc, 400


# swagger done
@app.route("/api/feature/create", methods=["POST"])
@validate_user
@swag_from("swagger/feature-create.yml")
def create_user_story():
    data = request.get_json()
    if not set(("short_name", "description", "project")) <= set(data):
        logger.error(
            "Mandatory params 'short_name', 'description', 'project' not in request"
        )
        input_val_err = respond(
            False,
            True,
            message="Mandatory params 'short_name', 'description', 'project' not in request",
        )
        return input_val_err, 400
    else:
        try:
            my_proj = Project.objects.get(name=data.get("project"))
        except DoesNotExist:
            project_not_exists = respond(
                False,
                True,
                message="Project '{}' does not exist".format(data.get("project")),
            )
            return project_not_exists, 404

        short_name = data.get("short_name")
        desc = data.get("description")
        try:
            ref_user_case = UseCase.objects(short_name=short_name).update_one(
                short_name=short_name, description=desc, project=my_proj, upsert=True,
            )
            ref_feature = UseCase.objects.get(short_name=short_name)
            if ref_feature not in my_proj.features:
                my_proj.features.append(ref_feature)
                my_proj.save()
            logger.info(
                "Successfully created user-story/feature '{}'".format(short_name)
            )
            return respond(
                True,
                False,
                message="Successfully created Feature '{}'".format(short_name),
                data={"short_name": short_name},
            )
        except Exception as e:
            logger.exception(e)
            return respond(False, True, message="Unable to create User Story"), 400


# swagger done
@app.route("/api/abuse-case/create", methods=["POST"])
@validate_user
@swag_from("swagger/abuse-create.yml")
def create_abuser_story():
    data = request.get_json()
    if not set(("short_name", "description", "feature")) <= set(data):
        logger.error(
            "Mandatory params 'short_name', 'description', 'feature' not in request"
        )
        input_val_err = respond(
            False,
            True,
            message="Mandatory params 'short_name', 'description', 'feature' not in request",
        )
        return input_val_err, 400
    else:
        try:
            ref_user_story = UseCase.objects.get(short_name=data.get("feature"))
        except DoesNotExist:
            project_not_exists = respond(
                False,
                True,
                message="Feature '{}' does not exist".format(data.get("feature")),
            )
            return project_not_exists, 404

        short_name = data.get("short_name")
        desc = data.get("description")
        try:
            ref_user_case = AbuseCase.objects(short_name=short_name).update_one(
                short_name=short_name,
                description=desc,
                use_case=ref_user_story,
                upsert=True,
            )
            ref_abuse = AbuseCase.objects.get(short_name=short_name)
            if ref_abuse not in ref_user_story.abuses:
                ref_user_story.abuses.append(ref_abuse)
                ref_user_story.save()
            logger.info("Successfully created abuser-story '{}'".format(short_name))
            return respond(
                True,
                False,
                message="Successfully created Abuser Story '{}'".format(short_name),
                data={"short_name": short_name},
            )
        except Exception as e:
            logger.exception(e)
            return respond(False, True, message="Unable to create Abuser Story"), 400


# swagger done
@app.route("/api/scenario/repo/create", methods=["POST"])
@validate_user
@swag_from("swagger/scenario-repo.yml")
def create_repo_scenario():
    data = request.get_json()
    try:
        ref_user_story = UseCase.objects.get(short_name=data.get("feature"))
    except DoesNotExist:
        return (
            respond(False, True, message="Unable to find reference User Story"),
            400,
        )

    try:
        ref_abuser_story = AbuseCase.objects.get(short_name=data.get("abuser_story"))
    except DoesNotExist:
        return (
            respond(False, True, message="Unable to find reference Abuser Story"),
            400,
        )
    tm_name = data.get("name")
    description = data.get("description")
    if not data.get("type") == "repo" and data.get("repo_name"):
        return respond(False, True, message="Input Validation Error"), 400
    else:
        repo_name = data.get("repo_name")
        severity = data.get("severity", 1)
        try:
            ref_repo = Repo.objects.get(short_name=repo_name)
        except Exception:
            return respond(False, True, message="repo not found"), 404
        try:
            ThreatModel.objects(name=tm_name).update_one(
                name=tm_name,
                cwe=ref_repo.cwe,
                vul_name=ref_repo.name,
                description=description,
                use_case=ref_user_story,
                abuse_case=ref_abuser_story,
                mitigations=ref_repo.mitigations,
                categories=ref_repo.categories,
                severity=severity,
                upsert=True,
            )
            ref_scenario = ThreatModel.objects.get(name=tm_name)
            if ref_scenario not in ref_abuser_story.scenarios:
                ref_abuser_story.scenarios.append(ref_scenario)
                ref_abuser_story.save()
        except Exception as e:
            logger.exception(e)
            return (
                respond(
                    False,
                    True,
                    message="Unable to store Threat Scenario: {}".format(tm_name),
                ),
                500,
            )

        if ref_repo.tests:
            for single_test in ref_repo.tests:
                try:
                    Test.objects(name=single_test.name).update_one(
                        name=single_test.name,
                        test_case=single_test.test_case,
                        executed=False,
                        scenario=ref_scenario,
                        tools=single_test.tools,
                        upsert=True,
                    )
                    ref_my_test = Test.objects.get(
                        name=single_test.name, scenario=ref_scenario
                    )
                    if ref_my_test not in ref_scenario.tests:
                        ref_scenario.tests.append(ref_my_test)
                        ref_scenario.save()
                except Exception as e:
                    logger.exception(e)
                    pass

        return respond(
            True,
            False,
            message="Successfully created Threat Scenario",
            data={"name": tm_name},
        )


# swagger done
@app.route("/api/scenario/create", methods=["POST"])
@validate_user
@swag_from("swagger/scenario-inline.yml")
def create_threat_scenario():
    data = request.get_json()
    mandatory_params = (
        "vul_name",
        "name",
        "description",
        "feature",
        "abuser_story",
        "type",
    )
    if not set(mandatory_params) <= set(data):
        return (
            respond(
                False,
                True,
                message="Input validation error",
                data={"mandatory_params": list(mandatory_params)},
            ),
            400,
        )
    else:
        try:
            ref_user_story = UseCase.objects.get(short_name=data.get("feature"))
        except DoesNotExist:
            return (
                respond(False, True, message="Unable to find reference User Story"),
                400,
            )

        try:
            ref_abuser_story = AbuseCase.objects.get(
                short_name=data.get("abuser_story")
            )
        except DoesNotExist:
            return (
                respond(False, True, message="Unable to find reference Abuser Story"),
                400,
            )
        try:
            tm_name = data.get("name")
            description = data.get("description")
            cwe_val = data.get("cwe", 0)
            mitigations = data.get("mitigations", [])
            severity = int(data.get("severity", 1))
            vul_name = data.get("vul_name")
            ThreatModel.objects(name=tm_name).update_one(
                name=tm_name,
                vul_name=vul_name,
                cwe=cwe_val,
                severity=severity,
                mitigations=mitigations,
                description=description,
                use_case=ref_user_story,
                abuse_case=ref_abuser_story,
                upsert=True,
            )
            ref_threat_model = ThreatModel.objects.get(name=tm_name)
            # if "categories" in data:
            #     for single_category in data.categories:
            #         if single_category not in ref_threat_model.categories:
            #             ref_threat_model.categories.append(single_category)
            #             ref_threat_model.save()

            if "mitigations" in data:
                ThreatModel.objects(name=tm_name).update_one(
                    mitigations=data.get("mitigations"), upsert=True
                )

            if ref_threat_model not in ref_abuser_story.scenarios:
                ref_abuser_story.scenarios.append(ref_threat_model)
                ref_abuser_story.save()

            logger.info("Created Threat Scenario '{}'".format(tm_name))
            return respond(
                True,
                False,
                message="Successfully created Threat Scenario",
                data={"name": tm_name},
            )
        except Exception as e:
            logger.exception(e)
            return respond(False, True, message="Unable to load Threat Scenario"), 400


# swagger done
@app.route("/api/test/create", methods=["POST"])
@validate_user
@swag_from("swagger/test-case-create.yml")
def create_test_case():
    data = request.get_json()
    if not set(("test_case", "name", "threat_scenario")) <= set(data):
        logger.error(
            "Mandatory params 'test_case', 'name', 'threat_scenario' not in request"
        )
        input_val_err = respond(
            False,
            True,
            message="Mandatory params 'test_case', 'name', 'threat_scenario' not in request",
        )
        return input_val_err, 400
    else:
        try:
            ref_scenario = ThreatModel.objects.get(name=data.get("threat_scenario"))
        except DoesNotExist:
            project_not_exists = respond(
                False,
                True,
                message="Threat Scenario '{}' does not exist".format(
                    data.get("threat_scenario")
                ),
            )
            return project_not_exists, 404

        test_name = data.get("name")
        test_case = data.get("test_case")
        tool_list = data.get("tools", [])
        tag_list = data.get("tags", [])
        executed = data.get("executed", False)
        test_type = data.get("test_type", "discovery")

        try:
            Test.objects(name=test_name).update_one(
                name=test_name,
                test_case=test_case,
                executed=executed,
                test_type=test_type,
                scenario=ref_scenario,
                upsert=True,
            )
            if tool_list:
                Test.objects(name=test_name, scenario=ref_scenario).update_one(
                    tools=tool_list
                )

            if tag_list:
                Test.objects(name=test_name, scenario=ref_scenario).update_one(
                    tags=tag_list
                )

            ref_test = Test.objects.get(name=test_name, scenario=ref_scenario)
            if ref_test not in ref_scenario.tests:
                ref_scenario.tests.append(ref_test)
                ref_scenario.save()

            logger.info(
                "Created Test-Case '{}' for Threat Scenario '{}'".format(
                    test_name, ref_scenario.name
                )
            )
            return respond(
                True,
                False,
                message="Created Test-Case '{}' for Threat Scenario '{}'".format(
                    test_name, ref_scenario.name
                ),
                data={"name": test_name},
            )

        except Exception as e:
            logger.exception(e)
            return respond(False, True, message="Unable to create Test Case"), 400


# swagger done
@app.route("/api/target/create", methods=["POST"])
@validate_user
@swag_from("swagger/target-create-update.yml")
def create_target():
    data = request.get_json()
    if not set(("name", "url", "project")) <= set(data):
        logger.error("Mandatory params 'name', 'url', 'project' not in request")
        input_val_err = respond(
            False,
            True,
            message="Mandatory params 'name', 'url', 'project' not in request",
        )
        return input_val_err, 400
    else:
        try:
            ref_project = Project.objects.get(name=data.get("project"))
        except Exception:
            return respond(False, True, message="Project not found"), 404
        try:
            new_target = Target(
                name=data.get("name"), url=data.get("url"), project=ref_project
            )
            new_target.save()
            return respond(
                True,
                False,
                message="successfully created target",
                data={"name": data.get("name")},
            )
        except Exception:
            return respond(False, True, message="Unable to create Target")


@app.route("/api/scan/create", methods=["POST"])
@validate_user
@swag_from("swagger/scan-create.yml")
def create_scan():
    data = request.get_json()
    if not set(("tool", "target")) <= set(data):
        logger.error("Mandatory params 'tool', 'target' not in request")
        input_val_err = respond(
            False, True, message="Mandatory params 'tool', 'target' not in request",
        )
        return input_val_err, 400
    else:
        try:
            ref_target = Target.objects.get(name=data.get("target"))
            ref_project = Project.objects.get(id=ref_target.project.id)
        except Exception:
            return respond(False, True, message="Target not found"), 404
        try:
            new_scan = Scan(tool=data.get("tool"), target=ref_target)
            if "scan_type" in data:
                if data.get("scan_type") in ["SAST", "DAST", "SCA", "IAST", "Manual"]:
                    new_scan.scan_type = data.get("scan_type")

            new_scan.save()
            if new_scan not in ref_target.scans:
                ref_target.scans.append(new_scan)
                ref_target.save()

            ref_features = UseCase.objects(project=ref_project)
            for single_feature in ref_features:
                ref_scenarios = ThreatModel.objects(use_case=single_feature)
                for single_scenario in ref_scenarios:
                    for single_test in single_scenario.tests:
                        ref_test = Test.objects.get(id=single_test.id)
                        if data.get("tool") in ref_test.tools:
                            ref_test.executed = True
                            ref_test.save()

            return respond(
                True,
                False,
                message="successfully created scan",
                data={"name": new_scan.name},
            )
        except Exception as ex:
            logger.error(ex)
            return respond(False, True, message="Unable to create Scan")


@app.route("/api/vulnerability/create", methods=["POST"])
@validate_user
@swag_from("swagger/vulnerability-create.yml")
def create_vulnerability():
    data = request.get_json()
    if "name" not in data and "scan" not in data:
        return (
            respond(
                False, True, message="Mandatory field 'name' and 'scan' not in request"
            ),
            400,
        )
    else:
        scan = data.get("scan")
        try:
            ref_scan = Scan.objects.get(name=scan)
        except Exception:
            return respond(False, True, message="Unable to find scan"), 404

        try:
            ref_target = Target.objects.get(id=ref_scan.target.id)
            ref_project = Project.objects.get(id=ref_target.project.id)
        except Exception:
            return respond(False, True, message="Unable to find target"), 404

        name = data.get("name")
        severity = data.get("severity", 1)
        cwe = data.get("cwe", 0)
        new_vul = Vulnerability(name=name, severity=severity, cwe=cwe)
        new_vul.scan = ref_scan
        new_vul.target = ref_target
        if "description" in data:
            new_vul.description = data.get("description")
        if "observation" in data:
            new_vul.description = data.get("observation")
        if "vul_name" in data:
            new_vul.description = data.get("vul_name")
        if "remediation" in data:
            new_vul.description = data.get("remediation")

        try:
            new_vul.save()
            if (
                "evidences" in data
                and isinstance(data.get("evidences"), list)
                and data.get("evidences")
            ):
                all_evidences = data.get("evidences")
                for single in all_evidences:
                    new_evid = VulnerabilityEvidence()
                    new_evid.evidence_type = ref_scan.scan_type
                    if "log" in single:
                        new_evid.log = single.get("log")
                    if "url" in single:
                        new_evid.url = single.get("url")
                    if "param" in single:
                        new_evid.param = single.get("param")
                    if "line_num" in single:
                        new_evid.line_num = single.get("line_num")
                    if "attack" in single:
                        new_evid.attack = single.get("attack")
                    if "info" in single:
                        new_evid.info = single.get("info")
                    new_evid.vuln = new_vul

                    try:
                        new_evid.save()
                        if new_evid not in new_vul.evidences:
                            new_vul.evidences.append(new_evid)
                            new_vul.save()
                    except Exception as ev_e:
                        logger.error(ev_e)
                        return (
                            respond(False, True, message="Unable to save evidence"),
                            500,
                        )

            return respond(
                True,
                False,
                message="Vulnerability successfully created",
                data={"name": name},
            )
        except Exception as vul_ex:
            logger.error(vul_ex)
            return (
                respond(
                    False,
                    True,
                    "Unable to save vulnerability with name '{}'".format(name),
                ),
                500,
            )


@app.route("/api/project/read", methods=["GET", "POST"])
@app.route("/api/project/read/<page_num>", methods=["GET", "POST"])
@validate_user
@swag_from("swagger/get-project.yml")
def get_project(page_num=1):
    if request.method == "GET":
        num_pages = (Project.objects.count() % items_per_page) + 1
        if num_pages > 1 and page_num:
            if page_num == 1:
                project_list = json.loads(
                    Project.objects.limit(items_per_page).to_json()
                )
                return respond(
                    True,
                    False,
                    message="Successfully retrieved data",
                    data=project_list,
                )
            else:
                offset = (page_num - 1) * items_per_page
                project_list = json.loads(
                    Project.objects.skip(offset).limit(items_per_page).to_json()
                )
                return respond(
                    True,
                    False,
                    message="Successfully retrieved data",
                    data=project_list,
                )
        else:
            project_list = json.loads(Project.objects().to_json())
            return respond(True, False, data=project_list)

    if request.method == "POST":
        data = request.get_json()
        if "name" in data:
            try:
                ref_project = json.loads(
                    Project.objects.get(name=data.get("name")).to_json()
                )
                return respond(True, False, data=ref_project)
            except Exception as e:
                logger.exception(e)
                return respond(False, True, message="Unable to find the project"), 404


@app.route("/api/feature/read", methods=["GET", "POST"])
@validate_user
@swag_from("swagger/get-feature.yml")
def get_features():
    if request.method == "GET":
        user_story_list = json.loads(UseCase.objects().to_json())
        return respond(True, False, data=user_story_list)
    elif request.method == "POST":
        data = request.get_json()
        if "project" in data:
            try:
                ref_project = Project.objects.get(name=data.get("project"))
            except Exception:
                return respond(False, True, message="Project does not exist"), 404

            if "short_name" in data:
                try:
                    ref_feature = json.loads(
                        UseCase.objects.get(
                            short_name=data.get("short_name"), project=ref_project
                        ).to_json()
                    )
                    return respond(True, False, data=ref_feature)
                except Exception as e:
                    logger.exception(e)
                    return (
                        respond(
                            False,
                            True,
                            message="Unable to fetch the referenced user story",
                        ),
                        404,
                    )
            else:
                if "page" in data:
                    page_num = data.get("page")
                    num_pages = (UseCase.objects.count() % items_per_page) + 1
                    if num_pages > 1 and page_num:
                        if page_num == 1:
                            feature_list = json.loads(
                                UseCase.objects(project=ref_project)
                                .limit(items_per_page)
                                .to_json()
                            )
                            return respond(
                                True,
                                False,
                                message="Successfully retrieved data",
                                data=feature_list,
                            )
                        else:
                            offset = (page_num - 1) * items_per_page
                            feature_list = json.loads(
                                UseCase.objects(project=ref_project)
                                .skip(offset)
                                .limit(items_per_page)
                                .to_json()
                            )
                            return respond(
                                True,
                                False,
                                message="Successfully retrieved data",
                                data=feature_list,
                            )
                else:
                    feature_list = json.loads(
                        UseCase.objects(project=ref_project).to_json()
                    )
                    return respond(
                        True,
                        False,
                        message="Successfully retrieved data",
                        data=feature_list,
                    )
    else:
        return respond(False, True, message="Unable to find User Stories/Features"), 404


@app.route("/api/abuses/read", methods=["POST"])
@validate_user
@swag_from("swagger/get-abuse.yml")
def get_abuser_story():
    data = request.get_json()
    if "user_story" in data:
        try:
            ref_use_case = UseCase.objects.get(short_name=data.get("user_story"))
        except Exception:
            return respond(False, True, message="User Story does not exist"), 404

        if "short_name" in data:
            try:
                ref_abuse = json.loads(
                    AbuseCase.objects.get(
                        short_name=data.get("short_name"), use_case=ref_use_case
                    ).to_json()
                )
                return respond(True, False, data=ref_abuse)
            except Exception as e:
                logger.exception(e)
                return (
                    respond(
                        False,
                        True,
                        message="Unable to fetch the referenced abuser story",
                    ),
                    404,
                )
        else:
            if "page" in data:
                page_num = data.get("page")
                num_pages = (AbuseCase.objects.count() % items_per_page) + 1
                if num_pages > 1 and page_num:
                    if page_num == 1:
                        feature_list = json.loads(
                            AbuseCase.objects(use_case=ref_use_case)
                            .limit(items_per_page)
                            .to_json()
                        )
                        return respond(
                            True,
                            False,
                            message="Successfully retrieved data",
                            data=feature_list,
                        )
                    else:
                        offset = (page_num - 1) * items_per_page
                        feature_list = json.loads(
                            AbuseCase.objects(use_case=ref_use_case)
                            .skip(offset)
                            .limit(items_per_page)
                            .to_json()
                        )
                        return respond(
                            True,
                            False,
                            message="Successfully retrieved data",
                            data=feature_list,
                        )
            else:
                feature_list = json.loads(
                    AbuseCase.objects(use_case=ref_use_case).to_json()
                )
                return respond(
                    True,
                    False,
                    message="Successfully retrieved data",
                    data=feature_list,
                )

    return (
        respond(
            False,
            True,
            message="Unable to find Abuser Stories. You need to provide a reference feature/user story",
        ),
        404,
    )


@app.route("/api/scenarios/read", methods=["GET", "POST"])
@validate_user
@swag_from("swagger/get-scenario.yml")
def get_threat_scenario():
    if request.method == "GET":
        threat_scenario_list = json.loads(ThreatModel.objects().to_json())
        return respond(True, False, data=threat_scenario_list)
    elif request.method == "POST":
        data = request.get_json()
        if "abuser_story" in data:
            try:
                ref_abuse = AbuseCase.objects.get(short_name=data.get("abuser_story"))
            except Exception:
                return respond(False, True, message="Abuser Story does not exist"), 404

            if "name" in data:
                try:
                    ref_scenario = json.loads(
                        ThreatModel.objects.get(
                            name=data.get("name"), abuse_case=ref_abuse
                        ).to_json()
                    )
                    return respond(True, False, data=ref_scenario)
                except Exception as e:
                    logger.exception(e)
                    return (
                        respond(
                            False,
                            True,
                            message="Unable to fetch the referenced threat scenario",
                        ),
                        404,
                    )
            else:
                if "page" in data:
                    page_num = data.get("page")
                    num_pages = (ThreatModel.objects.count() % items_per_page) + 1
                    if num_pages > 1 and page_num:
                        if page_num == 1:
                            feature_list = json.loads(
                                ThreatModel.objects(abuse_case=ref_abuse)
                                .limit(items_per_page)
                                .to_json()
                            )
                            return respond(
                                True,
                                False,
                                message="Successfully retrieved data",
                                data=feature_list,
                            )
                        else:
                            offset = (page_num - 1) * items_per_page
                            feature_list = json.loads(
                                ThreatModel.objects(abuse_case=ref_abuse)
                                .skip(offset)
                                .limit(items_per_page)
                                .to_json()
                            )
                            return respond(
                                True,
                                False,
                                message="Successfully retrieved data",
                                data=feature_list,
                            )
                else:
                    feature_list = json.loads(
                        ThreatModel.objects(abuse_case=ref_abuse).to_json()
                    )
                    return respond(
                        True,
                        False,
                        message="Successfully retrieved data",
                        data=feature_list,
                    )
    else:
        return respond(False, True, message="Unable to find Threat Scenarios"), 404


@app.route("/api/test/read", methods=["POST"])
@validate_user
@swag_from("swagger/get-tests.yml")
def get_test_case():
    data = request.get_json()
    if "scenario" in data:
        try:
            ref_scenario = ThreatModel.objects.get(name=data.get("scenario"))
        except Exception:
            return respond(False, True, message="Abuser Story does not exist"), 404

        if "name" in data:
            try:
                ref_test = json.loads(
                    Test.objects.get(
                        name=data.get("name"), scenario=ref_scenario
                    ).to_json()
                )
                return respond(True, False, data=ref_test)
            except Exception as e:
                logger.exception(e)
                return (
                    respond(
                        False, True, message="Unable to fetch the referenced test-case",
                    ),
                    404,
                )
        else:
            if "page" in data:
                page_num = data.get("page")
                num_pages = (Test.objects.count() % items_per_page) + 1
                if num_pages > 1 and page_num:
                    if page_num == 1:
                        feature_list = json.loads(
                            Test.objects(abuse_case=ref_scenario)
                            .limit(items_per_page)
                            .to_json()
                        )
                        return respond(
                            True,
                            False,
                            message="Successfully retrieved data",
                            data=feature_list,
                        )
                    else:
                        offset = (page_num - 1) * items_per_page
                        feature_list = json.loads(
                            Test.objects(abuse_case=ref_scenario)
                            .skip(offset)
                            .limit(items_per_page)
                            .to_json()
                        )
                        return respond(
                            True,
                            False,
                            message="Successfully retrieved data",
                            data=feature_list,
                        )
            else:
                feature_list = json.loads(Test.objects(scenario=ref_scenario).to_json())
                return respond(
                    True,
                    False,
                    message="Successfully retrieved data",
                    data=feature_list,
                )

    return respond(False, True, message="Unable to find Threat Scenarios"), 404


@app.route("/api/scenario/vuln/", methods=["POST"])
@validate_user
def map_threat_scenario_vul():
    data = request.get_json()
    if "id" not in data:
        return respond(False, True, message="Mandatory param 'id' not in request"), 400
    else:
        try:
            ref_scenario = ThreatModel.objects.get(id=data.get("id"))
        except Exception:
            return respond(False, True, message="Unable to find Threat Scenario")

        if ref_scenario.cwe:
            ref_abuse = AbuseCase.objects.get(id=ref_scenario.abuse.id)
            ref_use_case = UseCase.objects.get(id=ref_abuse.use_case.id)
            ref_project = Project.objects.get(id=ref_use_case.project.id)
            ref_targets = Target.objects(project=ref_project)
            for single_target in ref_targets:
                ref_vulns = Vulnerability.objects(target=single_target)
            if ref_vulns:
                return respond(
                    True,
                    False,
                    message="successfully returned mapped objects",
                    data={
                        "threat_scenario": json.loads(ref_scenario.to_json()),
                        "vulnerabilities": json.loads(ref_vulns.to_json()),
                    },
                )


@app.route("/api/scenario/severity", methods=["GET"])
@validate_user
def threat_scenario_severity():
    if request.method == "GET":
        try:
            scenario_severity_list = json.loads(
                ThreatModel.objects().values_list("severity").to_json()
            )
            return respond(
                True,
                False,
                message="Successfully retrieved data",
                data=scenario_severity_list,
            )
        except Exception as e:
            logger.exception(e)
            return respond(False, True, message="Therat Scenario does not exist"), 404
    else:
        return (
            respond(False, True, message="Unable to find Threat Scenarios severity"),
            404,
        )


@app.route("/api/vulnerability/severity", methods=["GET"])
@validate_user
def vulnerability_severity():
    if request.method == "GET":
        try:
            scenario_severity_list = json.loads(
                Vulnerability.objects().values_list("severity").to_json()
            )
            return respond(
                True,
                False,
                message="Successfully retrieved data",
                data=scenario_severity_list,
            )
        except Exception as e:
            logger.exception(e)
            return respond(False, True, message="Therat Scenario does not exist"), 404
    else:
        return (
            respond(False, True, message="Unable to find Threat Scenarios severity"),
            404,
        )


### Select APIs that we need
# Get Vulnerabilities by Target


@app.route("/api/target/read", methods=["GET", "POST"])
@validate_user
def get_target(page_num=1):
    if request.method == "GET":
        num_pages = (Target.objects.count() % items_per_page) + 1
        if num_pages > 1 and page_num:
            if page_num == 1:
                target_list = json.loads(Target.objects.limit(items_per_page).to_json())
                return respond(
                    True,
                    False,
                    message="Successfully retrieved data",
                    data=target_list,
                )
            else:
                offset = (page_num - 1) * items_per_page
                target_list = json.loads(
                    Target.objects.skip(offset).limit(items_per_page).to_json()
                )
                return respond(
                    True,
                    False,
                    message="Successfully retrieved data",
                    data=target_list,
                )
        else:
            target_list = json.loads(Scan.objects().to_json())
            return respond(True, False, data=scan_list)

    if request.method == "POST":
        data = request.get_json()
        if "project" in data:
            ref_project = Project.objects.get(name = data.get('project'))
            targets_for_project = json.loads(
                Target.objects(project=ref_project).to_json()
            )
            return respond(True, False, data = targets_for_project)
         
        if "name" in data:
            specific_target = json.loads(Target.objects.get(name = data.get('name')).to_json())
            return respond(True, False, data = specific_target)


@app.route("/api/scan/read", methods=["GET", "POST"])
@validate_user
def get_scan(page_num=1):
    if request.method == "GET":
        num_pages = (Scan.objects.count() % items_per_page) + 1
        if num_pages > 1 and page_num:
            if page_num == 1:
                scan_list = json.loads(Scan.objects.limit(items_per_page).to_json())
                return respond(
                    True, False, message="Successfully retrieved data", data=scan_list,
                )
            else:
                offset = (page_num - 1) * items_per_page
                scan_list = json.loads(
                    Scan.objects.skip(offset).limit(items_per_page).to_json()
                )
                return respond(
                    True, False, message="Successfully retrieved data", data=scan_list,
                )
        else:
            scan_list = json.loads(Scan.objects().to_json())
            return respond(True, False, data=scan_list)

    if request.method == "POST":
        data = request.get_json()
        if "name" in data:
            try:
                ref_scan = json.loads(Scan.objects.get(name=data.get("name")).to_json())
                return respond(True, False, data=ref_scan)
            except Exception as e:
                logger.exception(e)
                return respond(False, True, message="Unable to find the scan"), 404


@app.route("/api/scenarios/project", methods=["POST"])
@validate_user
def get_threat_scenario_by_project():
    data = request.get_json()
    if "project" in data:
        try:
            ref_project = Project.objects.get(name=data.get("project"))
        except Exception:
            return respond(False, True, message="Project does not exist"), 404
        user_story = UseCase.objects(project=ref_project).to_json()
        d = json.loads(user_story)
        try:
            user_stories_list = [a.get("_id").get("$oid") for a in d]
            ref_threatScenario = json.loads(
                ThreatModel.objects.filter(use_case__in=user_stories_list).to_json()
            )
            return respond(True, False, data=ref_threatScenario)
        except Exception as e:
            return respond(False, True, message="Scenario does not exist"), 404
    else:
        return respond(False, True, message="Project does not exist"), 404
    return respond(False, True, message="Scenario does not exist"), 404


@app.route("/api/vulnerability/read", methods=["GET", "POST"])
@validate_user
def get_vulnerability(page_num=1):
    if request.method == "GET":
        num_pages = (Vulnerability.objects.count() % items_per_page) + 1
        if num_pages > 1 and page_num:
            if page_num == 1:
                vul_list = json.loads(
                    Vulnerability.objects.limit(items_per_page).to_json()
                )
                return respond(
                    True, False, message="Successfully retrieved data", data=vul_list,
                )
            else:
                offset = (page_num - 1) * items_per_page
                vul_list = json.loads(
                    Vulnerability.objects.skip(offset).limit(items_per_page).to_json()
                )
                return respond(
                    True, False, message="Successfully retrieved data", data=vul_list,
                )
        else:
            vul_list = json.loads(Vulnerability.objects().to_json())
            return respond(True, False, data=vul_list)

    if request.method == "POST":
        data = request.get_json()
        if "name" in data:
            try:
                ref_scan = json.loads(
                    Vulnerability.objects.get(name=data.get("name")).to_json()
                )
                return respond(True, False, data=ref_scan)
            except Exception as e:
                logger.exception(e)
                return (
                    respond(False, True, message="Unable to find the vulnerability"),
                    404,
                )


@app.route("/api/vulnerability/project", methods=["POST"])
@validate_user
def get_vulnerability_by_project():
    data = request.get_json()
    if "project" in data:
        vul_dict = {}
        try:
            ref_project = Project.objects.get(name=data.get("project"))
        except Exception:
            return respond(False, True, message="Project does not exist"), 404
        try:
            target_obj = Target.objects(project=ref_project)
        except Exception:
            return respond(False, True, message="Target does not exist"), 404
        try:
            for single_target in target_obj:
                ref_vuls = json.loads(Vulnerability.objects(target=single_target).to_json())
                vul_dict['data'] = ref_vuls
                  
            return respond(True, False, data=vul_dict)
        except Exception as e:
            return respond(False, True, message="Vulnerability does not exist"), 404
    else:
        return respond(False, True, message="Project does not exist"), 404
    return respond(False, True, message="Vulnerability does not exist"), 404


@app.route("/api/scan/project", methods=["POST"])
@validate_user
def get_scan_by_project():
    data = request.get_json()
    if "project" in data:
        resp_dict = {}
        try:
            ref_project = Project.objects.get(name=data.get("project"))
            resp_dict['project'] = ref_project.name
        except Exception:
            return respond(False, True, message="Project does not exist"), 404
        try:
            target_obj = Target.objects(project=ref_project)
        except Exception:
            return respond(False, True, message="Target does not exist"), 404
        try:
            resp_dict['data'] = []
            for single_target in target_obj:
                ref_scans = Scan.objects(target=single_target)
                for single_scan in ref_scans:
                    data_dict = {
                        "name": single_scan.name,
                        "target": single_target.name,
                        "tool": single_scan.tool
                    }
                    resp_dict['data'].append(data_dict)

            return respond(True, False, data=resp_dict)
        except Exception as e:
            return respond(False, True, message="Scans does not exist"), 404
    else:
        return respond(False, True, message="Project does not exist"), 404
    return respond(False, True, message="Scans does not exist"), 404


@app.route("/api/user-story/project", methods=["POST"])
@validate_user
def get_user_story_tree_by_project():
    data = request.get_json()
    user_story_tree = []
    if "project" in data:
        try:
            ref_project = Project.objects.get(name=data.get("project"))
        except Exception:
            return respond(False, True, message="Project does not exist"), 404
        try:
            usecases_obj = UseCase.objects(project=ref_project.id)
        except Exception:
            return respond(False, True, message="Target does not exist"), 404
        for usecase in usecases_obj:
            userStory_dict = {}
            userStory_dict["name"] = usecase.short_name
            userStory_dict["description"] = usecase.description
            userStory_dict["children"] = []
            userStory_dict["type"] = "us"
            userStory_dict["title"] = "User Story"
            for abuses in usecase.abuses:
                abuserStory_dict = {}
                abuserStory_dict["name"] = abuses.short_name
                abuserStory_dict["description"] = abuses.description
                abuserStory_dict["children"] = []
                abuserStory_dict["type"] = "as"
                abuserStory_dict["title"] = "Abuser Story"
                userStory_dict["children"].append(abuserStory_dict)
                for scenario in abuses.scenarios:
                    threat_scenario_dict = {}
                    threat_scenario_dict["name"] = scenario.name
                    threat_scenario_dict["description"] = scenario.description
                    threat_scenario_dict["vul_name"] = scenario.vul_name
                    threat_scenario_dict["severity"] = scenario.severity
                    threat_scenario_dict["cwe"] = scenario.cwe
                    threat_scenario_dict["children"] = []
                    threat_scenario_dict["type"] = "sce"
                    threat_scenario_dict["title"] = "Threat Scenario"
                    abuserStory_dict["children"].append(threat_scenario_dict)
                    for test in scenario.tests:
                        test_dict = {}
                        test_dict["name"] = test.name
                        test_dict["test_case"] = test.test_case
                        test_dict["tools"] = test.tools
                        test_dict["test_type"] = test.test_type
                        test_dict["executed"] = test.executed
                        test_dict["type"] = "tc"
                        test_dict["title"] = "Test Case"
                        threat_scenario_dict["children"].append(test_dict)
            user_story_tree.append(userStory_dict)
        try:
            ref_scans = json.loads(json.dumps(user_story_tree))
            return respond(True, False, data=ref_scans)
        except Exception as e:
            return respond(False, True, message="UserStory does not exist"), 404
    else:
        return respond(False, True, message="Project does not exist"), 404
    return respond(False, True, message="UserStory does not exist"), 404


@app.route("/api/abuser-story/project", methods=["POST"])
@validate_user
def get_abuser_story_tree_by_project():
    data = request.get_json()
    abuser_story_tree = []
    if "project" in data:
        try:
            ref_project = Project.objects.get(name=data.get("project"))
        except Exception:
            return respond(False, True, message="Project does not exist"), 404
        try:
            usecases_obj = UseCase.objects(project=ref_project.id)
        except Exception:
            return respond(False, True, message="Target does not exist"), 404
        for usecase in usecases_obj:
            for abuses in usecase.abuses:
                abuserStory_dict = {}
                abuserStory_dict["name"] = abuses.short_name
                abuserStory_dict["description"] = abuses.description
                abuserStory_dict["children"] = []
                abuserStory_dict["type"] = "as"
                abuserStory_dict["title"] = "Abuser Story"
                # userStory_dict['children'].append(abuserStory_dict)
                for scenario in abuses.scenarios:
                    threat_scenario_dict = {}
                    threat_scenario_dict["name"] = scenario.name
                    threat_scenario_dict["description"] = scenario.description
                    threat_scenario_dict["vul_name"] = scenario.vul_name
                    threat_scenario_dict["severity"] = scenario.severity
                    threat_scenario_dict["cwe"] = scenario.cwe
                    threat_scenario_dict["children"] = []
                    threat_scenario_dict["type"] = "sce"
                    threat_scenario_dict["title"] = "Threat Scenario"
                    abuserStory_dict["children"].append(threat_scenario_dict)
                    for test in scenario.tests:
                        test_dict = {}
                        test_dict["name"] = test.name
                        test_dict["test_case"] = test.test_case
                        test_dict["executed"] = test.executed
                        test_dict["tools"] = test.tools
                        test_dict["test_type"] = test.test_type
                        test_dict["type"] = "tc"
                        test_dict["title"] = "Test Case"
                        threat_scenario_dict["children"].append(test_dict)
                abuser_story_tree.append(abuserStory_dict)
        try:
            ref_scans = json.loads(json.dumps(abuser_story_tree))
            return respond(True, False, data=ref_scans)
        except Exception as e:
            return respond(False, True, message="AbuserStory does not exist"), 404
    else:
        return respond(False, True, message="Project does not exist"), 404
    return respond(False, True, message="AbuserStory does not exist"), 404


@app.route("/api/threat-scenario/project", methods=["POST"])
@validate_user
def get_threat_scenario_tree_by_project():
    data = request.get_json()
    threat_scenario_tree = []
    if "project" in data:
        try:
            ref_project = Project.objects.get(name=data.get("project"))
        except Exception:
            return respond(False, True, message="Project does not exist"), 404
        try:
            usecases_obj = UseCase.objects(project=ref_project.id)
        except Exception:
            return respond(False, True, message="Target does not exist"), 404
        for usecase in usecases_obj:
            for abuses in usecase.abuses:
                for scenario in abuses.scenarios:
                    threat_scenario_dict = {}
                    threat_scenario_dict["name"] = scenario.name
                    threat_scenario_dict["description"] = scenario.description
                    threat_scenario_dict["vul_name"] = scenario.vul_name
                    threat_scenario_dict["severity"] = scenario.severity
                    threat_scenario_dict["cwe"] = scenario.cwe
                    threat_scenario_dict["children"] = []
                    threat_scenario_dict["type"] = "sce"
                    threat_scenario_dict["title"] = "Threat Scenario"
                    for test in scenario.tests:
                        test_dict = {}
                        test_dict["name"] = test.name
                        test_dict["test_case"] = test.test_case
                        test_dict["tools"] = test.tools
                        test_dict["test_type"] = test.test_type
                        test_dict["executed"] = test.executed
                        test_dict["type"] = "tc"
                        test_dict["title"] = "Test Case"
                        threat_scenario_dict["children"].append(test_dict)
                    threat_scenario_tree.append(threat_scenario_dict)
        try:
            ref_scans = json.loads(json.dumps(threat_scenario_tree))
            return respond(True, False, data=ref_scans)
        except Exception as e:
            return respond(False, True, message="ThreatScenario does not exist"), 404
    else:
        return respond(False, True, message="Project does not exist"), 404
    return respond(False, True, message="ThreatScenario does not exist"), 404


@app.route("/api/threatmap/project", methods=["POST"])
@validate_user
def get_threatmap_by_project():
    data = request.get_json()
    threat_map = {}
    if "project" in data:
        try:
            ref_project = Project.objects.get(name=data.get("project"))
            threat_map["name"] = ref_project.name
            threat_map["children"] = []
            threat_map["type"] = "Project"
            threat_map["id"] = 1
        except Exception:
            return respond(False, True, message="Project does not exist"), 404
        try:
            usecases_obj = UseCase.objects(project=ref_project.id)
        except Exception:
            return respond(False, True, message="Target does not exist"), 404
        for usecase in usecases_obj:
            userStory_id = str(uuid.uuid4())
            userStory_dict = {}
            userStory_dict["id"] = userStory_id
            userStory_dict["name"] = usecase.short_name
            userStory_dict["title"] = usecase.description
            userStory_dict["type"] = "Feature"
            userStory_dict["children"] = []
            threat_map["children"].append(userStory_dict)
            for abuses in usecase.abuses:
                abuserStory_id = str(uuid.uuid4())
                abuserStory_dict = {}
                abuserStory_dict["id"] = abuserStory_id
                abuserStory_dict["name"] = abuses.short_name
                abuserStory_dict["title"] = abuses.description
                abuserStory_dict["children"] = []
                abuserStory_dict["type"] = "Abuses"
                userStory_dict["children"].append(abuserStory_dict)
                for scenario in abuses.scenarios:
                    scenario_id = str(uuid.uuid4())
                    threat_scenario_dict = {}
                    threat_scenario_dict["id"] = scenario_id
                    threat_scenario_dict["name"] = scenario.name
                    threat_scenario_dict["title"] = scenario.description
                    threat_scenario_dict["vul_name"] = scenario.vul_name
                    threat_scenario_dict["severity"] = scenario.severity
                    threat_scenario_dict["cwe"] = scenario.cwe
                    threat_scenario_dict["children"] = []
                    threat_scenario_dict["type"] = "Scenarios"
                    abuserStory_dict["children"].append(threat_scenario_dict)
                    for test in scenario.tests:
                        test_id = str(uuid.uuid4())
                        test_dict = {}
                        test_dict["id"] = test_id
                        test_dict["name"] = test.name
                        test_dict["title"] = test.test_case
                        test_dict["tools"] = test.tools
                        test_dict["test_type"] = test.test_type
                        test_dict["executed"] = test.executed
                        test_dict["type"] = "Test Cases"
                        threat_scenario_dict["children"].append(test_dict)
        try:
            ref_threatmap = json.loads(json.dumps(threat_map))
            return respond(True, False, data=ref_threatmap)
        except Exception as e:
            return respond(False, True, message="THreatMap does not exist"), 404
    else:
        return respond(False, True, message="Project does not exist"), 404
    return respond(False, True, message="THreatMap does not exist"), 404


@app.route("/api/scan-vuls/project", methods=["POST"])
@validate_user
def get_individual_scan_vuls():
    data = request.get_json()
    if "name" in data:
        try:
            ref_scans = Scan.objects.get(name=data.get("name"))
            ref_vuls = json.loads(Vulnerability.objects(scan=ref_scans.id).to_json())
            return respond(True, False, data=ref_vuls)
        except Exception as e:
            return respond(False, True, message="Scans does not exist"), 404
    else:
        return respond(False, True, message="Project does not exist"), 404
    return respond(False, True, message="Scans does not exist"), 404


@app.route("/api/asvs", methods=["POST"])
@validate_user
def get_asvs_vuls():
    data = request.get_json()
    if "cwe" in data:
        try:
            ref_asvs = json.loads(ASVS.objects(cwe=data.get("cwe")).to_json())
            return respond(True, False, data=ref_asvs)
        except Exception as e:
            return respond(False, True, message="ASVS does not exist"), 404
    else:
        return respond(False, True, message="Project does not exist"), 404

    return respond(False, True, message="ASVS does not exist"), 404


@app.route("/api/delete/feature", methods=["POST"])
@validate_user
def delete_feature():
    data = request.get_json()
    if "name" not in data and "project" not in data:
        return (
            respond(
                False,
                True,
                message="Mandatory fields 'name' and 'project' not in request",
            ),
            400,
        )

    try:
        ref_project = Project.objects.get(name=data.get("project"))
        ref_use_case = UseCase.objects.get(
            short_name=data.get("name"), project=ref_project
        )
        ref_use_case.delete()
        return respond(
            True,
            False,
            message="Successfully deleted Feature: {}".format(data.get("name")),
        )
    except Exception as del_e:
        logger.error(del_e)
        return respond(False, True, message="Unable to delete Use-Case"), 500


@app.route("/api/delete/abuser-story", methods=["POST"])
@validate_user
def delete_abuse_case():
    data = request.get_json()
    if "name" not in data and "feature" not in data:
        return (
            respond(
                False,
                True,
                message="Mandatory fields 'name' and 'feature' not in request",
            ),
            400,
        )

    try:
        ref_use_case = UseCase.objects.get(short_name=data.get("feature"))
        ref_abuse = AbuseCase.objects.get(
            short_name=data.get("name"), use_case=ref_use_case
        )
        ref_abuse.delete()
        return respond(
            True,
            False,
            message="Successfully deleted Abuser Story: {}".format(data.get("name")),
        )
    except Exception as del_e:
        logger.error(del_e)
        return respond(False, True, message="Unable to delete Abuser Story"), 500


@app.route("/api/delete/scenario", methods=["POST"])
@validate_user
def delete_scenario():
    data = request.get_json()
    if "name" not in data and "abuser_story" not in data:
        return (
            respond(
                False,
                True,
                message="Mandatory fields 'name' and 'abuser_story' not in request",
            ),
            400,
        )

    try:
        ref_abuse_case = AbuseCase.objects.get(short_name=data.get("abuser_story"))
        ref_scenario = ThreatModel.objects.get(
            name=data.get("name"), abuse_case=ref_abuse_case
        )
        ref_scenario.delete()
        return respond(
            True,
            False,
            message="Successfully deleted Threat Scenario: {}".format(data.get("name")),
        )
    except Exception as del_e:
        logger.error(del_e)
        return respond(False, True, message="Unable to delete Threat Scenario"), 500


@app.route("/api/delete/test", methods=["POST"])
@validate_user
def delete_test():
    data = request.get_json()
    if "name" not in data and "scenario" not in data:
        return (
            respond(
                False,
                True,
                message="Mandatory fields 'name' and 'scenario' not in request",
            ),
            400,
        )

    try:
        ref_scenario = ThreatModel.objects.get(name=data.get("scenario"))
        ref_test = Test.objects.get(name=data.get("name"), scenario=ref_scenario)
        ref_scenario.delete()
        return respond(
            True,
            False,
            message="Successfully deleted Test-Case: {}".format(data.get("name")),
        )
    except Exception as del_e:
        logger.error(del_e)
        return respond(False, True, message="Unable to delete Test Case"), 500


@app.route("/api/delete/project", methods=["POST"])
@validate_user
def delete_project():
    data = request.get_json()
    if "name" not in data:
        return (
            respond(False, True, message="Mandatory fields 'name' not in request"),
            400,
        )

    try:
        ref_project = Project.objects.get(name=data.get("name"))
        ref_project.delete()
        return respond(
            True,
            False,
            message="Successfully deleted Project {}".format(data.get("name")),
        )
    except Exception as del_e:
        logger.error(del_e)
        return respond(False, True, message="Unable to delete Project"), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)

