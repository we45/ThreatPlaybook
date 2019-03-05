from schema import Schema, Regex
from mongoengine import *
from models import User
import os
from huepy import *
import jwt


jwt_pass = os.environ.get('JWT_PASS',None)

def _validate_jwt(http_headers):
    if not jwt_pass:
        raise Exception("JWT Password is not set. Cannot authenticate user to system")
    else:
        if 'authorization' in http_headers:
            try:
                validated = jwt.decode(http_headers['authorization'], key = jwt_pass, algorithms=['HS256'])
                print(validated)
                ref_user = User.objects.get(email = validated['email'])
                if ref_user.default_password == False:
                    return True
                else:
                    return False
            except DoesNotExist:
                return False
            except Exception:
                return False
        else:
            return False

def _validate_jwt_super(http_headers):
    if not jwt_pass:
        raise Exception("JWT Password is not set. Cannot authenticate user to system")
    else:
        if 'authorization' in http_headers:
            try:
                validated = jwt.decode(http_headers['authorization'], key = jwt_pass, algorithms=['HS256'])
                print(validated)
                ref_user = User.objects.get(email = validated['email'])
                if ref_user.default_password == False and ref_user.user_type == "super":
                    return True
                else:
                    return False
            except DoesNotExist:
                return False
            except Exception:
                return False
        else:
            return False


def connect_db():
    if not 'MONGO_USER' in os.environ:
        db = connect(os.environ['MONGO_DB'])
    else:
        try:
            db = connect(
                username = os.environ['MONGO_USER'],
                password = os.environ['MONGO_PASS'],
                host = os.environ['MONGO_HOST'],
                db = os.environ['MONGO_DB'],
                port = int(os.environ['MONGO_PORT'])
            )
        except Exception as e:
            print(bold(red(e)))
            exit(1)

    return db


validation_dictionary = {'create_user': {'email': Regex(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)",
                                                        error="Not a valid email"),
                                         'password': Regex(r'[A-Za-z0-9@#$%^&+=]{8,}',
                                                           error="Password is not compliant with requirements")
                                         },
                         'login': {
                             'email': Regex(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)",
                                            error="Not a valid email"),
                             'password': Regex(r'[A-Za-z0-9@#$%^&+=]{8,}',
                                               error="Password is not compliant with requirements")
                         }
                        }

