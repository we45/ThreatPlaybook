import graphene
from graphene_mongo import MongoengineObjectType
from models import Vulnerability, Target
from models import Project as Proj
from models import ThreatModel
from models import UseCase, AbuseCase
from mongoengine import DoesNotExist
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
    short_name = graphene.String()
    description = graphene.String()
    project = graphene.String()

class NewAbuserStory(graphene.ObjectType):
    short_name = graphene.String()
    description = graphene.String()
    project = graphene.String()

class NewThreatModel(graphene.ObjectType):
    name = graphene.String()
    vul_name = graphene.String()
    description = graphene.String()
    severity = graphene.Int()
    cwe = graphene.Int()

class NewTarget(graphene.ObjectType):
    name = graphene.String()
    url = graphene.String()
    project = graphene.String()

class NewVulnerabilityEvidence(graphene.ObjectType):
    name = graphene.String()
    log = graphene.String()
    data = graphene.String()
    url = graphene.String()
    param = graphene.String()
    attack = graphene.String()
    evidence = graphene.String()
    other_info = graphene.String()

class VulnerabilityEvidenceInput(graphene.InputObjectType):
    name = graphene.String()
    log = graphene.String()
    data = graphene.String()
    url = graphene.String()
    param = graphene.String()
    attack = graphene.String()
    evidence = graphene.String()
    other_info = graphene.String()

class VulnerabilityInput(graphene.InputObjectType):
    tool = graphene.String()
    name = graphene.String()
    cwe = graphene.Int()
    severity = graphene.Int()
    description = graphene.String()
    observation = graphene.String()
    remediation = graphene.String()
    target = graphene.String()
    project = graphene.String()
    evidences = graphene.InputField(graphene.List(VulnerabilityEvidenceInput))

class NewVulnerability(graphene.ObjectType):
    tool = graphene.String()
    name = graphene.String()
    cwe = graphene.Int()
    severity = graphene.Int()
    description = graphene.String()
    observation = graphene.String()
    remediation = graphene.String()
    project = graphene.String()
    evidences = graphene.List(NewVulnerabilityEvidence)





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

class CreateOrUpdateUserStory(graphene.Mutation):
    class Arguments:
        short_name = graphene.String()
        description = graphene.String()
        project = graphene.String()
    created = graphene.Boolean()
    updated = graphene.Boolean()
    user_story = graphene.Field(lambda: NewUserStory)

    def mutate(self, info, short_name, description, project):
        try:
            my_proj = Proj.objects.get(name = project)
            try:
                UseCase.objects.get(short_name = short_name)
                new_user_story = UseCase.objects(short_name=short_name).update_one(short_name=short_name,
                                                                description=description,
                                                                project=my_proj, upsert=True)
                created = False
                updated = True
            except DoesNotExist:
                new_user_story = UseCase(short_name = short_name, description = description, project = my_proj).save()
                created = True
                updated = False

            return CreateOrUpdateUserStory(user_story = new_user_story)
        except DoesNotExist as de:
            return de.args
        except Exception as e:
            return e.args

class CreateOrUpdateAbuserStory(graphene.Mutation):
    class Arguments:
        short_name = graphene.String()
        description = graphene.String()
        project = graphene.String()
        user_story = graphene.String()

    created = graphene.Boolean()
    updated = graphene.Boolean()
    abuser_story = graphene.Field(lambda: NewAbuserStory)

    def mutate(self, info, short_name, description, project, user_story):
        try:
            ref_proj = Proj.objects.get(name = project)
        except DoesNotExist as de:
            return de.args

        try:
            ref_user_story = UseCase.objects.get(short_name = user_story)
        except DoesNotExist as ude:
            return ude.args

        try:
            AbuseCase.objects.get(short_name = short_name)
            new_abuse_case = AbuseCase.objects(short_name=short_name).update_one(short_name=short_name,
                                                         description=description,
                                                         project=ref_proj, upsert=True)
            ref_user_story.update(add_to_set__abuses=[new_abuse_case.id])
            updated = True
            created = False
        except DoesNotExist:
            new_abuse_case = AbuseCase(short_name=short_name, description=description, project=ref_proj).save()
            ref_user_story.update(add_to_set__abuses = [new_abuse_case.id])
            updated = False
            created = True

        return CreateOrUpdateAbuserStory(abuser_story = new_abuse_case)

