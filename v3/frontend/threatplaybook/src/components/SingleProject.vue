<template>
  <section>
    <h2 class="title">Project: {{ projectActual }}</h2>
    <b-tabs type="is-boxed" v-model="activeTab">
      <b-tab-item label="Feature/User Stories">
        <div v-for="item in singleProjectQuery">
            <h3 class="card-header-title">Name: {{ item.shortName }}</h3>
            <p class="card-header">{{ item.description }}</p>
            <br>
        </div>
      </b-tab-item>

      <b-tab-item label="Abuser Stories">
        <div v-for="item in singleProjectQuery">
            <div v-for="single_item in item.abuses">
                <h3 class="card-header-title">Name: {{ single_item.shortName }}</h3>
                <p>{{ single_item.description }}</p>
                <br>
            </div>
        </div>
      </b-tab-item>

      <b-tab-item label="Threat Scenarios">
          <div v-for="item in singleProjectQuery">
              <div v-for="single_item in item.abuses">
                  <div v-for="single_scene in single_item.models">
                      <h3 class="card-header-title">Name: {{ single_scene.name }}</h3>
                      <p>{{ single_scene.description }}</p>
                      <p>CWE: {{ single_scene.cwe }}</p>
                      <p v-if="single_scene.severity === 1">Severity: Low</p>
                      <p v-if="single_scene.severity === 2">Severity: Medium</p>
                      <p v-if="single_scene.severity === 3">Severity: High</p>
                      <br>
                  </div>

              </div>
          </div>
      </b-tab-item>

      <b-tab-item label="Threat Map">
        Threat Scenarios
      </b-tab-item>
      <b-tab-item label="Vulnerabilities">
        Threat Scenarios
      </b-tab-item>
    </b-tabs>
  </section>
</template>
<script>
import gql from "graphql-tag";
export default {
  props: ["projectName"],
  data() {
    return {
      projectActual: atob(this.projectName)
    };
  },
  apollo: {
    singleProjectQuery: {
      query: gql`
        query singleProjectQuery($pname: String!) {
          userStoryByProject(project: $pname) {
            shortName
            description
            abuses {
              shortName
              description
              models {
                name
                description
                cwe
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
      `,
      variables() {
        return {
          pname: atob(this.projectName)
        };
      },
      update: result => result.userStoryByProject
    }
  }
};
</script>
