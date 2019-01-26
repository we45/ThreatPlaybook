import graphene
from graphene_mongo import MongoengineObjectType
from models import Vulnerability
from models import Project as Proj
from models import ThreatModel
from models import UseCase, AbuseCase
from graphene.relay import Node

class Vuln(MongoengineObjectType):
    class Meta:
        model = Vulnerability


        interfaces = (Node,)

class Project(MongoengineObjectType):
    class Meta:
        model = Proj
#
class TModel(MongoengineObjectType):
    class Meta:
        model = ThreatModel

class UserStory(MongoengineObjectType):
    class Meta:
        model = UseCase

class AbuserStory(MongoengineObjectType):
    class Meta:
        model = AbuseCase

class NewProject(graphene.ObjectType):
    name = graphene.String()

class NewUserStory(graphene.ObjectType):
    name = graphene.String()
    description = graphene.String()

class NewAbuserStory(graphene.ObjectType):
    name = graphene.String()
    description = graphene.String()



#Mutations
class CreateProject(graphene.Mutation):
    class Arguments:
        name = graphene.String()

    ok = graphene.Boolean()
    project = graphene.Field(lambda: NewProject)

    def mutate(self,info, name):
        try:
            new_project = Proj(name = name).save()
            ok = True
            return CreateProject(project = new_project)
        except Exception as e:
            raise Exception(str(e))

class CreateUserStory(graphene.Mutation):
    class Arguments:
        short_name = graphene.String()
        description = graphene.String()
        project = graphene.String()
    ok = graphene.Boolean()
    user_story = graphene.Field(lambda: NewUserStory)

    def mutate(self, info, short_name, description, project):
        try:
            my_proj = Proj.objects.get(name = project)
            if UseCase.objects.get()
            new_user_story = UseCase(short_name = short_name, description = description, project = my_proj).save()
            ok = True
            return CreateUserStory(user_story = new_user_story)
        except Exception as e:
            raise Exception(str(e))

class CreateAbuserStory(graphene.Mutation):
    class Arguments:
        short_name = graphene.String()
        description = graphene.String()
        project = graphene.String()

    ok = graphene.Boolean()
    abuser_story = graphene.Field(lambda: NewAbuserStory)

    def mutate(self, info, short_name, description, project):
        try:
            new_proj = Proj.objects.get(name = project)
            new_abuser

# class CreateVulnerability(graphene.Mutation):
#     class Arguments:
#         graphene.O




class ThreatPlaybookMutations(graphene.ObjectType):
    create_project = CreateProject.Field()

class Query(graphene.ObjectType):
    vulns = graphene.List(Vuln)
    projects = graphene.List(Project)
    scenarios = graphene.List(TModel)
    user_stories = graphene.List(UserStory)
    abuser_stories = graphene.List(AbuserStory)
    project = graphene.Field(NewProject)

    def resolve_vulns(self, info):
        return list(Vulnerability.objects.all())

    def resolve_projects(self, info):
        return list(Proj.objects.all())

    def resolve_user_stories(self, info):
        return list(UseCase.objects.all())

    def resolve_scenarios(self, info):
        return list(ThreatModel.objects.all())

    def resolve_abuser_stories(self, info):
        return list(AbuseCase.objects.all())

