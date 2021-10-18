# this source file contains AQL/c8QL Queries which we'll use to perform queries against the database

ARANGO_INSERT_USER = 'let createdDate = DATE_NOW() INSERT {"email": @email, "password": @password, "role": @role, "created_on": createdDate} into user RETURN NEW'

ARANGO_GET_USER_BY_EMAIL = (
    "FOR single in user FILTER single.email == @email RETURN single"
)

ARANGO_VALIDATE_USER_ROLE = "FOR single in user FILTER single.email == @email && single.role == @role RETURN single"

ARANGO_GET_USER_NS = "FOR single in user FILTER user.email == @email"

ARANGO_CREATE_GROUP = 'let createdDate = DATE_NOW() INSERT {"name": @name, "description": @description, "created_on": createdDate} into group RETURN NEW'

ARANGO_GET_GROUP_BY_NAME = (
    "FOR single in group FILTER single.name == @name RETURN single"
)

ARANGO_ASSIGN_USER_TO_GROUP = 'FOR userGroups in [{"_from": @userKey, "_to": @groupKey}, {"_from": @groupKey, "_to": @userKey}] INSERT userGroups INTO edges'

ARANGO_ASSIGN_GROUP_NAMESPACE = 'FOR groupNs in [{"_from": @groupKey, "_to": @nsKey, "privs": @privs}, {"_from": @nsKey, "_to": @groupKey, "privs": @privs}] INSERT groupNs INTO edges'

ARANGO_CREATE_NAMESPACE = 'let createdDate = DATE_NOW() INSERT {"name": @name, "description": @description, "created_on": createdDate} into namespace RETURN NEW'

ARANGO_LIST_NAMESPACES = "FOR single in namespace RETURN single"

ARANGO_GET_NAMESPACE_BY_NAME = (
    "FOR single in namespace FILTER single.name == @name RETURN single"
)

ARANGO_LOOKUP_USER_PRIVS = 'FOR single in user FILTER single.email == @email FOR v,e,p in 1..@depth OUTBOUND single edges RETURN {"vertex": v, "edges": e}'

ARANGO_CREATE_APPLICATION = [
    'let createdDate = DATE_NOW() INSERT {"name": @name, "description": @description, "app_type: @app_type, "hosting: @hosting, "compute: @compute, "created_on": createdDate',
    '} into namespace LET inserted = NEW FOR appNS in [{"_from": inserted._id, "_to": @nsKey}, {"_from": @nsKey, "_to": inserted._id}] INSERT appNS INTO edges'
]

ARANGO_GET_APPLICATION_BY_NAME = "FOR single in application FILTER single.name == @name RETURN single"