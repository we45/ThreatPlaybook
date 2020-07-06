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
        v-text="'Abuser Story of ' + projectName"
      ></v-card-title>
    </v-card>
    <br />
    <v-card>
      <v-treeview
        v-model="tree"
        hoverable
        :items="getAbuserStoryProjectTree"
        activatable
        item-key="name"
      >
        <template slot="label" slot-scope="{ item }">
          <a @click="openDialog(item)">{{ item.name }}</a>
        </template>
      </v-treeview>
    </v-card>
    <v-navigation-drawer v-model="drawer" absolute temporary right width="70%">
      <br />
      <h4 class="display-1 text-center" v-text="title"></h4>
      <!-- <v-list-item>
        <v-list-item-content>
          <v-list-item-title>{{ title }}</v-list-item-title>
        </v-list-item-content>
      </v-list-item>-->

      <br />
      <v-divider></v-divider>
      <v-card>
        <v-card-title
          class="display-1 justify-center"
          v-text="name"
        ></v-card-title>
        <v-card-text v-if="description">{{ description }}</v-card-text>
        <v-divider></v-divider>
        <v-card-text v-if="type === 'sce'">
          <v-row>
            <v-col cols="10">
              <h4 v-if="vulName" class="headline">{{ vulName }}</h4>
              <br />
              <p v-if="vulName" class="subtitle-1">CWE : {{ cwe }}</p>
            </v-col>
            <v-col cols="2">
              <v-chip
                v-if="sev === 'High'"
                class="ma-2"
                color="#d11d55"
                text-color="white"
                >{{ sev }}</v-chip
              >
              <v-chip
                v-if="sev === 'Medium'"
                class="ma-2"
                color="#ff9c2c"
                text-color="white"
                >{{ sev }}</v-chip
              >
              <v-chip
                v-if="sev === 'Low'"
                class="ma-2"
                color="#008b8f"
                text-color="white"
                >{{ sev }}</v-chip
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
          <!-- <p class="title" v-if="mitigations.length > 0">Mitigation</p>
          <v-simple-table v-if="mitigations.length > 0">
            <template v-slot:default>
              <thead>
                <tr>
                  <th class="text-left">Phase</th>
                  <th class="text-left">Strategy</th>
                  <th class="text-left">Description</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="item in mitigations" :key="item.id">
                  <td>{{ item.phase }}</td>
                  <td>{{ item.strategy }}</td>
                  <td>{{ item.description }}</td>
                </tr>
              </tbody>
            </template>
          </v-simple-table>-->
          <!-- <p v-if="mitigations.length > 0" class="subtitle-1">
            Mitigations: {{ mitigations }}
          </p>-->
        </v-card-text>
        <!-- Test Cases -->
        <v-card v-if="type === 'tc'">
          <v-card-text>
            <p v-if="testCase" class="subtitle-1 text-center">{{ testCase }}</p>
            <p v-if="testType" class="title">
              Type :
              <v-chip class="ma-2" color="indigo" text-color="white">
                {{ testType }}
              </v-chip>
            </p>
            <p v-if="tools.length > 0" class="title">
              Tools : {{ tools.toString() }}
            </p>
            <v-chip class="ma-2" color="green" text-color="white" v-if="isExecuted">
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
      chartData: [],
      drawer: false,
      items: [
        { title: 'Home', icon: 'dashboard' },
        { title: 'About', icon: 'question_answer' }
      ],
      type: '',
      title: '',
      description: '',
      vulName: '',
      sev: '',
      cwe: '',
      mitigations: [],
      relatedVuls: [],
      testCase: '',
      testType: '',
      tools: [],
      asvsData: [],
      isExecuted: false
    }
  },
  created() {
    this.projectName = this.$route.params.name
    const data = {
      project : this.projectName
    }
    this.fetchAbuserStoryTreeByProject(data)
  },
  methods: {
    ...mapActions('abuserStory', ['fetchAbuserStoryTreeByProject']),
    ...mapActions('vulnerability', ['fetchASVSbyProject']),
    openDialog(event) {
      if (!this.drawer) {
        this.drawer = true
      }
      this.type = ''
      this.title = ''
      this.name = ''
      this.vulName = ''
      this.sev = ''
      this.cwe = ''
      this.mitigations = []
      this.relatedVuls = []
      this.asvsData = []
      this.testType = ''
      this.tools = ''
      this.type = event.type
      this.title = event.title
      this.name = event.name
      this.description = event.description
      if (event.type === 'sce') {
        if (event.vul_name) {
          this.vulName = event.vul_name
        }
        if (event.severity === 3) {
          this.sev = 'High'
        } else if (event.severity === 2) {
          this.sev = 'Medium'
        } else {
          this.sev = 'Low'
        }
        this.cwe = event.cwe
          const data = {
            cwe: parseInt(event.cwe)
          }
          this.fetchASVSbyProject(data)
        if (event.mitigations) {
          this.mitigations = event.mitigations
        }
      }
      if (event.type === 'tc') {
        if (event.test_case) {
          this.testCase = event.test_case
        }
        if (event.test_type) {
          this.testType = event.test_type
        }
        if (event.tools) {
          this.tools = event.tools
        }
        this.isExecuted = event.executed
      }
    },
  },
  computed: {
    ...mapGetters('abuserStory', {
      getAbuserStoryProjectTree: 'getAbuserStoryProjectTree'
    }),
    ...mapGetters('vulnerability', {
      getASVSData: 'getASVSData'
    }),
  }
}
</script>
