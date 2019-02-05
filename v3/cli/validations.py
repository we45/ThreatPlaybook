import pyjq
from jinja2 import Template

def validate_project_response(content):
    return pyjq.first('.data.createProject.project.name', content)

def validate_user_story(content):
    return pyjq.first('.data.createOrUpdateUserStory.userStory.shortName',content)

def validate_abuser_story(content):
    return pyjq.first('.data.createOrUpdateAbuserStory.abuserStory', content)

def validate_repo_query(content):
    return pyjq.first('.data.repoByName',content)

def validate_threat_model_query(content):
    return pyjq.first('.data.createOrUpdateThreatModel.threatModel',content)

def validate_test_case_query(content):
    return pyjq.first('.data.createOrUpdateTestCase.case.name', content)

def template_threat_model_mutation():
    mutation = """
    mutation {
      createOrUpdateThreatModel(
        tModel: {
          {% for key, value in mutation_vars.items() %}
          {% if value['type'] == "string" %}
          {{ key }}: "{{ value['name'] }}"
          {% elif value['type'] == "list" %}
          {{ key }}: {{ value['name']|tojson }}  
          {% else %} 
          {{ key }}: {{ value['name'] }}
          {% endif %}
          {% endfor %}
        }
      ) {
        threatModel {
          name
        }
      }
    }
    """
    return Template(mutation)

def template_test_case_mutation():
    mutation = """
    mutation {
      createOrUpdateTestCase(
        singleCase: {
          {% for key, value in mutation_vars.items() %}
          {% if value['type'] == "string" %}
          {{ key }}: "{{ value['name'] }}"
          {% elif value['type'] == "list" %}
          {{ key }}: {{ value['name']|tojson }}  
          {% else %} 
          {{ key }}: {{ value['name'] }}
          {% endif %}
          {% endfor %}     
        }
      ) {
        case {
          name
        }
      }
    }
    """
    return Template(mutation)