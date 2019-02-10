import responder
from models import *
import graphene
from gql import Query, ThreatPlaybookMutations
import json
import logging
from utils import validation_dictionary, connect_db
from schema import Schema, Regex, SchemaMissingKeyError
from argon2 import PasswordHasher
import jwt
import os

api = responder.API(cors = True, cors_params={
    "allow_origins": ['*'],
    "allow_methods": ["*"],
    "allow_headers": ["*"],
    "allow_credentials": True
})
ph = PasswordHasher()
logger = logging.getLogger(__name__)
handler = logging.FileHandler('api.log')

db = connect_db()

# GraphQL Views
schema = graphene.Schema(query=Query, mutation=ThreatPlaybookMutations)
view = responder.ext.GraphQLView(api = api, schema = schema)

async def _load_valid_data(req_content):
    try:
        content = json.loads(await req_content)
        return content
    except ValueError as encode_error:
        logger.error("_load_valid_data:error: {}".format(str(encode_error)))
        return {}

async def _validate(content, key):
    try:
        if key in validation_dictionary:
            validator = Schema(validation_dictionary[key])
            validated = validator.validate(content)
            return validated
        else:
            logger.error("_validate:Key {} reference is not present".format(key))
            return {'__error': 'no key present'}
    except SchemaMissingKeyError as missing:
        logger.error("_validate:{}".format(str(missing)))
        return {"__error": str(missing)}
    except Exception as generic:
        logger.error("_validate:{}".format(str(generic)))
        print(generic)
        return {"__error": str(generic)}


#Regular API Views
@api.route('/create-user')
async def create_user(req, resp):
    if req.method == 'post':
        valid_data = await _load_valid_data(req.content)
        if valid_data:
            validated_data = await _validate(valid_data, 'create_user')
            if '__error' in validated_data:
                resp.status_code = api.status_codes.HTTP_400
                resp.media = {'error': validated_data['error']}
                return resp
            else:
                hash_pass = ph.hash(validated_data['password'])
                User(email = validated_data['email'], password = hash_pass).save()
                resp.media = {'success': validated_data['email']}
                return resp
        else:
            resp.status_code = api.status_codes.HTTP_400
            resp.media = {'error': "Unable to parse JSON"}
            return resp
    else:
        resp.status_code = api.status_codes.HTTP_405
        resp.media = {"error": "Method not allowed"}
        return resp

@api.route('/login')
async def login(req, resp):
    if req.method == 'post':
        login_data = await _load_valid_data(req.content)
        if login_data:
            # validated = await _validate(login_data, 'login')
            # print(validated)
            # if '__error' in validated:
            #     resp.status_code = api.status_codes.HTTP_400
            #     resp.media = {'error': validated['error']}
            #     return resp
            # else:
            try:
                user_present = User.objects.get(email=login_data['email'])
                pass_verified = ph.verify(user_present.password, login_data['password'])
                if pass_verified:
                    token = jwt.encode({'email': user_present.email},key=os.environ['JWT_PASS'], algorithm="HS256").decode()
                    resp.media = {"success": "login", "token": token}
                    return resp

                else:
                    return {"error": "Invalid credentials"}
            except DoesNotExist as e:
                return {"error": "Invalid credentials"}

        else:
            resp.status_code = api.status_codes.HTTP_400
            resp.media = {'error': "Unable to parse JSON"}
            return resp
    else:
        resp.status_code = api.status_codes.HTTP_405
        resp.media = {"error": "Method not allowed"}
        return resp






#Additional Routes for API - GraphQL
api.add_route('/graph', view)



if __name__ == '__main__':
    api.run()
