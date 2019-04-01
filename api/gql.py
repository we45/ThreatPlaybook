import graphene
from graphene_mongo import MongoengineObjectType
from models import Vulnerability, Target
from models import Project as Proj
from models import ThreatModel, Test, Repo, RepoTestCase
from models import UseCase, AbuseCase, VulnerabilityEvidence, Scan, Interaction
from mongoengine import DoesNotExist
from graphene.relay import Node
from utils import connect_db, _validate_jwt

connect_db()


class Vuln(MongoengineObjectType):
    class Meta:
        model = Vulnerability


class Project(MongoengineObjectType):
    class Meta:
        model = Proj


class TCase(MongoengineObjectType):
    class Meta:
        model = Test


class TModel(MongoengineObjectType):
    class Meta:
        model = ThreatModel


class UserStory(MongoengineObjectType):
    class Meta:
        model = UseCase


class AbuserStory(MongoengineObjectType):
    class Meta:
        model = AbuseCase
        # interfaces = (Node,)


class Repository(MongoengineObjectType):
    class Meta:
        model = Repo


class RepositoryTestCase(MongoengineObjectType):
    class Meta:
        model = RepoTestCase


class Tgt(MongoengineObjectType):
    class Meta:
        model = Target


class VulScan(MongoengineObjectType):
    class Meta:
        model = Scan


class Relations(MongoengineObjectType):
    class Meta:
        model = Interaction


class VulEvidence(MongoengineObjectType):
    class Meta:
        model = VulnerabilityEvidence


class NewProject(graphene.ObjectType):
    name = graphene.String()


class NewScan(graphene.ObjectType):
    created_on = graphene.String()
    name = graphene.String()
    synced = graphene.Boolean()


class NewUserStory(graphene.ObjectType):
    short_name = graphene.String()
    description = graphene.String()
    project = graphene.String()


class NewAbuserStory(graphene.ObjectType):
    short_name = graphene.String()
    description = graphene.String()
    project = graphene.String()


class NewTestCase(graphene.ObjectType):
    name = graphene.String()
    test_case = graphene.String()
    executed = graphene.Boolean()
    tools = graphene.List(graphene.String)
    type = graphene.String()
    tags = graphene.List(graphene.String)


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

class AggregateThreatModel(graphene.ObjectType):
    name = graphene.String()
    vul_name = graphene.String()
    description = graphene.String()
    severity = graphene.Int()
    cwe = graphene.Int()
    abuses = graphene.List(AbuserStory)
    usecases = graphene.List(UserStory)


class NewVulnerabilityEvidence(graphene.ObjectType):
    name = graphene.String()
    log = graphene.String()
    data = graphene.String()
    url = graphene.String()
    param = graphene.String()
    attack = graphene.String()
    evidence = graphene.String()
    other_info = graphene.String()


class UserStoryInput(graphene.InputObjectType):
    short_name = graphene.String()
    description = graphene.String()
    project = graphene.String()
    part_of = graphene.String()


class InteractionInput(graphene.InputObjectType):
    user_story_name = graphene.String()
    nature = graphene.String()
    endpoint = graphene.String()
    data_flow = graphene.String()


class NewInteraction(graphene.ObjectType):
    user_story_name = graphene.String()
    nature = graphene.String()
    endpoint = graphene.String()
    data_flow = graphene.String()


class VulnerabilityEvidenceInput(graphene.InputObjectType):
    name = graphene.String()
    log = graphene.String()
    data = graphene.String()
    url = graphene.String()
    param = graphene.String()
    attack = graphene.String()
    evidence = graphene.String()
    other_info = graphene.String()
    vuln_id = graphene.String()


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
    scan = graphene.String()


# class TestCaseInput(graphene.InputObjectType):
#     name = graphene.String()
#     test_case = graphene.String()
#     executed = graphene.Boolean()
#     tools = graphene.List(graphene.String)
#     type = graphene.String()
#     tags = graphene.List(graphene.String)

class IndividualTestCaseInput(graphene.InputObjectType):
    name = graphene.String()
    test_case = graphene.String()
    executed = graphene.Boolean()
    tools = graphene.List(graphene.String)
    type = graphene.String()
    tags = graphene.List(graphene.String)
    threat_model = graphene.String()


class ThreatModelInput(graphene.InputObjectType):
    name = graphene.String()
    vul_name = graphene.String()
    description = graphene.String()
    severity = graphene.Int()
    cwe = graphene.Int()
    abuser_stories = graphene.List(graphene.String)
    user_story = graphene.String()
    mitigations = graphene.List(graphene.JSONString)
    categories = graphene.List(graphene.String)


