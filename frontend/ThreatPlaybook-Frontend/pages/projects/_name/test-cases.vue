/* eslint-disable no-var */
<template>
  <div>
    <v-card>
      <v-card-title
        class="display-2 justify-center"
        v-text="projectName + ' - Threat Scenario'"
      ></v-card-title>
    </v-card>
    <br />
    <v-card>
      <v-treeview hoverable :items="chartData"></v-treeview>
    </v-card>
  </div>
</template>
<script>
import gql from 'graphql-tag'
export default {
  layout: 'main',
  data() {
    return {
      chartData: []
    }
  },
  created() {
    this.projectName = this.$route.params.name
    this.fetchProjectUserInfo()
  },
  methods: {
    async fetchProjectUserInfo() {
      const result = await this.$apollo.query({
        query: gql`
          query singleProjectQuery($pname: String!) {
            userStoryByProject(project: $pname) {
              shortName
              abuses {
                id
                shortName
                scenarios {
                  id
                  name
                  tests {
                    id
                    name
                    testCase
                    testType
                    tools
                  }
                }
              }
            }
          }
        `,
        variables: {
          pname: this.projectName
        }
      })
      this.chartData = []
      if (result.data.userStoryByProject.length > 0) {
        for (const single of result.data.userStoryByProject) {
          // let userStoryObj = {}
          // userStoryObj = {
          //   name: single.shortName,
          //   children: [],
          //   type: 'us',
          //   title: 'User Story'
          // }
          // this.chartData.push(userStoryObj)
          for (const abuse of single.abuses) {
            // let abuseObj = {}
            // abuseObj = {
            //   name: abuse.shortName,
            //   children: [],
            //   type: 'as',
            //   title: 'Abuser Story'
            // }
            // userStoryObj.children.push(abuseObj)
            if (single.abuses.length > 0) {
              // let scenarioObj = {}
              // for (const scenario of abuse.scenarios) {
              //   scenarioObj = {
              //     name: scenario.name,
              //     children: [],
              //     type: 'mod',
              //     title: 'Threat Scenario'
              //   }
              //   this.chartData.children.push(scenarioObj)
              // }
              if (abuse.scenarios.length > 0) {
                for (const scenario of abuse.scenarios) {
                  for (const test of scenario.tests) {
                    let testObj = {}
                    testObj = {
                      name: test.name,
                      title: 'Test Case',
                      type: 'tm',
                      testType: test.testType,
                      testCase: test.testCase,
                      tools: test.tools
                    }
                    this.chartData.push(testObj)
                  }
                }
              }
            }
          }
        }
      }
    }
  }
}
</script>
