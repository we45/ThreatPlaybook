<template>
  <div>
    <nav-bar-index></nav-bar-index>
    <br>
    <el-row :gutter="20">
      <el-col :span="2">
        <sidebar></sidebar>
      </el-col>
      <el-col :span="22">
        <el-breadcrumb separator-class="el-icon-arrow-right">
          <el-breadcrumb-item :to="{ path: '/home' }">Home</el-breadcrumb-item>
          <el-breadcrumb-item :to="{ path: '/project' }">Projects</el-breadcrumb-item>
          <el-breadcrumb-item>{{ actual_project_name }}</el-breadcrumb-item>
        </el-breadcrumb>
        <br>
        <br>
        <el-row>
          <el-col :span="12">
            <span style="float: left;" class="headerStyle">  Name : {{ actual_project_name }} </span>
          </el-col>
          <el-col :span="12">
            <el-button type="primary" round style="float: right;margin-right: 2%;" @click="viewUserStoryMap()">User Story Map</el-button>
            <el-button type="primary" round style="float: right; margin-right: 2%;" @click="viewThreatMap()">Threat
              Map
            </el-button>
          </el-col>
        </el-row>
        <el-divider></el-divider>
        <single-project-dash-box :user_story_count="user_story_count.length"
                                 :abuse_count="abuse_count.length"
                                 :threat_scenario_count="threat_scenario_count.length"
                                 :test_case_count="test_case_count.length"
                                 :scan_count="scan_count.length"
                                 :vul_count="vul_count.length"
                                 @userStoryView="userStoryView($event)"
                                 @abuserStoryView="abuserStoryView($event)"
                                 @threatScenarioView="threatScenarioView($event)"
                                 @testCasesView="testCasesView($event)"
                                 @scansView="scansView($event)"></single-project-dash-box>
        <br>
        <el-row :gutter="20">
          <el-col :span="8">
            <p class="title">Vulnerabilities by Severity</p>
            <el-divider></el-divider>
            <apexchart type="pie" :options="pieOptions" :series="pieSeries" height="300"></apexchart>
          </el-col>
          <el-col :span="16">
            <p class="title">List of Scans</p>
            <el-divider></el-divider>
            <scan-table :tableData="scanData" @viewScan="viewScan($event)"></scan-table>
          </el-col>

        </el-row>
      </el-col>
    </el-row>
  </div>
</template>

<script>
import navBarIndex from '@/components/navbar/index'
import sidebar from '@/components/navbar/sidebar'
import singleProjectDashBox from '@/components/project/singleProjectDashBox'
import scanTable from '@/components/scan/scanTable'
import axios from '../../utils/auth'

export default {
  name: 'singleProject',
  components: {
    sidebar,
    navBarIndex,
    singleProjectDashBox,
    scanTable
  },
  data () {
    return {
      user_story_count: [],
      abuse_count: [],
      threat_scenario_count: [],
      test_case_count: [],
      scan_count: [],
      vul_count: [],
      pieOptions: {
        labels: ['High', 'Medium', 'Low'],
        colors: ['#d11d55', '#ff9c2c', '#008b8f']
      },
      pieSeries: [],
      tableData: [{
        id: '1',
        name: 'test_project'
      }, {
        id: '2',
        name: 'Demo'
      }],
      scanData: []

    }
  },
  created () {
    this.project_name = this.$route.params.projectName
    this.actual_project_name = atob(this.$route.params.projectName)
    this.fetchGraphData()
    this.getAllScans()
  },
  methods: {
    userStoryView () {
      this.$router.push('/user_stories/' + this.project_name)
    },
    abuserStoryView () {
      this.$router.push('/abuser_stories/' + this.project_name)
    },
    threatScenarioView () {
      this.$router.push('/threat_scenarios/' + this.project_name)
    },
    testCasesView () {
      this.$router.push('/test_cases/' + this.project_name)
    },
    scansView () {
      this.$router.push('/scans/' + this.project_name)
    },
    viewThreatMap () {
      this.$router.push('/threat_map/' + this.project_name)
    },
    viewUserStoryMap () {
      this.$router.push('/user_story_map/' + this.project_name)
    },
    viewScan (event) {
      this.$router.push('/scan/' + btoa(event.name) + '/' + this.project_name)
    },
    async fetchGraphData () {
      const projName = `"${this.actual_project_name}"`
      axios.post('/graph', {
        query: '{\n' +
                        'userStoryByProject(project:' + projName + '){\n' +
                        'shortName\n' +
                        'abuses{ \n' +
                        'shortName\n' +
                        'models{ \n' +
                        'name\n' +
                        'severity\n' +
                        'tests{ \n' +
                        'name\n' +
                        'testCase\n' +
                        '}\n' +
                        '}\n' +
                        '}\n' +
                        '}\n' +
                        '}'
      })
        .then(res => {
          if (res.data.data.userStoryByProject.length > 0) {
            for (let singleFeature of res.data.data.userStoryByProject) {
              this.user_story_count.push(singleFeature.shortName)
              for (let singleAbuse of singleFeature.abuses) {
                this.abuse_count.push(singleAbuse.shortName)
                for (let singleScenario of singleAbuse.models) {
                  this.threat_scenario_count.push(singleScenario.name)
                  for (let singleTest of singleScenario.tests) {
                    this.test_case_count.push(singleTest.name)
                  }
                }
              }
            }
          }
        }).catch(error => {
          console.log('Error', error)
        })
    },
    async getAllScans () {
      const projName = `"${this.actual_project_name}"`
      axios
        .post('/graph', {
          query:
                            '{\n' +
                            'tgtByProject(project:' +
                            projName +
                            '){\n' +
                            'name \n' +
                            'scans{\n' +
                            'name\n' +
                            'vulnerabilities{\n' +
                            'name\n' +
                            'severity\n' +
                            '}\n' +
                            '}\n' +
                            '}' +
                            '}'
        })
        .then(res => {
          const highPieCount = []
          const mediumPieCount = []
          const lowPieCount = []
          for (const scans of res.data.data.tgtByProject) {
            for (const scan of scans.scans) {
              this.scan_count.push(scan.name)
              this.scanData.push({
                name: scan.name
              })
              for (const vulSev of scan.vulnerabilities) {
                this.vul_count.push(vulSev.name)
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
          this.pieSeries.push(highPieCount.length)
          this.pieSeries.push(mediumPieCount.length)
          this.pieSeries.push(lowPieCount.length)
        })
        .catch(error => {
          console.log('Error', error)
        })
    }
  }
}
</script>

<style scoped>
.title {
    font-size: 14px;
    line-height: 1.33;
    color: #6b7784;
    text-align: left;
    font-family: Avenir, Helvetica, sans-serif;
  }
  .headerStyle{
    font-size: 16px;
    color: #6b7784;
    font-family: Avenir, Helvetica, sans-serif;
  }
</style>
