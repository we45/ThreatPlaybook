from datetime import datetime
from typing import Dict, List, Optional
from pydantic import BaseModel, Field, validator, PrivateAttr
from enum import Enum
from pydantic.networks import EmailStr
from pydantic.dataclasses import dataclass
import bcrypt


class User(BaseModel):
    email: EmailStr
    password: str
    @validator("password", pre=True)
    def hash_password(cls, v):
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(v.encode(), salt).decode()


class GroupCreate(BaseModel):
    name: str
    description: str


class UserGroupAssignment(BaseModel):
    email: EmailStr
    group_name: str


class NamespaceGroupAssignment(BaseModel):
    group_name: str
    ns_name: str
    privs: List[str]


class OpsUser(BaseModel):
    email: EmailStr
    password: str


class LookupObjectType(str, Enum):
    group = "group"
    namespace = "namespace"
    application = "application"


class LookupUserPrivileges(BaseModel):
    email: EmailStr
    lookup_obj: Optional[str]
    depth: Optional[LookupObjectType] = LookupObjectType.group
    priv_expected: Optional[str]


class NamespaceUpdate(BaseModel):
    """
    body of namespace update requests
    """

    key: str
    name: Optional[str] = None
    description: Optional[str] = None


class NamespaceGet(BaseModel):
    """
    body of the get namespace requests
    """

    name: str


class Namespace(BaseModel):
    name: str
    description: Optional[str] = None
    _created_on: datetime = PrivateAttr(default_factory=datetime.utcnow)


class Edge(BaseModel):
    _from: str
    _to: str
    relation: Optional[str] = None
    _created_on: datetime = PrivateAttr(default_factory=datetime.utcnow)


class Application(BaseModel):
    name: str
    description: str
    app_type: str
    hosting: str
    compute: str
    technologies: List[str] = []
    _created_on: datetime = PrivateAttr(default_factory=datetime.utcnow)


class ApplicationCreate(BaseModel):
    name: str
    namespace: str
    description: Optional[str]
    app_type: Optional[str] = "webapp"
    hosting: Optional[str] = "on-prem"
    compute: Optional[str] = "vm"
    technologies: Optional[List[str]]


class Datastore(BaseModel):
    name: str
    store_type: str
    hosting: str
    _created_on: datetime = PrivateAttr(default_factory=datetime.utcnow)


class Component(BaseModel):
    name: str
    component_type: str
    nature: str
    description: str
    primary_security_trait: str
    _created_on: datetime = PrivateAttr(default_factory=datetime.utcnow)


class UserStory(BaseModel):
    name: str
    description: str
    stride: Dict[str, bool] = None
    _created_on: datetime = PrivateAttr(default_factory=datetime.utcnow)


class AbuserStory(BaseModel):
    name: str
    description: str
    _created_on: datetime = PrivateAttr(default_factory=datetime.utcnow)


class ThreatScenario(BaseModel):
    name: str
    description: str
    scenario_type: str
    objective: Optional[str] = None
    cwe: int
    impact: int
    _created_on: datetime = PrivateAttr(default_factory=datetime.utcnow)


class TestCase(BaseModel):
    name: str
    description: str
    test_type: str
    objective: Optional[str] = None
    tools: Optional[List[str]] = []


class Mitigation(BaseModel):
    name: str
    description: str
    orientation: str
    source: str