class NewVulnerability(graphene.ObjectType):
    id = graphene.String()
    tool = graphene.String()
    name = graphene.String()
    cwe = graphene.Int()
    severity = graphene.Int()
    description = graphene.String()
    observation = graphene.String()
    remediation = graphene.String()
    project = graphene.String()
    evidences = graphene.List(NewVulnerabilityEvidence)


# Mutations
class CreateProject(graphene.Mutation):
    class Arguments:
        name = graphene.String()

    ok = graphene.Boolean()
    project = graphene.Field(lambda: NewProject)

    def mutate(self, info, name):
        if _validate_jwt(info.context['request'].headers):
            try:
                new_project = Proj(name=name).save()
                ok = True
                return CreateProject(project=new_project)
            except Exception as e:
                raise Exception(str(e))
        else:
            raise Exception("Unauthorized to perform action")


class CreateOrUpdateUserStory(graphene.Mutation):
    class Arguments:
        userstory = UserStoryInput(required=True)

    user_story = graphene.Field(lambda: NewUserStory)

    def mutate(self, info, **kwargs):
        if _validate_jwt(info.context['request'].headers):
            try:
                if 'userstory' in kwargs:
                    attrs = kwargs['userstory']
                    my_proj = Proj.objects.get(name=attrs['project'])
                    try:
                        ref_user_story = UseCase.objects.get(short_name=attrs['short_name'])
                        UseCase.objects(short_name=attrs['short_name']).update_one(short_name=attrs['short_name'],
                                                                                   description=attrs['description'],
                                                                                   project=my_proj, upsert=True)
                        if 'part_of' in attrs:
                            ref_user_story.update(part_of=attrs['part_of'])
                        new_user_story = ref_user_story
                    except DoesNotExist:
                        new_user_story = UseCase()
                        new_user_story.short_name = attrs['short_name']
                        new_user_story.description = attrs['description']
                        new_user_story.project = my_proj
                        if 'part_of' in attrs:
                            new_user_story.part_of = attrs['part_of']

                        new_user_story.save()

                        return CreateOrUpdateUserStory(user_story=new_user_story)
                    except DoesNotExist as de:
                        return de.args
                    except Exception as e:
                        return e.args
            except Exception as me:
                return me.args
        else:
            raise Exception("Unauthorized to Perform Action")


class CreateOrUpdateInteraction(graphene.Mutation):
    class Arguments:
        new_interaction = InteractionInput(required=True)

    interaction = graphene.Field(lambda: NewInteraction)

    def mutate(self, info, **kwargs):
        if _validate_jwt(info.context['request'].headers):
            try:
                attrs = kwargs['new_interaction']
                ref_user_story = UseCase.objects.get(short_name=attrs['user_story_name'])
                new_interaction = Interaction(nature=attrs['nature'],
                                              data_flow=attrs['data_flow'], endpoint=attrs['endpoint'],
                                              project=ref_user_story.project).save()
                if attrs['nature'] == 'I':
                    ref_user_story.update(add_to_set__relations=new_interaction)
                elif attrs['nature'] == 'E':
                    ref_user_story.update(add_to_set__relations=new_interaction)
                else:
                    raise Exception("Invalid type of Interaction")
            except DoesNotExist:
                raise Exception("The User Story doesn't seem to exist")
        else:
            raise Exception("Unauthorized to perform task")


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
        if _validate_jwt(info.context['request'].headers):
            try:
                ref_proj = Proj.objects.get(name=project)
            except DoesNotExist as de:
                return de.args

            try:
                ref_user_story = UseCase.objects.get(short_name=user_story)
            except DoesNotExist as ude:
                return ude.args

            try:
                AbuseCase.objects.get(short_name=short_name)
                AbuseCase.objects(short_name=short_name).update_one(short_name=short_name,
                                                                    description=description,
                                                                    project=ref_proj, upsert=True)
                new_abuse_case = AbuseCase.objects.get(short_name=short_name)

                ref_user_story.update(add_to_set__abuses=[new_abuse_case.id])
                updated = True
                created = False
            except DoesNotExist:
                new_abuse_case = AbuseCase(short_name=short_name, description=description, project=ref_proj).save()
                ref_user_story.update(add_to_set__abuses=[new_abuse_case.id])
                updated = False
                created = True

            return CreateOrUpdateAbuserStory(abuser_story=new_abuse_case)
        else:
            raise Exception("Unauthorized to perform action")


