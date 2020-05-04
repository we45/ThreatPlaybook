from flask import Flask, jsonify, request
import jwt
from secrets import token_urlsafe
from os import getenv
from tp_api.utils import (
    logger,
    connect_db,
    load_reload_asvs_db,
    load_reload_repo_db,
    initialize_superuser,
    respond,
)
from tp_api.models import *
import bcrypt
from functools import wraps
import json


JWT_PASSWORD = getenv("JWT_PASS", token_urlsafe(16))
items_per_page = 20
db = connect_db()
load_reload_repo_db()
load_reload_asvs_db()
initialize_superuser()


app = Flask(__name__)


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


@app.route("/", methods=["GET"])
def mytest():
    return "hello world"


@app.route("/change-password", methods=["POST"])
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


@app.route("/login", methods=["POST"])
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


@app.route("/project/create", methods=["POST"])
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


@app.route("/feature/create", methods=["POST"])
@validate_user
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


@app.route("/abuse-case/create", methods=["POST"])
@validate_user
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


@app.route("/scenario/create", methods=["POST"])
@validate_user
def create_threat_scenario():
    data = request.get_json()
    mandatory_params = ("vul_name", "name", "description", "feature", "abuser_story")
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
            cwe_val = data.get("cwe", 0)
            mitigations = data.get("mitigations", [])
            severity = int(data.get("severity", 1))
            tm_name = data.get("name")
            vul_name = data.get("vul_name")
            description = data.get("description")
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
            if "categories" in data:
                for single_category in data.categories:
                    if single_category not in ref_threat_model.categories:
                        ref_threat_model.categories.append(single_category)
                        ref_threat_model.save()

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


@app.route("/test/create", methods=["POST"])
@validate_user
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
            return respond(False, True, message="Unable to create Abuser Story"), 400


@app.route("/target/create", methods=["POST"])
@validate_user
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


@app.route("/scan/create", methods=["POST"])
@validate_user
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

            return respond(
                True,
                False,
                message="successfully created scan",
                data={"name": new_scan.name},
            )
        except Exception:
            return respond(False, True, message="Unable to create Scan")


@app.route("/vulnerability/create", methods=["POST"])
@validate_user
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
            ref_target = Target.objects.get(id = ref_scan.target.id)
        except Exception:
            return respond(False, True, message="Unable to find target"),404


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
                        # print(new_vul.cwe)
                        # if new_evid not in new_vul.evidences:
                        #     new_vul.append(new_evid)
                        #     print("append is happening")
                        #     new_vul.save()
                    except Exception:
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
        except Exception:
            return (
                respond(
                    False,
                    True,
                    "Unable to save vulnerability with name '{}'".format(name),
                ),
                500,
            )


@app.route("/project/read", methods=["GET", "POST"])
@app.route("/project/read/<page_num>", methods=["GET", "POST"])
@validate_user
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
                print(ref_project)
                return respond(True, False, data=ref_project)
            except Exception as e:
                logger.exception(e)
                return respond(False, True, message="Unable to find the project"), 404


@app.route("/feature/read", methods=["POST"])
@validate_user
def get_features():
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
                        False, True, message="Unable to fetch the referenced user story"
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

    return respond(False, True, message="Unable to find User Stories/Features"), 404


@app.route("/abuses/read", methods=["POST"])
@validate_user
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

    return respond(False, True, message="Unable to find Abuser Stories"), 404


@app.route("/scenarios/read", methods=["POST"])
@validate_user
def get_threat_scenario():
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

    return respond(False, True, message="Unable to find Threat Scenarios"), 404


@app.route("/test/read", methods=["POST"])
@validate_user
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


@app.route("/scenario/vuln/", methods=["POST"])
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
            ref_project = Project.objects.get(id = ref_use_case.project.id)
            ref_targets = Target.objects(project = ref_project)
            for single_target in ref_targets:
                ref_vulns = Vulnerability.objects(target = single_target)
            if ref_vulns:
                return respond(True, False, message="successfully returned mapped objects", data={
                    "threat_scenario": json.loads(ref_scenario.to_json()),
                    "vulnerabilities": json.loads(ref_vulns.to_json())
                })


if __name__ == "__main__":
    app.run(debug=True)
