/* eslint-disable no-var */
<template>
  <div>
    <v-breadcrumbs :items="breadcrumbData">
      <template v-slot:divider>
        <v-icon>mdi-forward</v-icon>
      </template>
    </v-breadcrumbs>
    <v-card>
      <v-card-title
        class="display-2 justify-center"
        v-text="'Vulnerabilities of ' + projectName"
      ></v-card-title>
    </v-card>
    <br />
    <v-card>
      <v-simple-table v-if="vulnerabilityData.length > 0">
        <template v-slot:default>
          <thead>
            <tr>
              <th class="text-left">Name</th>
              <th class="text-left">CWE</th>
              <th class="text-left">Severity</th>
              <th class="text-left">Description</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in vulnerabilityData" :key="item.id">
              <td>{{ item.name }}</td>
              <td>{{ item.cwe }}</td>
              <td>
                <v-chip
                  v-if="item.severity === 3"
                  class="ma-2"
                  color="#d11d55"
                  text-color="white"
                  >High</v-chip
                >
                <v-chip
                  v-if="item.severity === 2"
                  class="ma-2"
                  color="#ff9c2c"
                  text-color="white"
                  >Medium</v-chip
                >
                <v-chip
                  v-if="item.severity === 1"
                  class="ma-2"
                  color="#008b8f"
                  text-color="white"
                  >Low</v-chip
                >
                <v-chip
                  v-if="item.severity === 0"
                  class="ma-2"
                  color="#008b8f"
                  text-color="white"
                  >Low</v-chip
                >
              </td>
              <td>{{ item.description }}</td>
            </tr>
          </tbody>
        </template>
      </v-simple-table>
    </v-card>
  </div>
</template>
<script>
import gql from 'graphql-tag'
export default {
  layout: 'main',
  data() {
    return {
      breadcrumbData: [
        {
          text: 'Home',
          to: '/home'
        },
        {
          text: 'Project',
          to: '/projects'
        }
      ],
      vulnerabilityData: []
    }
  },
  created() {
    this.projectName = this.$route.params.name
    this.fetchProjectVulnerabilities()
  },
  methods: {
    async fetchProjectVulnerabilities() {
      const result = await this.$apollo.query({
        query: gql`
          query {
            vulns {
              cwe
              name
              description
              project {
                name
              }
              severity
              remediation
              scan {
                name
              }
            }
          }
        `
      })
      this.vulnerabilityData = []
      if (result.data.vulns.length > 0) {
        for (const vul of result.data.vulns) {
          if (this.projectName === vul.project.name) {
            this.vulnerabilityData.push({
              name: vul.name,
              cwe: vul.cwe,
              severity: vul.severity,
              description: vul.description
            })
          }
        }
      }
    }
  }
}
</script>
