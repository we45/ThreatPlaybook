from ast import parse
from starlette.responses import JSONResponse
from queries import *
from pyArango.connection import Connection, ConnectionError
from dotenv import load_dotenv
from os import defpath, getenv
from loguru import logger
import jwt
from fastapi import Request
import jmespath
from models import *

load_dotenv()

arango_host = getenv("ARANGO_HOST")
arango_port = getenv("ARANGO_PORT")

arango_url = f"{arango_host}:{arango_port}"

conn = Connection(
    arangoURL=arango_url, username=getenv("ARANGO_USER"), password=getenv("ARANGO_PASS")
)

JWT_PASS = getenv("JWT_PASS")


def get_db():
    """
    this is meant to generate a new database connection based on the global variable "conn" and returns a
    db object. It will throw an ConnectionError (arango native object) if its unable to connect
    """
    try:
        if conn.hasDatabase("threatplaybook"):
            db = conn["threatplaybook"]
            return db
        else:
            db = conn.createDatabase("threatplaybook")
            logger.info("New threatplaybook database created in arango")
            return db
    except ConnectionError as ce:
        logger.error("Unable to connect to ArangoDB instance")
        logger.error(ce.message)

    return


def validate_token(r: Request):
    if "Authorization" not in r.headers:
        return
    try:
        validated = jwt.decode(
            r.headers.get("Authorization"), JWT_PASS, algorithms=["HS256"]
        )
        return validated
    except jwt.DecodeError:
        logger.error(f"unable to validate token")
    except jwt.InvalidSignatureError:
        logger.error(f"invalid jwt signature")

    return


def validate_user_role(email, q_role, p_role):
    db = get_db()
    user_role = db.AQLQuery(
        ARANGO_VALIDATE_USER_ROLE, bindVars={"email": email, "role": q_role}
    )
    if user_role and len(user_role) > 0:
        if user_role[0].get("role") == p_role:
            return True

    return False


def does_user_exist(email):
    db = get_db()
    q_user = db.AQLQuery(
        ARANGO_GET_USER_BY_EMAIL, rawResults=True, bindVars={"email": email}
    )
    if q_user:
        return True

    return False


def does_namespace_exist(namespace: str):
    db = get_db()
    ns_exists = db.AQLQuery(ARANGO_GET_NAMESPACE_BY_NAME, bindVars={"name": namespace})
    if ns_exists and len(ns_exists) > 0:
        return True

    return False


parse_depth = {
    "group": 1,
    "namespace": 2,
    "application": 3,
    "user_story": 4,
    "abuser_story": 5,
    "threat_scenario": 6,
}

db = get_db()


def init_db():
    if not db.hasCollection("user"):
        db.createCollection(name="user")

    if not db.hasCollection("namespace"):
        db.createCollection(name="namespace")

    if not db.hasCollection("user_story"):
        db.createCollection(name="user_story")

    if not db.hasCollection("abuser_story"):
        db.createCollection(name="abuser_story")

    if not db.hasCollection("threat_scenario"):
        db.createCollection(name="threat_scenario")

    if not db.hasCollection("data_store"):
        db.createCollection(name="data_store")

    if not db.hasCollection("component"):
        db.createCollection(name="component")

    if not db.hasCollection("application"):
        db.createCollection(name="application")

    if not db.hasCollection("test_case"):
        db.createCollection(name="test_case")

    if not db.hasCollection("mitigation"):
        db.createCollection(name="mitigation")


class DuplicateUserException(Exception):
    pass


def create_user_in_db(user: User):
    if not does_user_exist(user.email):
        response = db.AQLQuery(
            ARANGO_INSERT_USER,
            rawResults=True,
            bindVars={
                "email": user.email,
                "password": user.password,
                "role": user.role,
            },
        )
        return response
    else:
        raise DuplicateUserException


def check_value_in_vertex(results: list, lookup: str):
    list_of_all_values = [
        value for elem in results for value in elem.get("vertex").values()
    ]
    if lookup in list_of_all_values:
        return True

    return False


def get_privs_for_user(results: list):
    results = list(results)
    exp = jmespath.compile("[].edges.privs[]")
    vals = exp.search(results)
    print(vals)
    return vals


