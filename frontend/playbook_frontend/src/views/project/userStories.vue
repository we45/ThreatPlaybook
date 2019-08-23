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
          <el-breadcrumb-item>User Stories</el-breadcrumb-item>
        </el-breadcrumb>
        <br>
        <br>
        <span style="float: left;" class="headerStyle">  Name : {{ actual_project_name }} </span>
        <br>
        <br>
        <el-card class="box-card">
          <div slot="header" class="clearfix">
            <span class="title" style="float: left;">User Stories</span>
          </div>
          <user-story-tree-view :chartData="chartData" :projectActual="actual_project_name"></user-story-tree-view>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script>
import navBarIndex from '@/components/navbar/index'
import sidebar from '@/components/navbar/sidebar'
import userStoryTreeView from '@/components/userstories/userStoryTreeView'
import axios from '../../utils/auth'

export default {
  name: 'userStories',
  components: {
    sidebar,
    navBarIndex,
    userStoryTreeView
  },
  data () {
    return {
      chartData: []
    }
  },
  created () {
    this.project_name = this.$route.params.projectName
    this.actual_project_name = atob(this.$route.params.projectName)
    this.fetchData()
  },
  methods: {
    fetchData () {
      if (this.actual_project_name) {
        const project = `"${this.actual_project_name}"`
        axios
          .post('/graph', {
            query:
                                '{\n' +
                                'userStoryByProject(project:' +
                                project +
                                '){\n' +
                                'id \n' +
                                'shortName \n' +
                                'abuses{ \n' +
                                'id \n' +
                                'shortName \n' +
                                'models{ \n' +
                                'id \n' +
                                'name \n' +
                                'tests{ \n' +
                                'id \n' +
                                'name \n' +
                                'testCase \n' +
                                'testType \n' +
                                'tools \n' +
                                '} \n' +
                                '} \n' +
                                '} \n' +
                                '}\n' +
                                '}'
          })
          .then(res => {
            this.chartData = []
            for (var single of res.data.data.userStoryByProject) {
              var userStoryObj = {}
              userStoryObj = {
                'label': single.shortName,
                'children': [],
                'type': 'us',
                'title': 'User Story'
              }
              this.chartData.push(userStoryObj)
              for (var abuse of single.abuses) {
                var abuseObj = {}
                abuseObj = {
                  'label': abuse.shortName,
                  'children': [],
                  'type': 'as',
                  'title': 'Abuser Story'
                }
                userStoryObj['children'].push(abuseObj)
                if (single.abuses.length > 0) {
                  for (var scenario of abuse.models) {
                    var scenarioObj = {}
                    scenarioObj = {
                      'label': scenario.name,
                      'name': scenario.name,
                      'children': [],
                      'type': 'mod',
                      'title': 'Threat Scenario'
                    }
                    abuseObj['children'].push(scenarioObj)
                  }
                  if (abuse.models.length > 0) {
                    for (var test of scenario.tests) {
                      var testObj = {}
                      testObj = {
                        'label': test.name,
                        'title': 'Test Case',
                        'type': 'tm',
                        'testType': test.testType,
                        'testCase': test.testCase,
                        'tools': test.tools
                      }
                      scenarioObj['children'].push(testObj)
                    }
                  }
                }
              }
            }
          })
          .catch(error => {
            console.log('Error', error)
          })
      }
    }
  }
}
</script>

<style scoped>
.title {
    font-size: 18px;
    line-height: 0.50;
    color: #6b7784;
    text-align: left;
    font-family: Avenir, Helvetica, sans-serif;
  }
  headerStyle{
    font-size: 16px;
    font-family: Avenir, Helvetica, sans-serif;
  }
</style>
