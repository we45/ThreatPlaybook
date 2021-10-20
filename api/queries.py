# this source file contains AQL/c8QL Queries which we'll use to perform queries against the database

ARANGO_INSERT_USER = 'let createdDate = DATE_NOW() INSERT {"email": @email, "password": @password, "created_on": createdDate} into user RETURN NEW'

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

ARANGO_CREATE_NAMESPACE = (
    'let createdDate = DATE_NOW() '
    'INSERT {"name": @name, "description": @description, "created_on": createdDate} into namespace '
    'RETURN NEW'
)

ARANGO_LIST_NAMESPACES = (
    "FOR single in namespace "
    "RETURN single"
)

ARANGO_UPDATE_NAMESPACE = (
    "FOR ns in namespace "
    "FILTER ns._key == @key "
    "UPDATE {_key: ns._key} WITH {name: @name, description: @description} IN namespace "
    "RETURN NEW"
)

ARANGO_DELETE_NAMESPACE = (
    "FOR ns in namespace "
    "FILTER ns.name == @name "
    "REMOVE ns IN namespace")

ARANGO_GET_NAMESPACE_BY_NAME = (
    "FOR single in namespace "
    "FILTER single.name == @namespace "
    "RETURN single"
)

ARANGO_GET_NAMESPACE_BY_KEY = (
    "FOR single in namespace "
    "FILTER single._key == @key "
    "RETURN single"
)

ARANGO_LOOKUP_USER_PRIVS = 'FOR single in user FILTER single.email == @email FOR v,e,p in 1..@depth OUTBOUND single edges RETURN {"vertex": v, "edges": e}'

ARANGO_CREATE_APP = (
    'LET createdDate = DATE_NOW() '
    'INSERT {"name": @name, "description": @description, "app_type": @app_type, "hosting": @hosting, "compute": @compute, "technologies": @technologies, "created_on": createdDate} INTO application '
    'RETURN NEW'
)

ARANGO_EDGE_APP_NAMESPACE = (
    'FOR appNS in [{"_from": @application_id, "_to": @namespace_id}, {"_from": @namespace_id, "_to": @application_id}] '
    'INSERT appNS INTO edges '
    'RETURN NEW'
)

ARANGO_GET_ALL_APPLICATIONS_UNDER_NAMESPACE = (
    "FOR single in namespace "
    "FILTER single.name == @namespace "
    "FOR app in 1..1 OUTBOUND single edges "
    "RETURN app"
)

ARANGO_GET_APPLICATION_BY_KEY = (
    "FOR app in application "
    "FILTER app._key == @key "
    "RETURN app"
)

ARANGO_UPDATE_APPLICATION = (
    "FOR app in application "
    "FILTER app._key == @key "
    "UPDATE {_key: app._key} WITH {name: @name, description: @description, app_type: @app_type, hosting: @hosting, compute: @compute, technologies: @technologies} IN application "
    "RETURN NEW"
)

ARANGO_CREATE_APPLICATION = [
    'let createdDate = DATE_NOW() INSERT {"name": @name, "description": @description, "app_type: @app_type, "hosting: @hosting, "compute: @compute, "created_on": createdDate',
    '} into application LET inserted = NEW FOR appNS in [{"_from": inserted._id, "_to": @nsKey}, {"_from": @nsKey, "_to": inserted._id}] INSERT appNS INTO edges'
]

ARANGO_GET_APPLICATION_BY_NAME = "FOR single in application FILTER single.name == @name RETURN single"

ARANGO_CREATE_USER_STORY = 'let createdDate = DATE_NOW() INSERT {"name": @name, "description": @description, stride: @stride, "created_on": createdDate } into user_story LET inserted = NEW FOR usApp in [{"_from": inserted._id, "_to": @appKey}, {"_from": @appKey, "_to": inserted._id}] INSERT usApp INTO edges'

ARANGO_UPDATE_USER_STORY = 'FOR single in user_story FILTER single._key == @singleKey UPDATE {_key: single._key} WITH {name: @name, description: @description, stride: @stride} IN user_story RETURN NEW'