class CreateOrUpdateThreatModel(graphene.Mutation):
    class Arguments:
        t_model = ThreatModelInput(required=True)

    threat_model = graphene.Field(lambda: NewThreatModel)

    def mutate(self, info, **kwargs):
        if _validate_jwt(info.context['request'].headers):
            if 't_model' in kwargs:
                model_attribs = kwargs['t_model']
                if not all(k in model_attribs for k in ("name", "vul_name", "description")):
                    raise Exception("Mandatory parameters are not in the mutation")
                else:
                    try:
                        cwe_val = model_attribs.get('cwe', 0)
                        related_cwes = model_attribs.get('related_cwes', [])
                        mitigations = model_attribs.get('mitigations', [])
                        severity = int(model_attribs.get('severity', 1))
                        test_cases = model_attribs.get('tests', [])
                        try:
                            ThreatModel.objects.get(name=model_attribs.get('name'))
                            new_threat_model = ThreatModel.objects(name=model_attribs.get('name')).update_one(
                                name=model_attribs.get('name'),
                                vul_name=model_attribs.get('vul_name'),
                                cwe=cwe_val, severity=severity,
                                related_cwes=related_cwes,
                                mitigations=mitigations,
                                description=model_attribs.get('description'),
                                tests=test_cases, upsert=True
                            )
                            new_threat_model = ThreatModel.objects.get(name=model_attribs.get('name'))

                        except DoesNotExist:
                            new_threat_model = ThreatModel(name=model_attribs.get('name'),
                                                           vul_name=model_attribs.get('vul_name'),
                                                           cwe=cwe_val, severity=severity,
                                                           related_cwes=related_cwes,
                                                           mitigations=mitigations,
                                                           description=model_attribs.get('description'),
                                                           tests=test_cases
                                                           ).save()
                    except Exception as e:
                        return e.args

                    if 'abuser_stories' in model_attribs:
                        abuses = model_attribs.get('abuser_stories')
                        for single in abuses:
                            try:
                                ref_abuse = AbuseCase.objects.get(short_name=single)
                                linked_tm = ThreatModel.objects.get(name=model_attribs.get('name'))
                                ref_abuse.update(add_to_set__models=[linked_tm.id])
                            except DoesNotExist:
                                pass

                    if 'user_story' in model_attribs:
                        try:
                            features = model_attribs.get('user_story')
                            ref_use = UseCase.objects.get(short_name=features)
                            ref_use.update(add_to_set__scenarios=new_threat_model)
                        except DoesNotExist:
                            raise Exception("Feature/User Story mentioned does not exist")

            return CreateOrUpdateThreatModel(threat_model=new_threat_model)
        else:
            raise Exception("Unauthorized to perform action")


class CreateOrUpdateTarget(graphene.Mutation):
    class Arguments:
        name = graphene.String()
        url = graphene.String()
        project = graphene.String()

    created = graphene.Boolean()
    updated = graphene.Boolean()
    target = graphene.Field(lambda: NewTarget)

    def mutate(self, info, **kwargs):
        if _validate_jwt(info.context['request'].headers):
            if not all(k in kwargs for k in ("name", "url", "project")):
                raise Exception("Mandatory fields of `name`, `url` and `project` not in mutation")

            else:
                try:
                    ref_project = Proj.objects.get(name=kwargs['project'])
                except DoesNotExist:
                    return "No Project specified"

                try:
                    Target.objects.get(name=kwargs['name'])
                    new_target = Target.objects(name=kwargs['name']).update_one(name=kwargs['name'],
                                                                                url=kwargs['url'],
                                                                                project=ref_project)
                    updated = True
                except DoesNotExist:
                    new_target = Target(name=kwargs['name'], url=kwargs['url'], project=ref_project).save()
                    created = True

                return CreateOrUpdateTarget(target=new_target)
        else:
            raise Exception("Unauthorized to perform action")


class CreateScan(graphene.Mutation):
    class Arguments:
        target = graphene.String()

    scan = graphene.Field(lambda: NewScan)

    def mutate(self, info, target):
        if _validate_jwt(info.context['request'].headers):
            try:
                ref_target = Target.objects.get(name=target)
                new_scan = Scan().save()
                ref_target.update(add_to_set__scans=new_scan.id)
            except DoesNotExist:
                raise Exception("Target matching query does not exist")
            return CreateScan(scan=new_scan)
        else:
            raise Exception("Unauthorized to perform action")


