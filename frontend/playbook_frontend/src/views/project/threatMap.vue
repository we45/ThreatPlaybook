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
          <el-breadcrumb-item :to="{ path: '/project/'+ project_name }">Project</el-breadcrumb-item>
          <el-breadcrumb-item>Threat Map</el-breadcrumb-item>
        </el-breadcrumb>
        <h3>{{ actual_project_name }}</h3>
        <org-chart :chartData="chartData"></org-chart>
        <br>
      </el-col>
    </el-row>
  </div>
</template>

<script>
import navBarIndex from '@/components/navbar/index'
import sidebar from '@/components/navbar/sidebar'
import orgChart from '@/components/chart/orgChart'
import axios from '../../utils/auth'

const uuidv1 = require('uuid/v1')

export default {
  name: 'threatMap',
  components: {
    sidebar,
    navBarIndex,
    orgChart
  },
  data () {
    return {
      chartData: {}
    }
  },
  created () {
    this.project_name = this.$route.params.projectName
    this.actual_project_name = atob(this.$route.params.projectName)
    this.fetchGraphData()
  },
  methods: {
    async fetchGraphData () {
      const projName = `"${this.actual_project_name}"`
      axios.post('/graph', {
        query: '{\n' +
                        'userStoryByProject(project:' + projName + '){\n' +
                        'shortName\n' +
                        'description\n' +
                        'abuses{ \n' +
                        'shortName\n' +
                        'description\n' +
                        'models{ \n' +
                        'name\n' +
                        'description\n' +
                        'cwe\n' +
                        'severity\n' +
                        'tests{ \n' +
                        'name\n' +
                        'testCase\n' +
                        'testType\n' +
                        '}\n' +
                        '}\n' +
                        '}\n' +
                        '}\n' +
                        '}'
      })
        .then(res => {
          this.chartData = {}
          this.chartData['id'] = 1
          this.chartData['name'] = this.actual_project_name
          this.chartData['children'] = []
          this.chartData['type'] = 'Project'
          if (res.data.data.userStoryByProject.length > 0) {
            for (let singleFeature of res.data.data.userStoryByProject) {
              var featureObj = {}
              let featureRandom = uuidv1()
              featureObj = {
                'id': featureRandom,
                'name': singleFeature.shortName,
                'title': singleFeature.description,
                'type': 'Feature',
                'children': []
              }
              this.chartData['children'].push(featureObj)
              // this.chartData['children'].push({'id': featureRandom, 'name': singleFeature.shortName, 'desc': singleFeature.description, 'children': []})
              for (let singleAbuse of singleFeature.abuses) {
                let abuseRandom = uuidv1()
                let abuseObj = {
                  'id': abuseRandom,
                  'name': singleAbuse.shortName,
                  'title': singleAbuse.description,
                  'type': 'Abuses',
                  'children': []
                }
                featureObj['children'].push(abuseObj)
                for (let singleScenario of singleAbuse.models) {
                  let sceneRandom = uuidv1()
                  let scenarioObj = {
                    'id': sceneRandom,
                    'name': singleScenario.name,
                    'title': singleScenario.description,
                    'type': 'Scenarios',
                    'children': []
                  }
                  abuseObj['children'].push(scenarioObj)
                  for (let singleTest of singleScenario.tests) {
                    let testRandom = uuidv1()
                    let testObj = {
                      'id': testRandom,
                      'name': singleTest.name,
                      'title': singleTest.testCase,
                      'type': 'Test Cases'
                    }
                    scenarioObj['children'].push(testObj)
                  }
                }
              }
            }
          }
        }).catch(error => {
          console.log('Error', error)
        })
    }
  }
}
</script>

<style scoped>

</style>
