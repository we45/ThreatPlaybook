"""
ThreatPlaybook API Configurator

Usage:
    api_cli configure
    api_cli set (database|host|port)
    api_cli create-super-user [--email=<email>] [--password=<password]
    api_cli load-repo-db

Options:
    -h --help   Show this screen
    --version   Show version
    --email=<email>  Username for superuser
    --password=<password>  Password for superuser
"""

from docopt import docopt
from models import *
import ntpath
from glob import glob
import os
import yaml
from mongoengine import *
import getpass
from dotenv import load_dotenv, find_dotenv
from secrets import token_urlsafe
from utils import validation_dictionary, connect_db
from huepy import *
from argon2 import PasswordHasher

ph = PasswordHasher()
load_dotenv(find_dotenv())



def load_reload_repo_db():
    repo_path = os.path.join(os.path.abspath(os.path.curdir),'repo/')
    for single in glob(repo_path + "*.yaml"):
        single_name = ntpath.basename(single).split('.')[0]
        with open(single,'r') as rfile:
            rval = rfile.read()

        rcon = yaml.safe_load(rval)
        test_case_list = []
        test_case_load = rcon.get('test-cases', [])
        try:
            if test_case_load:
                for single in test_case_load:
                    new_test_case = RepoTestCase(name = single.get('name', ''), test_case = single.get('test', ''),
                                                 tools = single.get('tools', []), type = single.get('type', ''),
                                                 tags = single.get('tags', [])).save()
                    test_case_list.append(new_test_case.id)
            new_repo_object = Repo(short_name = single_name, name = rcon['name'],
                                   cwe = rcon['cwe'], description = rcon.get('description', ''),
                                   mitigations = rcon.get('mitigations', []), risks = rcon.get('mitigations', []),
                                   categories = rcon.get('categories', []), variants = rcon.get('variants', []),
                                   related_cwes = rcon.get('related_cwes', []), tests = test_case_list
                                   ).save()
        except Exception as e:
            print(e)

def configure_api():
    conf_dict = {}
    mongo_host = str(input("Please enter your MongoDB Host (eg: localhost,192.168.1.1): ") or "localhost")
    conf_dict['MONGO_HOST'] = mongo_host
    mongo_port = int(input("Please enter your MongoDB Port (eg. 27017). Default 27017") or 27017)
    conf_dict['MONGO_PORT'] = mongo_port
    mongo_user = input("Please enter mongo username: ")
    if not mongo_user:
        print(info("No information for mongo user. Will attempt to connect to Mongo without authentication"))
    else:
        conf_dict['MONGO_USER'] = mongo_user

    mongo_pass = getpass.getpass(prompt = "Please enter your password: ")
    if not mongo_pass and not mongo_user:
        print(info("No information for mongo user. Will attempt to connect to Mongo without authentication"))
    else:
        conf_dict['MONGO_PASS'] = mongo_pass

    mongo_db = str(input("Please enter the target mongo database name. Default is `threat_playbook`: ")
                   or "threat_playbook")
    conf_dict['MONGO_DB'] = mongo_db

    try:
        jwt_key = token_urlsafe(64)
        conf_dict['JWT_PASS'] = jwt_key
        print(good("Generated Random JWT Password successfully"))
    except Exception as e:
        print(bold(red(e)))
        exit(1)

    return conf_dict



if __name__ == '__main__':
    arguments = docopt(__doc__, version="ThreatPlaybook API Controller v 1.0")
    if os.path.isfile('.env'):
        load_dotenv()
    else:
        open('.env','a').close()
        load_dotenv(find_dotenv())
    if arguments.get('configure'):
        conf_dict = configure_api()
        if isinstance(conf_dict, dict):
            with open('.env', 'w') as envfile:
                for k,v in conf_dict.items():
                    envfile.write("{}={}\n".format(k,v))

        db = connect_db()
        print(db)
    if arguments.get('create-super-user'):
        db = connect_db()
        print(db)
        try:
            if arguments.get('--email'):
                email = arguments.get('--email')
            else:
                email = input("Please enter email: ")

            if arguments.get('--password'):
                password = arguments.get('--password')
            else:
                password = getpass.getpass(prompt='Enter Password: ')
                conf_pass = getpass.getpass(prompt='Confirm Password: ')
                if not password == conf_pass:
                    print(bold(red("Passwords don't match")))
                    exit(1)

            hash_pass = ph.hash(password)
            print(email, hash_pass, type(hash_pass))
            super_user = User(email = email, password = hash_pass).save()
            print(good("Superuser with email: {} created successfully".format(email)))
        except Exception as e:
            print(bold(red(e)))




