# this is the entrypoint for the API
# Author: Abhay Bhargav

from types import BuiltinMethodType
from fastapi import FastAPI, Request
from fastapi.param_functions import Depends
from fastapi.responses import JSONResponse
from pydantic.schema import TypeModelOrEnum
from pydantic.utils import is_valid_field
from models import *
from utils import *
from loguru import logger
from queries import *
import bcrypt
import jwt
import json


myapp = FastAPI()  # initialize app
logger.add("api.log", enqueue=True)  # initialize log


@myapp.on_event("startup")
def startup_event():
    init_db()


# user CRUD
@myapp.put("/user/create")
def create_user(user: User):
    """
    creates a user based on the UserModel. User needs the following elements to become a user
    - email
    - password
    """
    try:
        create_user_in_db(user)
        logger.info(f"user {user.email} created")
        return {
            "success": True,
            "error": False,
            "message": f"user {user.email} successfully created",
        }
    except DuplicateUserException:
        logger.error(f"user {user.email} already exists")
        return {
            "success": False,
            "error": True,
            "message": f"user {user.email} already exists",
        }
    except Exception as e:
        logger.error(e.message)
        return {"success": False, "error": True, "message": "Unable to create user"}


@myapp.post("/user/login")
def login_user(user: OpsUser):
    """
    authenticates the user, when they provide an email and password.
    Returns a JWT with the `token` in the `data` key of the json object returned
    """
    try:
        q_user = db.AQLQuery(ARANGO_GET_USER_BY_EMAIL, bindVars={"email": user.email})
        if not q_user and not len(q_user) > 0:
            logger.error(f"Unable to find user {user.email} in the database")
            return JSONResponse(
                status_code=400,
                content={
                    "success": False,
                    "error": True,
                    "message": "email or password is incorrect",
                },
            )
        is_password_valid = bcrypt.checkpw(
            str(user.password).encode(), q_user[0].password.encode()
        )
        if not is_password_valid:
            logger.error(f"Authentication for user {user.email} failed")
            return JSONResponse(
                status_code=400,
                content={
                    "success": False,
                    "error": True,
                    "message": "email or password is incorrect",
                },
            )

        token = jwt.encode(
            {"user": user.email, "role": q_user[0].role}, JWT_PASS, algorithm="HS256"
        )
        return {
            "success": True,
            "error": False,
            "data": {"user": user.email, "token": token},
        }
    except Exception as e:
        logger.error(e)
        return JSONResponse(
            status_code=400,
            content={"success": False, "error": True, "message": "login error"},
        )


@myapp.put("/group/create")
def create_group(gc: GroupCreate, r: Request):
    if not check_user_access_and_privs(r):
        return JSONResponse(
            status_code=403,
            content={"success": False, "error": True, "message": "Unauthorized access"},
        )
    try:
        group_create = db.AQLQuery(
            ARANGO_CREATE_GROUP,
            rawResults=True,
            bindVars={"name": gc.name, "description": gc.description},
        )
        return {
            "success": True,
            "error": False,
            "message": f"group {gc.name} successfully created",
        }
    except Exception as e:
        logger.error(e)
        return JSONResponse(
            status_code=400,
            content={
                "success": False,
                "error": True,
                "message": "Unable to create group",
            },
        )


@myapp.post("/group/assign")
def assign_user_group(ga: UserGroupAssignment, r: Request):
    if not check_user_access_and_privs(r):
        return JSONResponse(
            status_code=403,
            content={"success": False, "error": True, "message": "Unauthorized access"},
        )
    assignment = assign_user_to_group(ga)
    if assignment:
        logger.info(f"user {ga.email} assigned to {ga.group_name}")
        return {
            "success": True,
            "error": False,
            "message": f"user {ga.email} assigned to {ga.group_name}",
        }
    else:
        logger.error(f"Unable to assign {ga.email} to {ga.group_name}")
        return JSONResponse(
            status_code=400,
            content={
                "success": False,
                "error": True,
                "message": f"Unable to assign {ga.email} to {ga.group_name}",
            },
        )


