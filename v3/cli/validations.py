import pyjq
from jinja2 import Template

def validate_project_response(content):
    return pyjq.first('.data.createProject.project.name', content)

def validate_user_story(content):
    return pyjq.first('.data.createOrUpdateUserStory.userStory.shortName',content)

def validate_abuser_story(content):
    return pyjq.first('.data.createOrUpdateAbuserStory.abuserStory.shortName', content)

def validate_repo_query(content):
    return pyjq.first('.data.repoByName',content)

def template_threat_model_mutation():
    mutation = """
    mutation {
      createOrUpdateThreatModel(
        tModel: {
          {% for key, value in mutation_vars.items() %}
          {% if value['type'] == "string" %}
          {{ key }}: "{{ value['val'] }}"
          {% elif value['type'] == "list" %}
          {{ key }}: {{ value['val']|tojson }}
          {% else %} 
          {{ key }}: {{ value['val'] }}
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