class CreateVulnerability(graphene.Mutation):
    class Arguments:
        vuln = VulnerabilityInput(required=True)

    vulnerability = graphene.Field(lambda: NewVulnerability)

    def mutate(self, info, **kwargs):
        if _validate_jwt(info.context['request'].headers):
            vuln_attributes = kwargs.get('vuln', {})
            if not vuln_attributes:
                raise Exception("You need to specify a vuln key")
            else:
                if not all(k in vuln_attributes for k in ("name", "tool", "description", "project", "scan")):
                    raise Exception("Mandatory fields not in Vulnerability Definition")
                else:
                    try:
                        ref_project = Proj.objects.get(name=vuln_attributes.get('project'))
                        ref_scan = Scan.objects.get(name=vuln_attributes.get('scan'))
                        new_vuln = Vulnerability(name=vuln_attributes['name'], tool=vuln_attributes['tool'],
                                                 description=vuln_attributes['description'],
                                                 cwe=vuln_attributes.get('cwe', 0),
                                                 observation=vuln_attributes.get('observation', ''),
                                                 severity=vuln_attributes.get('severity', 1), project=ref_project,
                                                 remediation=vuln_attributes.get('remediation', '')
                                                 ).save()
                        ref_scan.update(add_to_set__vulnerabilities=new_vuln.id)
                    except DoesNotExist:
                        return "Project OR Target or Scan not found"
                    except Exception as e:
                        return e.args

            return CreateVulnerability(vulnerability=new_vuln)
        else:
            raise Exception("Unauthorized to perform action")


class CreateVulnerabilityEvidence(graphene.Mutation):
    class Arguments:
        evidence = VulnerabilityEvidenceInput(required=True)

    vuln_evidence = graphene.Field(lambda: NewVulnerabilityEvidence)

    def mutate(self, info, **kwargs):
        if _validate_jwt(info.context['request'].headers):
            attributes = kwargs.get('evidence', {})
            if not attributes:
                raise Exception("Vulnerability Evidence doesn't have mandatory fields")
            else:
                if not all(k in attributes for k in ("name", "url", "vuln_id")):
                    raise Exception("Mandatory fields `name`, `url` or `vuln_id` missing")
                else:
                    ref_vuln = Vulnerability.objects.get(id=attributes.get('vuln_id'))
                    new_evidence = VulnerabilityEvidence()
                    new_evidence.name = attributes.get('name')
                    new_evidence.url = attributes.get('url')
                    if 'param' in attributes:
                        new_evidence.param = attributes.get('param')
                    if 'log' in attributes:
                        new_evidence.log = attributes.get('log')
                    if 'attack' in attributes:
                        new_evidence.attack = attributes.get('attack')
                    if 'other_info' in attributes:
                        new_evidence.other_info = attributes.get('other_info')
                    if 'evidence' in attributes:
                        new_evidence.evidence = attributes.get('evidence')

                    new_evidence.save()
                    ref_vuln.update(add_to_set__evidences=new_evidence)

            return CreateVulnerabilityEvidence(new_evidence)
        else:
            raise Exception("Unauthorized to perform action")


class CreateOrUpdateTestCase(graphene.Mutation):
    class Arguments:
        single_case = IndividualTestCaseInput(required=True)

    case = graphene.Field(lambda: NewTestCase)

    def mutate(self, info, **kwargs):
        if _validate_jwt(info.context['request'].headers):
            case_attrs = kwargs.get('single_case')

            if not case_attrs:
                raise Exception("No Case Attributes")
            else:
                if not all(k in case_attrs for k in ("name", "test_case", "threat_model")):
                    raise Exception("mandatory fields not in test case specification")
                else:
                    tool_list = case_attrs.get('tools', [])
                    tag_list = case_attrs.get('tags', [])
                    executed = case_attrs.get('executed', False)
                    test_type = case_attrs.get('test_type', 'discovery')

                    try:
                        ref_case = Test.objects.get(name=case_attrs['name'])
                        if ref_case:
                            Test.objects(name=case_attrs['name']).update_one(
                                name=case_attrs['name'], test_case=case_attrs['test_case'], executed=executed,
                                test_type=test_type, upsert=True)
                            new_test_case = Test.objects.get(name=case_attrs['name'])
                    except DoesNotExist:
                        new_test_case = Test(
                            name=case_attrs['name'], test_case=case_attrs['test_case'],
                            tags=tag_list, tools=tool_list, executed=executed, test_type=test_type
                        ).save()
                    try:
                        ref_model = ThreatModel.objects.get(name=case_attrs['threat_model'])
                        ref_model.update(add_to_set__tests=new_test_case)
                        print(ref_model)

                    except DoesNotExist:
                        pass
            return CreateOrUpdateTestCase(case=new_test_case)
        else:
            raise Exception("Unauthorized to perform action")