def create_group(grp: GroupCreate):
    response = db.AQLQuery(
        ARANGO_CREATE_GROUP, bindVars={"name": grp.name, "description": grp.description}
    )
    return response


def assign_user_to_group(ug: UserGroupAssignment):
    q_user = db.AQLQuery(
        ARANGO_GET_USER_BY_EMAIL, rawResults=True, bindVars={"email": ug.email}
    )
    q_group = db.AQLQuery(
        ARANGO_GET_GROUP_BY_NAME, rawResults=True, bindVars={"name": ug.group_name}
    )
    if not q_user or not q_group:
        return False

    user_exists = all(d for d in q_user)
    group_exists = all(d for d in q_group)
    if user_exists and group_exists:
        user_key = q_user[0].get("_id")
        group_key = q_group[0].get("_id")
        print(user_key, group_key)
        add_ug = db.AQLQuery(
            ARANGO_ASSIGN_USER_TO_GROUP,
            bindVars={"userKey": user_key, "groupKey": group_key},
        )
        return True

    return False


def assign_group_to_ns(nsg: NamespaceGroupAssignment):
    q_group = db.AQLQuery(
        ARANGO_GET_GROUP_BY_NAME, rawResults=True, bindVars={"name": nsg.group_name}
    )
    q_ns = db.AQLQuery(
        ARANGO_GET_NAMESPACE_BY_NAME, rawResults=True, bindVars={"name": nsg.ns_name}
    )
    if not q_group or not q_ns:
        return False

    group_exists = all(d for d in q_group)
    ns_exists = all(d for d in q_ns)
    if ns_exists and group_exists:
        group_key = q_group[0].get("_id")
        ns_key = q_ns[0].get("_id")
        print(group_key, ns_key)
        add_ug = db.AQLQuery(
            ARANGO_ASSIGN_GROUP_NAMESPACE,
            bindVars={"groupKey": group_key, "nsKey": ns_key, "privs": nsg.privs},
        )
        return True

    return False


def validate_user_access(up: LookupUserPrivileges):
    q_user = db.AQLQuery(
        ARANGO_GET_USER_BY_EMAIL, rawResults=True, bindVars={"email": up.email}
    )
    user_exists = all(d for d in q_user)
    if not user_exists:
        return False

    if q_user[0].get("role") == "admin":
        return True

    end_depth = parse_depth[up.depth]
    access_check = db.AQLQuery(
        ARANGO_LOOKUP_USER_PRIVS,
        rawResults=True,
        bindVars={"email": up.email, "depth": end_depth},
    )
    if not all(d for d in access_check):
        return False

    is_value_in_vertex = check_value_in_vertex(access_check, lookup=up.lookup_obj)
    if not is_value_in_vertex:
        return False

    privs = get_privs_for_user(results=access_check)
    if not privs:
        return False

    if up.priv_expected in privs:
        return True

    return False


def check_user_access_and_privs(
    r: Request, lobj: str = None, ltype: str = None, expected_privs: str = None
):
    token = validate_token(r)
    if not token:
        logger.error("Unable to validate user authorization token")
        return False
    if expected_privs and lobj and ltype and ltype in parse_depth.keys():
        lookup_privs = LookupUserPrivileges(
            email=token.get("user"),
            lookup_obj=lobj,
            depth=ltype,
            priv_expected=expected_privs,
        )
    else:
        lookup_privs = LookupUserPrivileges(email=token.get("user"))
    is_user_authorized = validate_user_access(lookup_privs)
    if not is_user_authorized:
        logger.error(f"user {token.get('user')} is not authorized to create a group")
        return False

    return True


def get_ns_from_db(name: str):
    db = get_db()
    ns_exists = db.AQLQuery(ARANGO_GET_NAMESPACE_BY_NAME, bindVars={"name": name})
    if ns_exists and len(ns_exists) > 0:
        return ns_exists[0]

    return


def does_app_exist(name: str):
    db = get_db()
    app_exists = db.AQLQuery(
        ARANGO_GET_USER_BY_EMAIL, rawResults=True, bindVars={"email": email}
    )
    if app_exists:
        return True

    return False