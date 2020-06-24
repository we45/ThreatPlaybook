<template>
  <div>
    <v-breadcrumbs :items="breadcrumbData">
      <template v-slot:divider>
        <v-icon>mdi-forward</v-icon>
      </template>
    </v-breadcrumbs>
    <Header
      :name="this.$route.params.name"
      :vulcount="getVulnerabilityProjectCount"
      :userstorycount="getUserStoryProjectCount"
      :abusecount="getAbuserStoryProjectCount"
      :threatscenariocount="get_project_scenario_count"
      :testcasecount="testCaseCount.length"
      :scancount="scanCount.length"
      @viewThreatMap="threatMapPage($event)"
      @viewUserStory="userStoryPage($event)"
      @viewAbuserStory="abuserStoryPage($event)"
      @viewThreatScenario="threatScenarioPage($event)"
      @viewVulnerabilities="vulnerabilitiesPage($event)"
    ></Header>
    <Content :pie-series="getVulnerabilityProjectSev" :scanData="getScanProjectData"></Content>
  </div>
</template>
<script>
import { mapActions, mapGetters } from 'vuex'
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
  mounted() {
    this.projectName = this.$route.params.name
    const data = {
      project: this.projectName
    }
    this.fetchUserStoryByProject(data)
    this.fetchProjectThreatScenarioData(data)
    this.fetchVulnerabilitybyProject(data)
    this.fetchScanbyProject(data)
  },
  methods: {
     ...mapActions('userStory', ['fetchUserStoryByProject']),
     ...mapActions('threatScenario', ['fetchProjectThreatScenarioData']),
     ...mapActions('vulnerability', ['fetchVulnerabilitybyProject']),
     ...mapActions('scan', ['fetchScanbyProject']),
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
    }
  },
  computed: {
    ...mapGetters('userStory', {
      getUserStoryProjectCount: 'getUserStoryProjectCount',
      getAbuserStoryProjectCount: 'getAbuserStoryProjectCount',
      getUserStoryProjectdata: 'getUserStoryProjectdata',
      getUserStoryProjectID: 'getUserStoryProjectID'
    }),
    ...mapGetters('threatScenario', {
      get_project_scenario_count: 'get_project_scenario_count'
    }),
    ...mapGetters('vulnerability', {
      getVulnerabilityProjectCount: 'getVulnerabilityProjectCount',
      getVulnerabilityProjectSev: 'getVulnerabilityProjectSev'
    }),
    ...mapGetters('scan', {
      getScanProjectData: 'getScanProjectData'
    }),
  }
}
</script>
