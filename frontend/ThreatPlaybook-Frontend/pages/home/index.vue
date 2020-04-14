<template>
  <div>
    <v-breadcrumbs :items="breadcrumbData">
      <template v-slot:divider>
        <v-icon>mdi-forward</v-icon>
      </template>
    </v-breadcrumbs>
    <v-row>
      <v-col v-for="(item, i) in getCountList" :key="i" cols="3">
        <v-card>
          <div class="d-flex flex-no-wrap justify-space-between">
            <div>
              <v-card-title
                class="subtitle-1"
                v-text="item.title"
              ></v-card-title>

              <!-- <v-card-subtitle v-text="item.artist"></v-card-subtitle> -->
              <h2 class="display-1 text-center" v-text="item.count"></h2>
              <br />
            </div>

            <!-- <v-avatar class="ma-3" size="125" tile>
              <v-icon v-text="item.icon"></v-icon>
            </v-avatar>-->
            <!-- <v-img :src="item.src"></v-img> -->
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
              :series="fetchThreatScenarioSevChartData"
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
              :series="fetchSeverityChartData"
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
  },
  methods: {
    ...mapActions('home', ['showPageLoading', 'fetchData'])
  },
  computed: {
    ...mapGetters('home', {
      isPageLoading: 'isPageLoading',
      getCountList: 'getCountList',
      fetchThreatScenarioSevChartData: 'fetchThreatScenarioSevChartData',
      fetchSeverityChartData: 'fetchSeverityChartData'
    })
  }
  // apollo: {
  //   dashboardQuery: {
  //     query: gql`
  //       query {
  //         projects {
  //           name
  //         }
  //         userStories {
  //           id
  //         }
  //         scenarios {
  //           severity
  //         }
  //         scans {
  //           name
  //           vulnerabilities {
  //             severity
  //           }
  //         }
  //       }
  //     `,
  //     update: (result) => {
  //       return result
  //     }
  //   }
  // }
}
</script>