class MarkScanSynced(graphene.Mutation):
    class Arguments:
        scan_name = graphene.String()

    scan = graphene.Field(lambda: NewScan)

    def mutate(self, info, scan_name):
        if _validate_jwt(info.context['request'].headers):
            try:
                ref_scan = Scan.objects.get(name=scan_name)
                if not ref_scan.synced:
                    ref_scan.update(synced=True)
                    return MarkScanSynced(scan=ref_scan)
            except DoesNotExist:
                raise Exception("Scan does not exist")
        else:
            raise Exception("Unauthorized to perform action")


# declarations of Mutations and Queries

class ThreatPlaybookMutations(graphene.ObjectType):
    create_project = CreateProject.Field()
    create_or_update_user_story = CreateOrUpdateUserStory.Field()
    create_or_update_abuser_story = CreateOrUpdateAbuserStory.Field()
    create_or_update_threat_model = CreateOrUpdateThreatModel.Field()
    create_vulnerability = CreateVulnerability.Field()
    create_target = CreateOrUpdateTarget.Field()
    create_or_update_test_case = CreateOrUpdateTestCase.Field()
    create_vulnerability_evidence = CreateVulnerabilityEvidence.Field()
    create_scan = CreateScan.Field()
    create_interaction = CreateOrUpdateInteraction.Field()
    mark_scan_synced = MarkScanSynced.Field()


