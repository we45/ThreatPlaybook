from mongoengine import *
import datetime
import namesgenerator
from uuid import uuid4

def random_scan_name():
    return "{}-{}".format(namesgenerator.get_random_name(sep="-"), str(uuid4()))

class Project(Document):
    name = StringField(max_length=100, required = True, unique=True)

    # class Session(Document):
#     created_on = DateTimeField(default=datetime.datetime.utcnow)
#     project = ReferenceField(Project, reverse_delete_rule=CASCADE)


class Entity(Document):
    short = StringField(max_length=50, unique = True)
    shape = StringField(max_length=50)
    description = StringField()
    caption = StringField()
    project = ReferenceField(Project, reverse_delete_rule=CASCADE)


class EntityMapping(Document):
    start = ReferenceField(Entity)
    end = ReferenceField(Entity)
    link_text = StringField(max_length=50)
    subgraph = StringField(max_length=30)
    project = ReferenceField(Project, reverse_delete_rule=CASCADE)

class Test(Document):
    name = StringField()
    test_case = StringField()
    executed = BooleanField(default = False)
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
    short_name = StringField(required = True)
    name = StringField(required = True)
    cwe = IntField(required = True)
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
    description = StringField(required = True)
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

class Target(Document):
    name = StringField(unique=True)
    url = StringField()
    project = ReferenceField(Project, reverse_delete_rule=CASCADE)


class Recon(Document):
    tool = StringField(max_length=100)
    options = StringField(max_length=100)
    created_on = DateTimeField(default=datetime.datetime.utcnow)
    result = StringField()
    models = ListField(ReferenceField(ThreatModel))
    target = ReferenceField(Target)


class VulnerabilityEvidence(Document):
    name = StringField(max_length=100)
    log = StringField()
    url = StringField()
    param = StringField(max_length=100)
    attack = StringField()
    other_info = StringField()
    evidence = StringField()


class Vulnerability(Document):
    severity_choices = ((3, "High"), (2, "Medium"), (1, "Low"), (0, "Info"))
    tool = StringField(max_length=100)
    name = StringField(max_length=100)
    cwe = IntField()
    severity = IntField(choices=severity_choices)
    description = StringField()
    observation = StringField()
    remediation = StringField()
    evidences = ListField(ReferenceField(VulnerabilityEvidence))
    project = ReferenceField(Project)
    target = ReferenceField(Target)
    created_on = DateTimeField(default=datetime.datetime.utcnow)


class Scan(Document):
    created_on = DateTimeField(default=datetime.datetime.utcnow)
    name = StringField(default = random_scan_name)
    target = ReferenceField(Target)
    vulnerabilities = ListField(ReferenceField(Vulnerability))

class User(Document):
    user_type_choices = (('super', "superuser"), ('user', "user"))
    email = StringField(max_length=100, unique=True)
    password = StringField(max_length=100)
    user_type = StringField(choices=user_type_choices, max_length=6, default = "user")

