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
        v-text="projectName"
      ></v-card-title>
    </v-card>
    <br />
    <v-row>
      <v-col cols="12">
        <organization-chart
          :datasource="getThreatMapProjectData"
          :pan="true"
          :zoom="true"
          @node-click="nodeClick($event)"
        ></organization-chart>
      </v-col>
    </v-row>
    <v-navigation-drawer v-model="drawer" absolute temporary right width="70%">
      <v-card>
        <v-card-title
          class="display-1 justify-center"
          v-text="dialogData.type"
        ></v-card-title>
        <v-card-text v-if="dialogData.name">
          <h4 class="title">{{ dialogData.name }}</h4>
        </v-card-text>
        <v-divider></v-divider>
        <v-card-text>{{ dialogData.title }}</v-card-text>
        <v-card-text v-if="dialogData.type === 'Scenarios'">
          <v-row>
            <v-col cols="10">
              <h4 v-if="dialogData.vul_name" class="headline">
                {{ dialogData.vul_name }}
              </h4>
              <br />
              <p v-if="dialogData.cwe" class="subtitle-1">
                CWE : {{ dialogData.cwe }}
              </p>
            </v-col>
            <v-col cols="2">
              <v-chip
                v-if="dialogData.severity === 3"
                class="ma-2"
                color="#d11d55"
                text-color="white"
                >High</v-chip
              >
              <v-chip
                v-if="dialogData.severity === 2"
                class="ma-2"
                color="#ff9c2c"
                text-color="white"
                >Medium</v-chip
              >
              <v-chip
                v-if="dialogData.severity === 1"
                class="ma-2"
                color="#008b8f"
                text-color="white"
                >Low</v-chip
              >
              <v-chip
                v-if="dialogData.severity === 0"
                class="ma-2"
                color="#008b8f"
                text-color="white"
                >Low</v-chip
              >
            </v-col>
          </v-row>
          <p v-if="getASVSData.length > 0" class="title">ASVS</p>
          <v-simple-table v-if="getASVSData.length > 0">
            <template v-slot:default>
              <thead>
                <tr>
                  <th class="text-left">Name</th>
                  <th class="text-left">CWE</th>
                  <th class="text-left">Level</th>
                  <th class="text-left">Description</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="item in getASVSData" :key="item.id">
                  <td>{{ item.name }}</td>
                  <td>{{ item.cwe }}</td>
                  <td>
                    <v-chip
                      v-if="item.l1"
                      class="ma-2"
                      color="indigo"
                      text-color="white"
                      small
                      >L1</v-chip
                    >
                    <v-chip
                      v-if="item.l2"
                      class="ma-2"
                      color="indigo"
                      text-color="white"
                      small
                      >L2</v-chip
                    >
                    <v-chip
                      v-if="item.l3"
                      class="ma-2"
                      color="indigo"
                      text-color="white"
                      small
                      >L3</v-chip
                    >
                  </td>
                  <td>{{ item.description }}</td>
                </tr>
              </tbody>
            </template>
          </v-simple-table>
          <p v-if="relatedVuls.length > 0" class="title">
            Vulnerabilities linked with threat scenario
          </p>
          <v-simple-table v-if="relatedVuls.length > 0">
            <template v-slot:default>
              <thead>
                <tr>
                  <th class="text-left">Name</th>
                  <th class="text-left">CWE</th>
                  <th class="text-left">Severity</th>
                  <th class="text-left">Tool</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="item in relatedVuls" :key="item.id">
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
                  <td>{{ item.tool }}</td>
                </tr>
              </tbody>
            </template>
          </v-simple-table>
        </v-card-text>
        <!-- Test Cases -->
        <v-card v-if="dialogData.type === 'Test Cases'">
          <v-card-text>
            <p v-if="dialogData.test_case" class="subtitle-1 text-center">
              {{ dialogData.test_case }}
            </p>
            <p v-if="dialogData.test_type" class="title">
              Type :
              <v-chip class="ma-2" color="indigo" text-color="white">
                {{ dialogData.test_type }}
              </v-chip>
            </p>
            <p v-if="dialogData.tools.length > 0" class="title">
              Tools : {{ dialogData.tools.toString() }}
            </p>
            <v-chip class="ma-2" color="green" text-color="white" v-if="dialogData.executed">
                Test Case Excuted
              </v-chip>
          </v-card-text>
        </v-card>
      </v-card>
    </v-navigation-drawer>
  </div>
</template>
<script>
import { mapActions, mapGetters } from 'vuex'
export default {
  layout: 'main',
  name: 'ThreatMap',
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
      drawer: false,
      chartData: {},
      dialogData: '',
      asvsData: [],
      relatedVuls: []
    }
  },
  created() {
    this.projectName = this.$route.params.name
     const data = {
      project : this.projectName
    }
    this.fetchThreatMapbyProject(data)
    // this.fetchThreatMapInfo()
  },
  methods: {
    ...mapActions('threatmap', ['fetchThreatMapbyProject']),
    ...mapActions('vulnerability', ['fetchASVSbyProject']),
    nodeClick(event) {
      if (!this.drawer) {
        this.drawer = true
      }
      this.dialogData = ''
      this.asvsData = []
      this.relatedVuls = []
      this.dialogData = event
      if (event.type === 'Scenarios') {
          const data = {
            cwe: parseInt(event.cwe)
          }
          this.fetchASVSbyProject(data)
      }
    },
    
  },
  computed: {
    ...mapGetters('threatmap', {
      getThreatMapProjectData: 'getThreatMapProjectData'
    }),
    ...mapGetters('vulnerability', {
      getASVSData: 'getASVSData'
    }),
  }
}
</script>
<style>
.orgchart-container {
  height: 620px;
  width: calc(100% - 24px);
  border: none;
}
</style>
