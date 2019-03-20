import requests
import json
import os
from uuid import uuid4
import graphene
from mongoengine.errors import NotUniqueError
from mongoengine import DoesNotExist
from utils import connect_db, _validate_jwt
from orchy_model import OrchyCreds
from models import Scan
from graphql.error import GraphQLError

connect_db()

class SyncScan(graphene.ObjectType):
    created_on = graphene.String()
    name = graphene.String()
    synced = graphene.Boolean() 


class OrchyConfig(graphene.Mutation):
    class Arguments:
        endpoint = graphene.String()
        email = graphene.String()
        password = graphene.String()
    
    saved = graphene.Boolean()

    def mutate(self, info, endpoint, email, password):
        if _validate_jwt(info.context['request'].headers):
            try:
                token_url = "{0}/api/user/token/".format(endpoint)
                body = {
                    "email":email,
                    "password":password,
                }
                r = requests.post(token_url,json=body)
                if r.status_code == 200:
                    token = r.json().get('token')
                    access_key_url = "{0}/api/get/token/".format(endpoint)
                    headers = {
                        'Authorization':'JWT {0}'.format(token)
                    }
                    token_req = requests.get(access_key_url,headers=headers)
                    if token_req.status_code == 200:
                        data = {
                            'endpoint':endpoint,
                            'email':email,
                            'password':password,
                        }                                                
                        orchy_creds = OrchyCreds(**data).save()                                                           
                        return OrchyConfig(saved=True)                        
                    else:
                        raise Exception("Invalid creds")
                else:
                    raise Exception("Invalid creds")
            except NotUniqueError:
                raise Exception('Duplicate entry!')
            except:
                raise Exception("Invalid creds")
        else:
            raise Exception("Unauthorized to perform action")        


class MarkScanSynced(graphene.Mutation):
    class Arguments:
        scan_name = graphene.String()

    status = graphene.String()

    def mutate(self, info, scan_name):
        if _validate_jwt(info.context['request'].headers):            
            try:
                ref_scan = Scan.objects.get(name=scan_name)                            
                if not ref_scan.synced:
                    vul = ref_scan.vulnerabilities[0]
                    project = vul.project                    
                    creds = OrchyCreds.objects.first()
                    email = creds.email
                    password = creds.password
                    endpoint = creds.endpoint
                    token_url = "{0}/api/user/token/".format(endpoint)
                    body = {
                        "email":email,
                        "password":password,
                    }
                    r = requests.post(token_url,json=body)
                    if r.status_code == 200:
                        token = r.json().get('token')
                        application_url = '{0}/api/applications/'.format(endpoint)                    
                        headers = {
                            'Authorization':'JWT {0}'.format(token)
                        }
                        application_req = requests.get(application_url,headers=headers)
                        if application_req.status_code == 200:
                            applications = application_req.json().get('results')
                            application_present = [app for app in applications if app.get('name') == project.name]
                            if application_present:
                                get_webhook_url = '{0}/api/applications/{1}/'.format(endpoint,application_present[0].get('id'))                    
                                headers = {
                                    'Authorization':'JWT {0}'.format(token)
                                }
                                get_webhook_req = requests.get(get_webhook_url,headers=headers)
                                if get_webhook_req.status_code == 200:
                                    webhook_id = get_webhook_req.json().get('webhook_id')                                    
                                    vul_dict = {
                                        'tool':vul.tool,
                                        'vulnerabilities':[],
                                    }
                                    for vul in ref_scan.vulnerabilities:                                        
                                        if project.name == application_present[0].get('name'):
                                            data_dict = {
                                                'name':vul.name,
                                                'description':vul.description,
                                                'cwe':vul.cwe,
                                                'severity':vul.severity,
                                            }
                                            vul_dict['vulnerabilities'].append(data_dict)                                                                        
                                    webhook_post_url = '{0}/api/webhooks/post/{1}/'.format(endpoint,webhook_id)
                                    webhook_post_req = requests.post(webhook_post_url,json={'vuls':vul_dict},headers=headers)
                                    if webhook_post_req.status_code == 200:
                                        scan_id = webhook_post_req.json().get('scan_id')
                                        ref_scan.update(synced=True)
                                        status = 'Scan synced to Orchestron with the scan id `{0}`'.format(scan_id)
                                        return MarkScanSynced(status=status)
                                    else:
                                        raise GraphQLError("Unable to sync the scan")                                
                                else:
                                    raise GraphQLError("Unable to getch the webhook for this application")
                            else:
                                raise GraphQLError("Application not present")                                
                        else:
                            raise GraphQLError("Unable to fetch applications")
                    else:
                        raise GraphQLError("Unable to authenticate with Orchestron")
                else:
                    raise GraphQLError("Scan is already synced")
            except DoesNotExist:
                raise GraphQLError("Scan does not exist")                          
        else:
            raise GraphQLError("Unauthorized to perform action")



