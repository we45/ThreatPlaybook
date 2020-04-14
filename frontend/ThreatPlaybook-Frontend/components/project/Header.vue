<template>
  <div>
    <v-card>
      <v-card-title
        class="display-2 justify-center"
        v-text="name"
      ></v-card-title>
      <v-card-text class="grey lighten-5 text-right">
        <v-btn color="primary" @click="viewThreatMap()">Threat Map</v-btn>
      </v-card-text>
    </v-card>
    <br />
    <v-row>
      <v-col cols="3">
        <v-card @click.native="viewUserStory()">
          <div class="d-flex flex-no-wrap justify-space-between">
            <div>
              <v-card-title
                class="subtitle-1"
                v-text="'User Stories'"
              ></v-card-title>
              <h2 class="display-1 text-center" v-text="userStoryCount"></h2>
              <br />
            </div>
          </div>
        </v-card>
      </v-col>
      <!-- Abuser Stories -->
      <v-col cols="3">
        <v-card @click.native="viewAbuserStory()">
          <div class="d-flex flex-no-wrap justify-space-between">
            <div>
              <v-card-title
                class="subtitle-1"
                v-text="'Abuser Stories'"
              ></v-card-title>
              <h2 class="display-1 text-center" v-text="abuseCount"></h2>
              <br />
            </div>
          </div>
        </v-card>
      </v-col>
      <!-- Threat Scenario -->
      <v-col cols="3">
        <v-card @click.native="viewThreatScenario()">
          <div class="d-flex flex-no-wrap justify-space-between">
            <div>
              <v-card-title
                class="subtitle-1"
                v-text="'Threat Scenarios'"
              ></v-card-title>
              <h2
                class="display-1 text-center"
                v-text="threatScenarioCount"
              ></h2>
              <br />
            </div>
          </div>
        </v-card>
      </v-col>
      <!-- Test Cases -->
      <!-- <v-col cols="2">
        <v-card @click.native="viewTestCases()">
          <div class="d-flex flex-no-wrap justify-space-between">
            <div>
              <v-card-title
                class="subtitle-1"
                v-text="'Test Cases'"
              ></v-card-title>
              <h2 class="display-1 text-center" v-text="testCaseCount"></h2>
              <br />
            </div>
          </div>
        </v-card>
      </v-col> -->
      <!-- Scans -->
      <!-- <v-col cols="2">
        <v-card>
          <div class="d-flex flex-no-wrap justify-space-between">
            <div>
              <v-card-title class="subtitle-1" v-text="'Scans'"></v-card-title>
              <h2 class="display-1 text-center" v-text="scanCount"></h2>
              <br />
            </div>
          </div>
        </v-card>
      </v-col> -->
      <!-- Vulnerabilities -->
      <v-col cols="3">
        <v-card @click.native="viewVulnerabilities()">
          <div class="d-flex flex-no-wrap justify-space-between">
            <div>
              <v-card-title
                class="subtitle-1"
                v-text="'Vulnerabilities'"
              ></v-card-title>
              <h2 class="display-1 text-center" v-text="vulCount"></h2>
              <br />
            </div>
          </div>
        </v-card>
      </v-col>
    </v-row>
  </div>
</template>
<script>
export default {
  name: 'Header',
  props: {
    name: {
      required: true,
      type: String
    },
    userStoryCount: {
      required: true,
      type: Number,
      default: 0
    },
    abuseCount: {
      required: true,
      type: Number,
      default: 0
    },
    threatScenarioCount: {
      required: true,
      type: Number,
      default: 0
    },
    testCaseCount: {
      required: true,
      type: Number,
      default: 0
    },
    scanCount: {
      required: true,
      type: Number,
      default: 0
    },
    vulCount: {
      required: true,
      type: Number,
      default: 0
    }
  },
  methods: {
    viewThreatMap() {
      this.$emit('viewThreatMap', { view: true })
      // this.$router.push('/projects/' + name + '/threat-map')
    },
    viewUserStory() {
      this.$emit('viewUserStory', { view: true })
    },
    viewAbuserStory() {
      this.$emit('viewAbuserStory', { view: true })
    },
    viewThreatScenario() {
      this.$emit('viewThreatScenario', { view: true })
    },
    // viewTestCases() {
    //   this.$emit('viewTestCases', { view: true })
    // },
    viewVulnerabilities() {
      this.$emit('viewVulnerabilities', { view: true })
    }
  }
}
</script>
