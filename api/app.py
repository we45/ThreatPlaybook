import responder
from models import *
import graphene
from gql import Query, ThreatPlaybookMutations
import json
import logging
from utils import validation_dictionary, connect_db, _validate_jwt, _validate_jwt_super
from schema import Schema, Regex, SchemaMissingKeyError
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
import jwt
import os
from glob import glob
import ntpath
import yaml
from bson.json_util import dumps
from sys import exit

api = responder.API(cors=True, cors_params={
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
view = responder.ext.GraphQLView(api=api, schema=schema)


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


def load_reload_repo_db():
    if not Repo.objects:
        print("No Repo items found. Loading...")
        repo_path = os.path.join(os.path.abspath(os.path.curdir), 'repo/')
        for single in glob(repo_path + "*.yaml"):
            single_name = ntpath.basename(single).split('.')[0]
            with open(single, 'r') as rfile:
                rval = rfile.read()

            rcon = yaml.safe_load(rval)
            test_case_list = []
            test_case_load = rcon.get('test-cases', [])
            try:
                if test_case_load:
                    for single in test_case_load:
                        new_test_case = RepoTestCase(name=single.get('name', ''), test_case=single.get('test', ''),
                                                     tools=single.get('tools', []), type=single.get('type', ''),
                                                     tags=single.get('tags', [])).save()
                        test_case_list.append(new_test_case.id)
                new_repo_object = Repo(short_name=single_name, name=rcon['name'],
                                       cwe=rcon['cwe'], description=rcon.get('description', ''),
                                       mitigations=rcon.get('mitigations', []), risks=rcon.get('mitigations', []),
                                       categories=rcon.get('categories', []), variants=rcon.get('variants', []),
                                       related_cwes=rcon.get('related_cwes', []), tests=test_case_list
                                       ).save()
            except Exception as e:
                print(e)


def initialize_superuser():
    if not User.objects or not User.objects(user_type="super"):
        if not 'SUPERUSER_EMAIL' in os.environ:
            print("Mandatory variable SUPERUSER_EMAIL not present")
            exit(1)
        else:
            hash_pass = ph.hash("pl@yb00k1234")
            User(email=os.environ.get('SUPERUSER_EMAIL'), password=hash_pass, user_type="super").save()
            print("Initialized SuperUser with default password")


load_reload_repo_db()  # check if repos are not loaded, then loads them
initialize_superuser()  # adds superuser with default password if there's no superuser

# Regular API Views
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
                if _validate_jwt_super(req.headers):
                    hash_pass = ph.hash(validated_data['password'])
                    User(email=validated_data['email'], password=hash_pass).save()
                    resp.media = {'success': validated_data['email'],
                                  "message": "user will have to change password before using ThreatPlaybook"}
                    return resp
                else:
                    resp.status_code = api.status_codes.HTTP_403
                    resp.media = {'error': "Unauthorized to perform action"}
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
            try:
                user_present = User.objects.get(email=login_data['email'])
                pass_verified = ph.verify(user_present.password, login_data['password'])
                if pass_verified:
                    token = jwt.encode({'email': user_present.email}, key=os.environ.get('JWT_PASS', 'JbuLZIt2B2x4Iw'),
                                       algorithm="HS256").decode()
                    resp.media = {"success": "login", "token": token}
                    return resp

                else:
                    return {"error": "Invalid credentials"}
            except DoesNotExist as e:
                return {"error": "Invalid credentials"}
            except VerifyMismatchError as ve:
                resp.status_code = api.status_codes.HTTP_403
                resp.media = {'error': "Invalid credentials"}
                return resp

        else:
            resp.status_code = api.status_codes.HTTP_400
            resp.media = {'error': "Unable to parse JSON"}
            return resp
    else:
        resp.status_code = api.status_codes.HTTP_405
        resp.media = {"error": "Method not allowed"}
        return resp


@api.route('/change-password')
async def change_password(req, resp):
    if req.method == 'post':
        pass_data = await _load_valid_data(req.content)
        if pass_data:
            try:
                ref_user = User.objects.get(email=pass_data['email'])
                verify_pass = ph.verify(ref_user.password, pass_data['old_password'])
                if verify_pass and (pass_data['new_password'] == pass_data['verify_password']):
                    hash_pass = ph.hash(pass_data['new_password'])
                    ref_user.update(password=hash_pass, default_password=False)
                    resp.media = {'success': "Successfully changed password"}
                    return resp
                else:
                    resp.status_code = api.status_codes.HTTP_403
                    resp.media = {'error': "Failed Old Password Verify or Password mismatch"}
                    return resp
            except DoesNotExist:
                resp.status_code = api.status_codes.HTTP_403
                resp.media = {'error': "Invalid Credentials"}
                return resp
            except Exception:
                resp.status_code = api.status_codes.HTTP_403
                resp.media = {'error': "Invalid Credentials"}
                return resp
        else:
            resp.status_code = api.status_codes.HTTP_400
            resp.media = {'error': "Unable to parse JSON"}
            return resp

@api.route('/feature-by-cwe/{cwe}')
def get_story_by_cwe(req, resp, *, cwe):
    if req.method == 'post':
        if _validate_jwt(req.headers):
            cwe = int(cwe)
            pipeline = [{"$match": {"cwe": cwe}}, {
                "$lookup": {"from": "abuse_case", "localField": "_id", "foreignField": "models",
                            "as": "abuses_model"}}, {"$lookup": {"from": "use_case", "localField": "_id",
                                                           "foreignField": "scenarios", "as": "usecases_model"}},
                        {"$lookup": {"from": "project", "localField": "project",
                                     "foreignField": "_id", "as": "project_model"}},
                        ]
            cwe_list = json.loads(dumps(list(ThreatModel.objects.aggregate(*pipeline))))
            resp.media = cwe_list
            return resp
        else:
            resp.status_code = api.status_codes.HTTP_403
            resp.media = {'error': "Unauthorized to perform action"}
            return resp




# Additional Routes for API - GraphQL
api.add_route('/graph', view)
api.add_route('/', static=True)

if __name__ == '__main__':
    api.run(address='0.0.0.0')
