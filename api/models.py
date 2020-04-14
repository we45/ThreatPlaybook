from mongoengine import *
import datetime
from uuid import uuid4
from hashlib import sha256
from mongoengine import signals


def random_scan_name():
    return str(uuid4())


class Project(Document):
    name = StringField(max_length=100, required=True, unique=True)
    orchy_webhook = StringField(required=False)
    features = ListField(ReferenceField('UseCase'))


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


class Interaction(Document):
    nature_choices = (("I", "Internal"), ("E", "External"))
    nature = StringField(choices=nature_choices)
    endpoint = StringField()
    data_flow = StringField()
    project = ReferenceField(Project, reverse_delete_rule=CASCADE)


class UseCase(Document):
    short_name = StringField()
    description = StringField()
    project = ReferenceField(Project, reverse_delete_rule=CASCADE, required=True)
    hash = StringField(unique=True)
    relations = ListField(ReferenceField(Interaction))
    boundary = StringField()
    abuses = ListField(ReferenceField('AbuseCase'))

    @classmethod
    def pre_save(cls, sender, document, **kwargs):
        print(document.project.name)
        document.hash = sha256(
            "${}${}".format(document.short_name, document.project.name).encode()
        ).hexdigest()


class AbuseCase(Document):
    short_name = StringField(max_length=100, unique=True)
    description = StringField()
    use_case = ReferenceField(UseCase, reverse_delete_rule=CASCADE, required=True)
    hash = StringField()
    scenarios = ListField(ReferenceField('ThreatModel'))

    @classmethod
    def pre_save(cls, sender, document, **kwargs):
        document.hash = sha256(
            "${}${}".format(document.short_name, document.use_case.short_name).encode()
        ).hexdigest()


model_type_choices = (("repo", "repo"), ("inline", "inline"))


class ThreatModel(Document):
    # meta = {'collection': 'threat_model'}
    name = StringField()
    vul_name = StringField()
    description = StringField(required=True)
    severity = IntField()
    model_type = StringField(max_length=6, choices=model_type_choices)
    repo_vul_name = ReferenceField(Repo)
    use_case = ReferenceField(UseCase, reverse_delete_rule=CASCADE)
    abuse_case = ReferenceField(AbuseCase, reverse_delete_rule=CASCADE)
    cwe = IntField()
    related_cwes = ListField(IntField(), null=True)
    categories = ListField(StringField(max_length=30))
    mitigations = ListField(DictField())
    hash = StringField(unique=True)
    entry_source = StringField(
        max_length=10,
        choices=(("automated", "automated"), ("manual", "manual")),
        default="automated",
    )
    tests = ListField(ReferenceField('Test'))

    @classmethod
    def pre_save(cls, sender, document, **kwargs):
        document.hash = sha256(
            "${}${}${}".format(
                document.name,
                document.use_case.short_name,
                document.abuse_case.short_name,
            ).encode()
        ).hexdigest()


class Test(Document):
    name = StringField()
    test_case = StringField()
    executed = BooleanField(default=False)
    tools = ListField(StringField())
    test_type = StringField()
    tags = ListField(StringField())
    scenario = ReferenceField(ThreatModel, reverse_delete_rule=CASCADE)

    


class Risk(EmbeddedDocument):
    consequence = StringField()
    risk_type = StringField()


class VulnerabilityEvidence(Document):
    name = StringField()
    log = StringField()
    url = StringField()
    param = StringField()
    attack = StringField()
    other_info = StringField()
    evidence = StringField()
    hash = StringField(unique=True)
    vuln = ReferenceField('Vulnerability')

    @classmethod
    def pre_save(cls, sender, document, **kwargs):
        document.hash = sha256(
            "${}${}".format(
                document.name,
                document.vuln.name
            ).encode()
        ).hexdigest()


class Vulnerability(Document):
    severity_choices = ((3, "High"), (2, "Medium"), (1, "Low"), (0, "Info"))
    tool = StringField()
    name = StringField(unique = True)
    cwe = IntField()
    severity = IntField(choices=severity_choices)
    description = StringField()
    observation = StringField()
    remediation = StringField()
    evidences = ListField(ReferenceField(VulnerabilityEvidence))
    project = ReferenceField(Project, reverse_delete_rule=CASCADE)
    created_on = DateTimeField(default=datetime.datetime.utcnow)
    scan = ReferenceField('Scan')
    target = ReferenceField("Target")
    scenarios = ListField(ReferenceField('ThreatModel'))

class Scan(Document):
    created_on = DateTimeField(default=datetime.datetime.utcnow)
    name = StringField(default=random_scan_name)
    vulnerabilities = ListField(ReferenceField('Vulnerability'))
    synced = BooleanField(default=False)


class Target(Document):
    name = StringField(unique=True)
    url = StringField()
    project = ReferenceField(Project, reverse_delete_rule=CASCADE)
    scans = ListField(ReferenceField(Scan))


class User(Document):
    user_type_choices = (("super", "superuser"), ("user", "user"))
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


## signals
signals.pre_save.connect(UseCase.pre_save, sender=UseCase)
signals.pre_save.connect(AbuseCase.pre_save, sender=AbuseCase)
signals.pre_save.connect(ThreatModel.pre_save, sender=ThreatModel)
signals.pre_save.connect(VulnerabilityEvidence.pre_save, sender = VulnerabilityEvidence)