class CreateOrUpdateThreatModel(graphene.Mutation):
    class Arguments:
        name = graphene.String()
        vul_name = graphene.String()
        description = graphene.String()
        severity = graphene.Int()
        project = graphene.String()
        cwe = graphene.Int()
        related_cwes = graphene.List(graphene.Int)
        categories = graphene.List(graphene.String)
        mitigations = graphene.List(graphene.String)
        abuser_stories = graphene.List(graphene.String)

    created = graphene.Boolean()
    updated = graphene.Boolean()
    threat_model = graphene.Field(lambda: NewThreatModel)

    def mutate(self, info, **kwargs):
        if not all(k in kwargs for k in ("name", "vul_name", "description", "project")):
            raise Exception("Mandatory parameters are not in the mutation")
        else:
            try:
                ref_project = Proj.objects.get(name = kwargs.get('project'))
            except DoesNotExist as pde:
                return pde.args

            try:
                cwe_val = kwargs.get('cwe', 0)
                related_cwes = kwargs.get('related_cwes', [])
                mitigations = kwargs.get('mitigations', [])
                severity = int(kwargs.get('severity', 1))
                try:
                    ThreatModel.objects.get(name = kwargs.get('name'))
                    new_threat_model = ThreatModel.objects(name=kwargs.get('name')).update_one(name=kwargs.get('name'),
                                                                            vul_name=kwargs.get('vul_name'),
                                                                            cwe=cwe_val,severity=severity,
                                                                            related_cwes = related_cwes,
                                                                            mitigations = mitigations,
                                                                            description = kwargs.get('description'),
                                                                            project = ref_project)
                except DoesNotExist:
                    new_threat_model = ThreatModel(name=kwargs.get('name'),
                                                   vul_name=kwargs.get('vul_name'),
                                                   cwe=cwe_val,severity=severity,
                                                   related_cwes = related_cwes,
                                                   mitigations = mitigations,
                                                   description = kwargs.get('description'),
                                                   project=ref_project).save()
            except Exception as e:
                return e.args

            if 'abuser_stories' in kwargs:
                if not isinstance(kwargs.get('abuser_stories'), list):
                    abuses = [kwargs.get('abuser_stories')]
                else:
                    abuses = kwargs.get('abuser_stories')

                for single in abuses:
                    try:
                        ref_abuse = AbuseCase.objects.get(short_name = single)
                        linked_tm = ThreatModel.objects.get(name = kwargs.get('name'))
                        ref_abuse.update(add_to_set__models=[linked_tm.id])
                    except DoesNotExist:
                        pass

            return CreateOrUpdateThreatModel(threat_model = new_threat_model)

class CreateOrUpdateTarget(graphene.Mutation):
    class Arguments:
        name = graphene.String()
        url = graphene.String()
        project = graphene.String()

    created = graphene.Boolean()
    updated = graphene.Boolean()
    target = graphene.Field(lambda: NewTarget)

    def mutate(self, info, **kwargs):
        if not all(k in kwargs for k in ("name", "url", "project")):
            raise Exception("Mandatory fields of `name`, `url` and `project` not in mutation")

        else:
            try:
                ref_project = Proj.objects.get(name = kwargs['project'])
            except DoesNotExist:
                return "No Project specified"

            try:
                Target.objects.get(name = kwargs['name'])
                new_target = Target.objects(name = kwargs['name']).update_one(name = kwargs['name'],
                                                                              url = kwargs['url'],
                                                                              project = ref_project)
                updated = True
            except DoesNotExist:
                new_target = Target(name = kwargs['name'], url = kwargs['url'], project = ref_project).save()
                created = True

            return CreateOrUpdateTarget(target = new_target)


class CreateVulnerability(graphene.Mutation):
    class Arguments:
        vuln = VulnerabilityInput(required = True)


    vulnerability = graphene.Field(lambda: NewVulnerability)

    def mutate(self, info, **kwargs):
        vuln_attributes = kwargs.get('vuln', {})
        if not vuln_attributes:
            raise Exception("You need to specify a vuln key")
        else:
            if not all(k in vuln_attributes for k in ("name", "tool", "description", "project", "target")):
                raise Exception("Mandatory fields not in Vulnerability Definition")
            else:
                evid_attribs = vuln_attributes.get('evidences', [])
                try:
                    ref_project = Proj.objects.get(name=vuln_attributes.get('project'))
                    ref_target = Target.objects.get(name = vuln_attributes.get('target'))
                    new_vuln = Vulnerability(name=vuln_attributes['name'], tool=vuln_attributes['tool'],
                                             description=vuln_attributes['description'],
                                             cwe=vuln_attributes.get('cwe', 0),
                                             observation=vuln_attributes.get('observation', ''),
                                             severity=vuln_attributes.get('severity', 1), project=ref_project,
                                             target = ref_target,remediation=vuln_attributes.get('remediation', ''),
                                             evidences=evid_attribs
                                             ).save()
                except DoesNotExist:
                    return "Project OR Target not found"
                except Exception as e:
                    return e.args

        return CreateVulnerability(vulnerability = new_vuln)










class ThreatPlaybookMutations(graphene.ObjectType):
    create_project = CreateProject.Field()
    create_or_update_user_story = CreateOrUpdateUserStory.Field()
    create_or_update_abuser_story = CreateOrUpdateAbuserStory.Field()
    create_or_update_threat_model = CreateOrUpdateThreatModel.Field()
    create_vulnerability = CreateVulnerability.Field()
    create_target = CreateOrUpdateTarget.Field()

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


