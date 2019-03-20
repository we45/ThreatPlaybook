from mongoengine import *
from graphene_mongo import MongoengineObjectType

class OrchyCreds(Document):
    endpoint = StringField(max_length=100, required = True, unique=True)
    email = StringField(max_length=100, required = True, unique=True)
    password = StringField(max_length=100, required = True, unique=True)


class NewOrchyCreds(MongoengineObjectType):
    class Meta:
        model = OrchyCreds    