# namespace CRUD
@myapp.put("/namespace/create")
def create_namespace(ns: Namespace, request: Request):
    """
    creates a namespace. this can only be invoked by an admin level user
    """
    if not check_user_access_and_privs(request):
        return JSONResponse(
            status_code=403,
            content={"success": False, "error": True, "message": "Unauthorized access"},
        )
    db = get_db()
    response = db.AQLQuery(
        ARANGO_CREATE_NAMESPACE,
        bindVars={"name": ns.name, "description": ns.description},
    )
    if response and len(response) > 0:
        logger.info(f"namespace {ns.name} has been successfully created")
        return {
            "success": True,
            "error": False,
            "message": f"namespace {ns.name} has been successfully created",
        }


@myapp.get("/namespace/list")
def list_namespaces(request: Request):
    """
    list all namespaces
    TODO:
    1. Pagination
    """
    if not check_user_access_and_privs(request):
        return JSONResponse(
            status_code=403,
            content={"success": False, "error": True, "message": "Unauthorized access"},
        )
    db = get_db()
    all_ns = db.AQLQuery(ARANGO_LIST_NAMESPACES, rawResults=True)
    if not all_ns:
        return JSONResponse(status_code=404)
    ns_list = []
    for single in all_ns:
        ns_list.append(single)
    return {"success": True, "error": False, "data": ns_list}


@myapp.post("/namespace/get")
def get_namespace(ns: NamespaceGet, request: Request):
    if not check_user_access_and_privs(request):
        return JSONResponse(
            status_code=403,
            content={"success": False, "error": True, "message": "Unauthorized access"},
        )
    db = get_db()
    q_ns = db.AQLQuery(
        ARANGO_GET_NAMESPACE_BY_NAME, rawResults=True, bindVars={"name": ns.name}
    )
    if not q_ns and len(q_ns) == 0:
        return JSONResponse(status_code=404)

    return {"success": True, "error": False, "data": q_ns[0]}


@myapp.post("/namespace/assign")
def assign_namespace_group(ns: NamespaceGroupAssignment, r: Request):
    if not check_user_access_and_privs(r):
        return JSONResponse(
            status_code=403,
            content={"success": False, "error": True, "message": "Unauthorized access"},
        )
    group_assign = assign_group_to_ns(ns)
    if group_assign:
        logger.info(
            f"group {ns.group_name} successfully assigned to {ns.ns_name} with {ns.privs}"
        )
        return {
            "success": True,
            "error": False,
            "message": f"group {ns.group_name} successfully assigned to {ns.ns_name} with {ns.privs}",
        }
    else:
        logger.error(f"Unable to assign group {ns.group_name} to {ns.ns_name}")
        return JSONResponse(
            status_code=400,
            content={
                "success": False,
                "error": True,
                "message": "Unable to complete group assignment",
            },
        )


# @myapp.put("/application/create")
# def create_application(apc: ApplicationCreate, r: Request):
#     if not check_user_access_and_privs(r, apc.namespace, "namepace", "write"):
#         return JSONResponse(
#             status_code=403,
#             content={"success": False, "error": True, "message": "Unauthorized access"},
#         )
    
#     if not does_namespace_exist(apc.namespace):
#         logger.error(f"namespace '{apc.namespace}' doesn't exist")
#         return JSONResponse(status_code=404, content = {
#             "success": False,
#             "error": True,
#             "message": f"namespace '{apc.namespace}' doesn't exist"
#         })
    
#     if apc.technologies:
#         ARANGO_CREATE_APPLICATION.insert(1, ', "technologies": @technologies')
#         create_app_query = ''.join(ARANGO_CREATE_APPLICATION)
#         db = get_db()
#         try:
#             db.AQLQuery(create_app_query, rawResults = True, bindVars = {
#                 "name": apc.name,
#                 "nsKey": get_ns_from_db(apc.namespace).get('_id'),
#                 "compute": apc.compute,
#                 "hosting": apc.hosting,
#                 "app_type": apc.app_type,
#                 "technologies": apc.technologies,
#             })
#         except Exception as e:
            

#     else:
#         create_app_query = ''.join(ARANGO_CREATE_APPLICATION)
#         db = get_db()
#         db.AQLQuery(create_app_query, rawResults = True, bindVars = {
#             "name": apc.name,
#             "nsKey": get_ns_from_db(apc.namespace).get('_id'),
#             "compute": apc.compute,
#             "hosting": apc.hosting,
#             "app_type": apc.app_type,
#         })
