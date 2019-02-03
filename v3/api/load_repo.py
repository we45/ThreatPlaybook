from models import *
import ntpath
from glob import glob
import os
import yaml
from mongoengine import *

connect('threat_playbook')

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

load_reload_repo_db()