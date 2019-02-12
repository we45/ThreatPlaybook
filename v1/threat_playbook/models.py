from mongoengine import *
import datetime


class Project(Document):
    name = StringField(max_length=100, required = True, unique=True)


class Session(Document):
    created_on = DateTimeField(default=datetime.datetime.utcnow)
    project = ReferenceField(Project, reverse_delete_rule=CASCADE)


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

class TestCase(EmbeddedDocument):
    name = StringField(unique=True)
    test = StringField()
    executed = BooleanField(default = False)
    tools = ListField()
    type = StringField(max_length=20)
    tags = ListField()

class Risk(EmbeddedDocument):
    consequence = StringField()
    risk_type = StringField()

class ThreatModel(Document):
    name = StringField(max_length=200, required=True, unique = True)
    vul_name = StringField()
    description = StringField(required = True)
    severity = IntField()
    project = ReferenceField(Project, reverse_delete_rule=CASCADE)
    cases = EmbeddedDocumentListField(TestCase)
    cwe = IntField()
    related_cwes = ListField(IntField(), null=True)
    categories = ListField(StringField(max_length=30))
    mitigations = ListField()
    risks = EmbeddedDocumentListField(Risk)


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
    models = ListField(ReferenceField(ThreatModel))
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
    session = ReferenceField(Session)
    target = ReferenceField(Target)
