import pyjq
from jinja2 import Template

def validate_project_response(content):
    return pyjq.first('.data.createProject.project', content)

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

def validate_user_story_name_select(content):
    return pyjq.first('.data.userStoryByName', content)

def validate_user_stories(content):
    return pyjq.first('.data.userStories', content)

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

def template_user_story_query(query_string_value):
    query = """
    query {
      userStoryByName(
        shortName: "%s"
      ) {
        shortName
        description
        project {
          id
          name
        }
        abuses {
          description
          shortName
          models {
            cwe
            name
            name
            severity
            tests {
              name
              testCase
              testType
            }
          }
        }
        
    }
    }
    """ % query_string_value

    return query

def template_user_story_full():
    query = """
    query {
      userStories {
        description
        shortName
        abuses {
          description
          shortName
          models {
            cwe
            description
            mitigations
            name
            severity
            tests {
              name
              testCase
              testType
              tools
            }
          }
        }
      }
    }
    """
    return query


def template_user_story_mutation():
    query = """
    mutation {
      createOrUpdateUserStory(userstory: {
      {% for key, value in mutation_vars.items() %}
        {{ key }}: "{{ value }}"
      {% endfor %}
      }) {
        userStory {
          shortName
        }
      }
    }
    """
    return Template(query)

def template_interaction_mutation():
    query = """
    mutation {
      createInteraction(newInteraction: {
        {% for key, value in mutation_vars.items() %}
        {{ key }}: "{{ value }}"
        {% endfor %}
      }) {
        interaction {
          nature
        }
      }
    }
    """
    return Template(query)