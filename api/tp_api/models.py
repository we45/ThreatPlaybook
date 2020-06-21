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
    features = ListField(ReferenceField("UseCase"), required=False)


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
    short_name = StringField(unique=True)
    description = StringField()
    project = ReferenceField(Project, reverse_delete_rule=CASCADE, required=True)
    relations = ListField(ReferenceField(Interaction))
    boundary = StringField()
    abuses = ListField(ReferenceField("AbuseCase"))


class AbuseCase(Document):
    short_name = StringField(max_length=100, unique=True)
    description = StringField()
    use_case = ReferenceField(UseCase, reverse_delete_rule=CASCADE, required=True)
    scenarios = ListField(ReferenceField("ThreatModel"), required=False)


model_type_choices = (("repo", "repo"), ("inline", "inline"))


class Mitigations(EmbeddedDocument):
    phase = StringField()
    strategy = StringField()
    description = StringField()
    code = StringField()


class Risk(EmbeddedDocument):
    description = StringField()
    phase = StringField()


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
    risks = EmbeddedDocumentListField(Risk)
    categories = ListField(StringField(max_length=30))
    mitigations = EmbeddedDocumentListField(Mitigations)
    tests = ListField(ReferenceField("Test"))


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
    evidence_type = StringField()
    log = StringField()
    url = StringField()
    line_num = IntField()
    param = StringField()
    attack = StringField()
    info = StringField()
    vuln = ReferenceField("Vulnerability")


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
    created_on = DateTimeField(default=datetime.datetime.utcnow)
    scan = ReferenceField("Scan")
    target = ReferenceField("Target")


class Scan(Document):
    created_on = DateTimeField(default=datetime.datetime.utcnow)
    name = StringField(unique=True)
    vulnerabilities = ListField(ReferenceField("Vulnerability"))
    target = ReferenceField("Target")
    tool = StringField()
    scan_type = StringField(
        choices=(
            ("SAST", "Static Analysis"),
            ("DAST", "Dynamic Analysis"),
            ("SCA", "Source Composition Analysis"),
            ("IAST", "Interactive Analysis"),
            ("Manual", "Manual Scan"),
        )
    )

    @classmethod
    def pre_save(cls, sender, document, **kwargs):
        document.name = "{}-scan-{}-{}@{}".format(
            document.tool,
            document.target.name,
            document.target.project.name,
            datetime.datetime.utcnow().isoformat(),
        )


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


signals.pre_save.connect(Scan.pre_save, sender = Scan)