<template>
  <div>
    <v-breadcrumbs :items="breadcrumbData">
      <template v-slot:divider>
        <v-icon>mdi-forward</v-icon>
      </template>
    </v-breadcrumbs>
    <v-row>
      <v-col cols="3">
         <v-card>
          <div class="d-flex flex-no-wrap justify-space-between">
            <div>
              <v-card-title
                class="subtitle-1"
                v-text="'Projects'"
              ></v-card-title>
              <h2 class="display-1 text-center" v-text="getProjectCount"></h2>
              <br />
            </div>
          </div>
        </v-card>
      </v-col>
      <v-col cols="3">
         <v-card>
          <div class="d-flex flex-no-wrap justify-space-between">
            <div>
              <v-card-title
                class="subtitle-1"
                v-text="'User Stories'"
              ></v-card-title>
              <h2 class="display-1 text-center" v-text="getUserStoryCount"></h2>
              <br />
            </div>
          </div>
        </v-card>
      </v-col>
      <v-col cols="3">
         <v-card>
          <div class="d-flex flex-no-wrap justify-space-between">
            <div>
              <v-card-title
                class="subtitle-1"
                v-text="'Threat Scenarios'"
              ></v-card-title>
              <h2 class="display-1 text-center" v-text="getThreatScenarioCount"></h2>
              <br />
            </div>
          </div>
        </v-card>
      </v-col>
      <v-col cols="3">
         <v-card>
          <div class="d-flex flex-no-wrap justify-space-between">
            <div>
              <v-card-title
                class="subtitle-1"
                v-text="'Scans'"
              ></v-card-title>
              <h2 class="display-1 text-center" v-text="getScanCount"></h2>
              <br />
            </div>
          </div>
        </v-card>
      </v-col>
    </v-row>
    <br />
    <v-row>
      <v-col cols="6">
        <v-card>
          <v-card-title class="subtitle-1">Threat model severity</v-card-title>
          <v-card-text>
            <apexchart
              type="donut"
              :options="donutOptions"
              :series="getThreatScenarioSevData"
              height="300"
            ></apexchart>
          </v-card-text>
        </v-card>
      </v-col>
      <v-col cols="6">
        <v-card>
          <v-card-title class="subtitle-1"
            >Vulnerabilities by Severity</v-card-title
          >
          <v-card-text>
            <apexchart
              type="pie"
              :options="pieOptions"
              :series="getVulnerabilitySevData"
              height="300"
            ></apexchart>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <v-overlay :value="isPageLoading">
      <v-progress-circular indeterminate size="64"></v-progress-circular>
    </v-overlay>
  </div>
</template>
<script>
import { mapActions, mapGetters } from 'vuex'
export default {
  layout: 'main',
  name: 'Home',
  data() {
    return {
      breadcrumbData: [
        {
          text: 'Home',
          disabled: false,
          to: '/home'
        }
      ],
      donutOptions: {
        labels: ['High', 'Medium', 'Low'],
        colors: ['#d11d55', '#ff9c2c', '#008b8f']
      },
      pieOptions: {
        labels: ['High', 'Medium', 'Low'],
        colors: ['#d11d55', '#ff9c2c', '#008b8f'],
        noData: {
          text: 'Loading...'
        }
      },
      noData: {
        text: 'Loading...'
      }
    }
  },
  mounted() {
    this.showPageLoading(true)
    this.fetchData()
    this.fetchProjectData()
    this.fetchUserStoryData()
    this.fetchThreatScenarioData()
    this.fetchScanData()
    this.fetchThreatScenarioSevData()
    this.fetchVulnerabilitySevData()
  },
  // async asyncData(){
  //   this.showPageLoading(true)
  //   this.fetchData()
  // },
  methods: {
    ...mapActions('home', ['showPageLoading', 'fetchData']),
    ...mapActions('projects', ['fetchProjectData']),
    ...mapActions('userStory', ['fetchUserStoryData']),
    ...mapActions('threatScenario', ['fetchThreatScenarioData', 'fetchThreatScenarioSevData']),
    ...mapActions('scan', ['fetchScanData']),
    ...mapActions('vulnerability', ['fetchVulnerabilitySevData'])
  },
  computed: {
    ...mapGetters('home', {
      isPageLoading: 'isPageLoading',
      fetchThreatScenarioSevChartData: 'fetchThreatScenarioSevChartData',
      fetchSeverityChartData: 'fetchSeverityChartData'
    }),
    ...mapGetters('projects', {
      getProjectCount: 'getProjectCount'
    }),
    ...mapGetters('userStory', {
      getUserStoryCount: 'getUserStoryCount'
    }),
    ...mapGetters('threatScenario', {
      getThreatScenarioCount: 'getThreatScenarioCount',
      getThreatScenarioSevData: 'getThreatScenarioSevData'
    }),
    ...mapGetters('scan', {
      getScanCount: 'getScanCount'
    }),
    ...mapGetters('vulnerability', {
      getVulnerabilitySevData: 'getVulnerabilitySevData'
    })
  }
}
</script>
