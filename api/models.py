from mongoengine import *
import datetime
from uuid import uuid4


def random_scan_name():
    return str(uuid4())


class Project(Document):
    name = StringField(max_length=100, required=True, unique=True)
    orchy_webhook = StringField(required=False)


class Interaction(Document):
    nature_choices = (("I", "Internal"), ("E", "External"))
    nature = StringField(choices=nature_choices)
    endpoint = StringField()
    data_flow = StringField()
    project = ReferenceField(Project, reverse_delete_rule=CASCADE)


class Test(Document):
    name = StringField()
    test_case = StringField()
    executed = BooleanField(default=False)
    tools = ListField(StringField())
    test_type = StringField()
    tags = ListField(StringField())


class RepoTestCase(Document):
    name = StringField()
    test_case = StringField()
    executed = BooleanField(default=False)
    tools = ListField(StringField())
    type = StringField(max_length=20)
    tags = ListField(StringField())


class Repo(Document):
    short_name = StringField(required=True)
    name = StringField(required=True)
    cwe = IntField(required=True)
    description = StringField()
    variants = ListField(StringField())
    categories = ListField(StringField())
    mitigations = ListField(DictField())
    risks = ListField(DictField())
    tests = ListField(ReferenceField(RepoTestCase))
    related_cwes = ListField(IntField())


class Risk(EmbeddedDocument):
    consequence = StringField()
    risk_type = StringField()


model_type_choices = (("repo", "repo"),
                      ("inline", "inline"))


class ThreatModel(Document):
    # meta = {'collection': 'threat_model'}
    name = StringField(max_length=200, unique=True)
    vul_name = StringField()
    description = StringField(required=True)
    severity = IntField()
    model_type = StringField(max_length=6, choices=model_type_choices)
    repo_vul_name = ReferenceField(Repo)
    project = ReferenceField(Project, reverse_delete_rule=CASCADE)
    tests = ListField(ReferenceField(Test))
    cwe = IntField()
    related_cwes = ListField(IntField(), null=True)
    categories = ListField(StringField(max_length=30))
    mitigations = ListField(DictField())
    # risks = EmbeddedDocumentListField(Risk)


class AbuseCase(Document):
    short_name = StringField(max_length=100, unique=True)
    description = StringField()
    project = ReferenceField(Project, reverse_delete_rule=CASCADE)
    models = ListField(ReferenceField(ThreatModel))


class UseCase(Document):
    short_name = StringField(max_length=100, unique=True)
    description = StringField()
    project = ReferenceField(Project, reverse_delete_rule=CASCADE)
    abuses = ListField(ReferenceField(AbuseCase))
    scenarios = ListField(ReferenceField(ThreatModel))
    relations = ListField(ReferenceField(Interaction))
    boundary = StringField()


class VulnerabilityEvidence(Document):
    name = StringField()
    log = StringField()
    url = StringField()
    param = StringField()
    attack = StringField()
    other_info = StringField()
    evidence = StringField()


class Vulnerability(Document):
    severity_choices = ((3, "High"), (2, "Medium"), (1, "Low"), (0, "Info"))
    tool = StringField()
    name = StringField()
    cwe = IntField()
    severity = IntField(choices=severity_choices)
    description = StringField()
    observation = StringField()
    remediation = StringField()
    evidences = ListField(ReferenceField(VulnerabilityEvidence))
    project = ReferenceField(Project, reverse_delete_rule=CASCADE)
    created_on = DateTimeField(default=datetime.datetime.utcnow)


class Scan(Document):
    created_on = DateTimeField(default=datetime.datetime.utcnow)
    name = StringField(default=random_scan_name)
    vulnerabilities = ListField(ReferenceField(Vulnerability))
    synced = BooleanField(default=False)


class Target(Document):
    name = StringField(unique=True)
    url = StringField()
    project = ReferenceField(Project, reverse_delete_rule=CASCADE)
    scans = ListField(ReferenceField(Scan))


class User(Document):
    user_type_choices = (('super', "superuser"), ('user', "user"))
    email = StringField(max_length=100, unique=True)
    password = StringField(max_length=100)
    user_type = StringField(choices=user_type_choices, max_length=6, default="user")
    default_password = BooleanField(default=True)


class Settings(Document):
    orchy_url = StringField()
    orchy_user = StringField()
    orchy_password = StringField()


class ASVS(Document):
    section = StringField()
    name = StringField()
    item = StringField()
    description = StringField()
    l1 = BooleanField(default=False)
    l2 = BooleanField(default=False)
    l3 = BooleanField(default=False)
    cwe = IntField()
    nist = StringField()
