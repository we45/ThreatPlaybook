from mongoengine import *
import datetime
import uuid

class Project(Document):
    name = StringField(max_length=100, required = True, unique=True)

class Session(Document):
    name = StringField()
    project = ReferenceField(Project, reverse_delete_rule=CASCADE)

class Entity(Document):
    # name = StringField(max_length=50)
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

class TestCase(Document):
    TEST_TYPES = (('M', "Manual"), ("A", "Automated"), ('R', "Recon"))
    short_name = StringField(unique=True)
    description = StringField()
    executed = BooleanField(default = False)
    case_type = StringField(max_length=10, choices = TEST_TYPES)
    tags = ListField()


class ThreatModel(Document):
    name = StringField(max_length=200, required=True, unique = True)
    description = StringField(required = True)
    #dread = ListField()
    severity = IntField()
    project = ReferenceField(Project, reverse_delete_rule=CASCADE)
    cases = ListField(ReferenceField(TestCase))
    cwe = ListField()

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
    models = ListField(ReferenceField(ThreatModel))

class Target(Document):
    name = StringField(unique=True)
    url = StringField()
    project = ReferenceField(Project, reverse_delete_rule=CASCADE)

class Recon(Document):
    tool = StringField(max_length=100)
    options = StringField(max_length=100)
    created_on = DateTimeField(default=datetime.datetime.utcnow)
    result = StringField()
    cases = ListField(ReferenceField(TestCase))
    session = ReferenceField(Session)
    target = ReferenceField(Target)

class VulnerabilityEvidence(EmbeddedDocument):
    name = StringField(max_length=100)
    log = StringField()
    data = StringField()
    url = StringField()
    param = StringField(max_length=100)
    attack = StringField()
    evidence = StringField()
    other_info = StringField()

class Vulnerability(Document):
    severity_choices = ((3, "High"), (2, "Medium"), (1, "Low"), (0, "Info"))
    tool = StringField(max_length=100)
    name = StringField(max_length=100)
    cwe = IntField()
    severity = IntField(choices=severity_choices)
    description = StringField()
    observation = StringField()
    remediation = StringField()
    evidences = EmbeddedDocumentListField(VulnerabilityEvidence)
    models = ListField(ReferenceField(ThreatModel))
    cases = ListField(ReferenceField(TestCase))
    session = ReferenceField(Session)
    target = ReferenceField(Target)

