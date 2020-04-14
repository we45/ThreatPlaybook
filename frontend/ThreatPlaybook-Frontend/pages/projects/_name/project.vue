<template>
  <div>
    <v-breadcrumbs :items="breadcrumbData">
      <template v-slot:divider>
        <v-icon>mdi-forward</v-icon>
      </template>
    </v-breadcrumbs>
    <Header
      :name="projectName"
      :vul-count="vulCount.length"
      :user-story-count="userStoryCount.length"
      :abuse-count="abuseCount.length"
      :threat-scenario-count="threatScenarioCount.length"
      :test-case-count="testCaseCount.length"
      :scan-count="scanCount.length"
      @viewThreatMap="threatMapPage($event)"
      @viewUserStory="userStoryPage($event)"
      @viewAbuserStory="abuserStoryPage($event)"
      @viewThreatScenario="threatScenarioPage($event)"
      @viewVulnerabilities="vulnerabilitiesPage($event)"
    ></Header>
    <Content :pie-series="pieSeries" :scanData="scanData"></Content>
  </div>
</template>
<script>
import gql from 'graphql-tag'
import Header from '@/components/project/Header'
import Content from '@/components/project/Content'
export default {
  layout: 'main',
  components: {
    Header,
    Content
  },
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
      userStoryCount: [],
      abuseCount: [],
      threatScenarioCount: [],
      testCaseCount: [],
      scanCount: [],
      vulCount: [],
      scanData: [],
      pieSeries: []
    }
  },
  created() {
    this.projectName = this.$route.params.name
    this.fetchProjectInfo()
    this.fetchProjectScanInfo()
  },
  methods: {
    threatMapPage(event) {
      if (event.view) {
        this.$router.push('/projects/' + this.projectName + '/threat-map')
      }
    },
    userStoryPage(event) {
      if (event.view) {
        this.$router.push('/projects/' + this.projectName + '/user-story')
      }
    },
    abuserStoryPage(event) {
      if (event.view) {
        this.$router.push('/projects/' + this.projectName + '/abuser-story')
      }
    },
    threatScenarioPage(event) {
      if (event.view) {
        this.$router.push('/projects/' + this.projectName + '/threat-scenario')
      }
    },
    vulnerabilitiesPage(event) {
      if (event.view) {
        this.$router.push('/projects/' + this.projectName + '/vulnerabilities')
      }
    },
    // testCasesPage(event) {
    //   if (event.view) {
    //     this.$router.push('/projects/' + this.projectName + '/test-cases')
    //   }
    // },
    async fetchProjectInfo() {
      const result = await this.$apollo.query({
        query: gql`
          query singleProjectQuery($pname: String!) {
            userStoryByProject(project: $pname) {
              shortName
              description
              abuses {
                shortName
                scenarios {
                  name
                  cwe
                  description
                  tests {
                    name
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
      if (result.data.userStoryByProject.length > 0) {
        for (const singleFeature of result.data.userStoryByProject) {
          this.userStoryCount.push(singleFeature.shortName)
          if (singleFeature.abuses.length > 0) {
            for (const singleAbuse of singleFeature.abuses) {
              this.abuseCount.push(singleAbuse.shortName)
              if (singleAbuse.scenarios.length > 0) {
                for (const singleScenario of singleAbuse.scenarios) {
                  this.threatScenarioCount.push(singleScenario.name)
                  for (const singleTest of singleScenario.tests) {
                    this.testCaseCount.push(singleTest.name)
                  }
                }
              }
            }
          }
        }
      }
    },
    async fetchProjectScanInfo() {
      const result = await this.$apollo.query({
        query: gql`
          query singleProjectQuery($pname: String!) {
            tgtByProject(project: $pname) {
              name
              scans {
                name
                vulnerabilities {
                  name
                  severity
                }
              }
            }
          }
        `,
        variables: {
          pname: this.projectName
        }
      })
      const highPieCount = []
      const mediumPieCount = []
      const lowPieCount = []
      if (result.data.tgtByProject.length > 0) {
        for (const scans of result.data.tgtByProject) {
          for (const scan of scans.scans) {
            this.scanCount.push(scan.name)
            this.scanData.push({
              name: scan.name
            })
            for (const vulSev of scan.vulnerabilities) {
              this.vulCount.push(vulSev.name)
              if (vulSev.severity === 3) {
                highPieCount.push(vulSev.severity)
              } else if (vulSev.severity === 2) {
                mediumPieCount.push(vulSev.severity)
              } else {
                lowPieCount.push(vulSev.severity)
              }
            }
          }
        }
      }
      this.pieSeries.push(highPieCount.length)
      this.pieSeries.push(mediumPieCount.length)
      this.pieSeries.push(lowPieCount.length)
    }
  }
}
</script>