class Query(graphene.ObjectType):
    vulns = graphene.List(Vuln)
    scans = graphene.List(VulScan)
    projects = graphene.List(Project)
    scenarios = graphene.List(TModel)
    user_stories = graphene.List(UserStory)
    abuser_stories = graphene.List(AbuserStory)
    all_repos = graphene.List(Repository)
    project = graphene.Field(NewProject)
    project_by_name = graphene.Field(Project, name=graphene.String())
    user_story_by_name = graphene.Field(UserStory, short_name=graphene.String())
    abuser_story_by_name = graphene.Field(AbuserStory, short_name=graphene.String())
    search_threat_scenario = graphene.List(TModel, name=graphene.String(), cwe=graphene.Int(),
                                           severity=graphene.Int(), tests__name=graphene.String(),
                                           tests__tools=graphene.String(), project_name=graphene.String())

    repo_by_name = graphene.Field(Repository, short_name=graphene.String())
    user_story_by_project = graphene.List(UserStory, project=graphene.String())
    abuser_story_by_project = graphene.List(AbuserStory, project=graphene.String())
    tgt_by_project = graphene.List(Tgt, project=graphene.String())
    vuls_by_scan = graphene.Field(VulScan, scan_name=graphene.String())
    relations = graphene.List(Relations)
    vuls_by_cwe = graphene.List(Vuln, cwe=graphene.Int())
    # stories_by_cwe = graphene.List(graphene.JSONString, cwe=graphene.Int())

    def resolve_vulns(self, info):
        if _validate_jwt(info.context['request'].headers):
            return list(Vulnerability.objects.all())
        else:
            raise Exception("Unauthorized to perform action")

    def resolve_scans(self, info):
        if _validate_jwt(info.context['request'].headers):
            return list(Scan.objects.all())
        else:
            raise Exception("Unauthorized to perform action")

    def resolve_projects(self, info):
        if _validate_jwt(info.context['request'].headers):
            return list(Proj.objects.all())
        else:
            raise Exception("Unauthorized to perform action")

    def resolve_user_stories(self, info):
        if _validate_jwt(info.context['request'].headers):
            return list(UseCase.objects.all())
        else:
            raise Exception("Unauthorized to perform action")

    def resolve_scenarios(self, info):
        if _validate_jwt(info.context['request'].headers):
            return list(ThreatModel.objects.all())
        else:
            raise Exception("Unauthorized to perform action")

    def resolve_abuser_stories(self, info):
        if _validate_jwt(info.context['request'].headers):
            return list(AbuseCase.objects.all())
        else:
            raise Exception("Unauthorized to perform action")

    def resolve_all_repos(self, info):
        if _validate_jwt(info.context['request'].headers):
            return list(Repo.objects.all())
        else:
            raise Exception("Unauthorized to perform action")

    def resolve_project_by_name(self, info, **kwargs):
        if 'name' in kwargs:
            return Proj.objects.get(name=kwargs['name'])

    def resolve_user_story_by_name(self, info, **kwargs):
        if _validate_jwt(info.context['request'].headers):
            if 'short_name' in kwargs:
                return UseCase.objects.get(short_name=kwargs['short_name'])
        else:
            raise Exception("Unauthorized to perform action")

    def resolve_user_story_by_project(self, info, **kwargs):
        if _validate_jwt(info.context['request'].headers):
            if 'project' in kwargs:
                ref_project = Proj.objects.get(name=kwargs.get('project'))
                print(ref_project)
                return UseCase.objects(project=ref_project.id)
        else:
            raise Exception("Unauthorized to perform action")

    def resolve_abuser_story_by_name(self, info, **kwargs):
        if _validate_jwt(info.context['request'].headers):
            if 'short_name' in kwargs:
                return AbuseCase.objects.get(short_name=kwargs['short_name'])
        else:
            raise Exception("Unauthorized to perform action")

    def resolve_abuser_story_by_project(self, info, **kwargs):
        if _validate_jwt(info.context['request'].headers):
            if 'project' in kwargs:
                ref_project = Proj.objects.get(name=kwargs.get('project'))
                return AbuseCase.objects(project=ref_project.id)
        else:
            raise Exception("Unauthorized to perform action")

    def resolve_tgt_by_project(self, info, **kwargs):
        if _validate_jwt(info.context['request'].headers):
            if 'project' in kwargs:
                ref_project = Proj.objects.get(name=kwargs.get('project'))
                return Target.objects(project=ref_project.id)
        else:
            raise Exception("Unauthorized to perform action")

    def resolve_search_threat_scenario(self, info, **kwargs):
        if _validate_jwt(info.context['request'].headers):
            if kwargs.get('project_name'):
                try:
                    ref_project = Proj.objects.get(name=kwargs.get('project_name'))
                    return ThreatModel.objects(project=ref_project.id)
                except DoesNotExist as de:
                    return de
            else:
                for single in kwargs.keys():
                    if '__' in single:
                        val = kwargs[single]
                        kwargs.pop(single)
                        other_val = single.replace('__', '.')
                        kwargs[other_val] = val
                print(kwargs)
                return ThreatModel.objects(__raw__=kwargs)
        else:
            raise Exception("Unauthorized to perform action")

    def resolve_repo_by_name(self, info, **kwargs):
        if _validate_jwt(info.context['request'].headers):
            return Repo.objects.get(short_name=kwargs.get('short_name'))
        else:
            raise Exception("Unauthorized to perform action")

    def resolve_vuls_by_scan(self, info, **kwargs):
        if _validate_jwt(info.context['request'].headers):
            if 'scan_name' in kwargs:
                ref_scan = Scan.objects.get(name=kwargs.get('scan_name'))
                return ref_scan
        else:
            raise Exception("Unauthorized to perform action")

    def resolve_relations(self, info):
        if _validate_jwt(info.context['request'].headers):
            return list(Interaction.objects.all())
        else:
            raise Exception("Unauthorized to perform action")

    def resolve_vuls_by_cwe(self, info, **kwargs):
        if _validate_jwt(info.context['request'].headers):
            if 'cwe' in kwargs:
                if isinstance(kwargs['cwe'], int):
                    return list(Vulnerability.objects(cwe=kwargs['cwe']))
        else:
            raise Exception("Unauthorized to perform action")

    # def resolve_stories_by_cwe(self, info, **kwargs):
    #     if _validate_jwt(info.context['request'].headers):
    #         if 'cwe' in kwargs:
    #             if isinstance(kwargs['cwe'], int):
    #                 pipeline = [{"$match": {"cwe": kwargs['cwe']}}, {
    #                     "$lookup": {"from": "abuse_case", "localField": "_id", "foreignField": "models",
    #                                 "as": "abuses"}}, {"$lookup": {"from": "use_case", "localField": "_id",
    #                                                                "foreignField": "scenarios", "as": "usecases"}}]
    #                 something = list(ThreatModel.objects.aggregate(*pipeline))
    #                 print(something)
    #                 return something
    #     else:
    #         raise Exception("Unauthorized to perform action")
