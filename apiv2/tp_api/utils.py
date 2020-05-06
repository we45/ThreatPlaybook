from mongoengine import *
from loguru import logger
from sys import exit
import os
from models import *
from glob import glob
import ntpath
import yaml
import bcrypt
import csv
from flask import jsonify

logger.add("logs/output.log", backtrace=True, diagnose=True)


def respond(success, error, message="", data=None):
    respond_dict = {
        "success": success,
        "error": error,
    }
    if message:
        respond_dict["message"] = message

    if data:
        respond_dict["data"] = data

    return jsonify(respond_dict)


def connect_db():
    if "MONGO_USER" not in os.environ:
        db = connect(os.environ.get("MONGO_DB", "threat_playbook"))
    else:
        try:
            db = connect(
                username=os.environ.get("MONGO_USER"),
                password=os.environ.get("MONGO_PASS"),
                host=os.environ.get("MONGO_HOST", "127.0.0.1"),
                db=os.environ.get("MONGO_DB", "threat_playbook"),
                port=int(os.environ.get("MONGO_PORT", 27017)),
            )
        except Exception as e:
            logger.exception(e)
            print("Unable to connect to Database. Please see log for exception")
            exit(1)

    return db


def load_reload_asvs_db():
    if not ASVS.objects:
        asvs_file = os.path.join(os.path.abspath(os.path.curdir), "asvs/asvs.csv")
        if os.path.isfile(asvs_file):
            with open(asvs_file, "rt") as asvs_file:
                data = csv.reader(asvs_file)
                for row in data:
                    cwe = row[7]
                    if not cwe:
                        cwe = 0
                    else:
                        cwe = int(row[7])
                    new_item = ASVS(
                        section=row[0],
                        name=row[1],
                        item=row[2],
                        description=row[3],
                        l1=row[4] or False,
                        l2=row[5] or False,
                        l3=row[6] or False,
                        cwe=cwe,
                        nist=row[8] or "",
                    ).save()


def load_reload_repo_db():
    if not Repo.objects:
        print("No Repo items found. Loading...")
        repo_path = os.path.join(os.path.abspath(os.path.curdir), "repo/")
        for single in glob(repo_path + "*.yaml"):
            single_name = ntpath.basename(single).split(".")[0]
            with open(single, "r") as rfile:
                rval = rfile.read()

            rcon = yaml.safe_load(rval)
            test_case_list = []
            test_case_load = rcon.get("test-cases", [])
            try:
                if test_case_load:
                    for single in test_case_load:
                        new_test_case = RepoTestCase(
                            name=single.get("name", ""),
                            test_case=single.get("test", ""),
                            tools=single.get("tools", []),
                            type=single.get("type", ""),
                            tags=single.get("tags", []),
                        ).save()
                        test_case_list.append(new_test_case.id)
                new_repo_object = Repo(
                    short_name=single_name,
                    name=rcon["name"],
                    cwe=rcon["cwe"],
                    description=rcon.get("description", ""),
                    mitigations=rcon.get("mitigations", []),
                    risks=rcon.get("mitigations", []),
                    categories=rcon.get("categories", []),
                    variants=rcon.get("variants", []),
                    related_cwes=rcon.get("related_cwes", []),
                    tests=test_case_list,
                ).save()
            except Exception as e:
                logger.exception(e)
                print("Unable to load Repo Objects. Please see log")


def initialize_superuser():
    if not User.objects or not User.objects(user_type="super"):
        if "SUPERUSER_EMAIL" not in os.environ:
            print("Mandatory variable SUPERUSER_EMAIL not present")
            exit(1)
        else:
            admin_pass = os.environ.get("SUPERUSER_PASS", "pl@yb00k1234")
            hash_pass = bcrypt.hashpw(admin_pass.encode(), bcrypt.gensalt()).decode()
            User(
                email=os.environ.get("SUPERUSER_EMAIL"),
                password=hash_pass,
                user_type="super",
            ).save()
            print("Initialized SuperUser with default password")
