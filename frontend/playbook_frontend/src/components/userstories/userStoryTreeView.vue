<template>
  <div>
    <el-tree :data="chartData" :props="defaultProps" @node-click="handleNodeClick($event)"></el-tree>
    <el-drawer
      :title="title"
      :visible.sync="dialog"
      direction="rtl"
      size="80%">
      <div class="ex1">
      <template v-if="selectedUserStory.length > 0">
        <template v-for="story in selectedUserStory">
          <span style="margin-left: 3%;font-family: Avenir, Helvetica, sans-serif;font-size: 16px;color: #6b7784" v-if="story.title || story.label">{{ story.title }} Name :</span>
          <p style="margin-left: 5%;font-family: Avenir, Helvetica, sans-serif;font-size: 14px;color: #6b7784" v-if="story.label"> {{ story.label }} </p>
          <el-divider></el-divider>
          <span style="margin-left: 3%;font-family: Avenir, Helvetica, sans-serif;font-size: 16px;color: #6b7784" v-if="story.desc">Description:</span>
          <p style="margin-left: 5%;font-family: Avenir, Helvetica, sans-serif;font-size: 14px;color: #6b7784;margin-right: 2%;" v-if="story.desc">{{ story.desc }}</p>
        </template>
      </template>

      <template v-if="selectedAbuserStory.length > 0">
        <template v-for="abusestory in selectedAbuserStory">
          <span style="margin-left: 3%;font-family: Avenir, Helvetica, sans-serif;font-size: 16px;color: #6b7784"
                v-if="abusestory.title || abusestory.label">{{ abusestory.title }} Name :</span>
          <p style="margin-left: 5%;font-family: Avenir, Helvetica, sans-serif;font-size: 14px;color: #6b7784" v-if="abusestory.label"> {{ abusestory.label }} </p>
          <el-divider></el-divider>
          <span style="margin-left: 3%;font-family: Avenir, Helvetica, sans-serif;font-size: 16px;color: #6b7784" v-if="abusestory.desc">Description:</span>
          <p style="margin-left: 5%;font-family: Avenir, Helvetica, sans-serif;font-size: 14px;color: #6b7784;margin-right: 2%" v-if="abusestory.desc">{{ abusestory.desc }}</p>
        </template>
      </template>

      <template v-if="selectedVulDetail.length > 0">
        <template v-for="scenarios in selectedVulDetail">
          <span style="margin-left: 3%;font-family: Avenir, Helvetica, sans-serif;font-size: 16px;color: #6b7784" v-if="scenarios.title || scenarios.label">{{ scenarios.title }} Name :</span>
          <p style="margin-left: 5%;font-family: Avenir, Helvetica, sans-serif;font-size: 14px;color: #6b7784" v-if="scenarios.label"> {{ scenarios.label }} </p>
<!--          <el-divider></el-divider>-->
          <span style="margin-left: 3%;font-family: Avenir, Helvetica, sans-serif;font-size: 16px;color: #6b7784" v-if="scenarios.desc">Description :</span>
          <p style="margin-left: 5%;font-family: Avenir, Helvetica, sans-serif;font-size: 14px;color: #6b7784;margin-right: 2%;" v-if="scenarios.desc">{{ scenarios.desc }}</p>
          <el-row :gutter="20">
            <el-col :span="10">
              <p style="margin-left: 5%;font-family: Avenir, Helvetica, sans-serif;font-size: 14px;color: #6b7784" v-if="scenarios.cwe">
              <span style="margin-left: 3%;font-family: Avenir, Helvetica, sans-serif;font-size: 16px;color: #6b7784" v-if="scenarios.cwe">CWE :</span>

                {{ scenarios.cwe }}</p>

            </el-col>
            <el-col :span="10">
              <p style="margin-left: 5%;" v-if="scenarios.severity">
              <span style="margin-left: 3%;font-family: Avenir, Helvetica, sans-serif;font-size: 16px;color: #6b7784" v-if="scenarios.severity">Severity :</span>
                <span class="label-high" v-if="scenarios.severity === 4">High</span>
                <span class="label-high" v-if="scenarios.severity === 3">High</span>
                <span class="label-medium" v-if="scenarios.severity === 2"
                >Medium</span>
                <span class="label-low" v-if="scenarios.severity === 1"
                >Low</span>
              </p>
            </el-col>
          </el-row>
          <span style="margin-left: 3%;font-family: Avenir, Helvetica, sans-serif;font-size: 18px;color: #6b7784"
                v-if="scenarios.mitigations.description">Mitigations :</span>
<!--          <p style="margin-left: 5%;">-->
<!--          <p v-if="scenarios.mitigations.phase" style="margin-left: 5%;font-family: Avenir, Helvetica, sans-serif;font-size: 16px;color: #6b7784"><b>Phase : </b>-->
<!--            <b-badge variant="info" style="margin-left: 5%;">{{ scenarios.mitigations.phase }}</b-badge>-->
<!--          </p>-->
<!--          <p v-if="scenarios.mitigations.strategy" style="margin-left: 5%;font-family: Avenir, Helvetica, sans-serif;font-size: 16px;color: #6b7784"><b>Strategy : </b>-->
<!--            <b-badge variant="success" pill style="margin-left: 5%;">{{ scenarios.mitigations.strategy }}-->
<!--            </b-badge>-->
<!--          </p>-->
<!--          <p v-if="scenarios.mitigations.description" style="margin-left: 5%;">-->
          <p style="font-family: Avenir, Helvetica, sans-serif;font-size: 16px;color: #6b7784; margin-left: 5%;" v-if="scenarios.mitigations.description"> <b>Description : </b></p>
           <p style="font-family: Avenir, Helvetica, sans-serif;font-size: 14px;color: #6b7784;margin-left: 5%; margin-right: 2%">
            {{ scenarios.mitigations.description }}
           </p>
<!--          </p>-->
        </template>
      </template>

      <template v-if="selectedRelatedVulDetail.length > 0">
        <h4 style="margin-left: 3%;font-family: Avenir, Helvetica, sans-serif;font-size: 18px;color: #6b7784">Vulnerabilities linked with threat scenario</h4>
        <el-divider></el-divider>
        <el-table
          :data="selectedRelatedVulDetail"
          style="width: 100%" height="250px">
          <el-table-column
            prop="name"
            label="Name"
            width="180">
          </el-table-column>
          <el-table-column
            prop="cwe"
            label="CWE"
            width="180">
          </el-table-column>
          <el-table-column
            prop="severity"
            label="Severity">
            <template slot-scope="scope">
              <span class="label-high" v-if="scope.row.severity === 4">High</span>
              <span class="label-high" v-if="scope.row.severity === 3">High</span>
              <span class="label-medium" v-if="scope.row.severity === 2"
              >Medium</span>
              <span class="label-low" v-if="scope.row.severity === 1"
              >Low</span>
            </template>
          </el-table-column>
          <el-table-column
            prop="tool"
            label="Tool">
          </el-table-column>
        </el-table>
      </template>

      <template v-if="asvsData.length > 0 ">
           <el-card class="box-card">
          <div slot="header" class="clearfix">
            <span class="title" style="float: left;font-family: Avenir, Helvetica, sans-serif;font-size: 16px;color: #6b7784">Related ASVS Information</span>
          </div>
          <el-table
      :data="asvsData"
      style="width: 100%;" height="350">
      <el-table-column
        prop="name"
        label="Name"
        width="180">
      </el-table-column>

            <el-table-column
        prop="description"
        label="Description" width="200">
      </el-table-column>
            <el-table-column
        prop="l1"
        label="L1">
              <template slot-scope="scope">
                <template v-if="scope.row.l1">
                  <el-tag type="info" effect="dark">L1</el-tag>
                </template>
                <template v-else>
                  -
                </template>
              </template>
      </el-table-column>
            <el-table-column
        prop="l2"
        label="L2">
              <template slot-scope="scope">
                <template v-if="scope.row.l2">
                  <el-tag type="info" effect="dark">L2</el-tag>
                </template>
                <template v-else>
                  -
                </template>
              </template>
      </el-table-column>
            <el-table-column
        prop="l3"
        label="L3">
              <template slot-scope="scope">
                <template v-if="scope.row.l3">
                  <el-tag type="info" effect="dark">L3</el-tag>
                </template>
                <template v-else>
                  -
                </template>
              </template>
      </el-table-column>

    </el-table>
           </el-card>
          </template>

      <template v-if="selectedTestCases.length > 0">
        <template v-for="test in selectedTestCases">
          <span style="margin-left: 3%; font-family: Avenir, Helvetica, sans-serif;font-size: 16px;color: #6b7784" v-if="test.title || test.label">{{ test.title }} Name :</span>
          <p style="margin-left: 5%;font-family: Avenir, Helvetica, sans-serif;font-size: 14px;color: #6b7784" v-if="test.label"> {{ test.label }} </p>
          <el-divider></el-divider>
          <span style="margin-left: 3%;font-family: Avenir, Helvetica, sans-serif;font-size: 16px;color: #6b7784" v-if="test.testCase">Test Case:</span>
          <p style="margin-left: 5%;font-family: Avenir, Helvetica, sans-serif;font-size: 14px;color: #6b7784" v-if="test.testCase">{{ test.testCase }}</p>
          <el-divider></el-divider>
          <span style="margin-left: 3%;font-family: Avenir, Helvetica, sans-serif;font-size: 16px;color: #6b7784" v-if="test.testType">Test Type:</span>
          <p style="margin-left: 5%;font-family: Avenir, Helvetica, sans-serif;font-size: 14px;color: #6b7784" v-if="test.testType">{{ test.testType }}</p>
          <el-divider></el-divider>
          <span style="margin-left: 3%;font-family: Avenir, Helvetica, sans-serif;font-size: 16px;color: #6b7784" v-if="test.tools">Tools:</span>
          <p style="margin-left: 5%;font-family: Avenir, Helvetica, sans-serif;font-size: 14px;color: #6b7784" v-if="test.tools">{{ test.tools.toString() }}</p>
        </template>
      </template>
      </div>
    </el-drawer>
  </div>
</template>

<script>
import axios from '../../utils/auth'

export default {
  name: 'userStoryTreeView',
  props: {
    chartData: {
      required: false,
      default: []
    },
    projectActual: {
      required: false
    }
  },
  data () {
    return {
      dialog: false,
      title: '',
      selectedUserStory: [],
      selectedAbuserStory: [],
      selectedVulDetail: [],
      asvsData: '',
      selectedTestCases: [],
      selectedRelatedVulDetail: [],
      defaultProps: {
        children: 'children',
        label: 'label'
      }
    }
  },
  methods: {
    handleNodeClick (data) {
      this.dialog = true
      this.selectedUserStory = []
      this.selectedAbuserStory = []
      this.selectedVulDetail = []
      this.selectedTestCases = []
      this.selectedRelatedVulDetail = []
      this.selectedNode = data
      if (this.selectedNode.type === 'us') {
        if (this.projectActual) {
          const project = `"${this.projectActual}"`
          axios
            .post('/graph', {
              query:
                                    '{\n' +
                                    'userStoryByProject(project:' +
                                    project +
                                    '){\n' +
                                    'id \n' +
                                    'shortName \n' +
                                    'description \n' +
                                    '}\n' +
                                    '}'
            })
            .then(res => {
              const singelresponseData = res.data.data.userStoryByProject
              for (const single of singelresponseData) {
                if (this.selectedNode.label === single.shortName) {
                  this.title = ''
                  this.title = this.selectedNode.title
                  this.selectedUserStory.push({
                    title: this.selectedNode.title,
                    label: this.selectedNode.label,
                    desc: single.description
                  })
                }
              }
            }).catch(error => {
            })
        }
      }

      if (this.selectedNode.type === 'as') {
        if (this.projectActual) {
          const project = `"${this.projectActual}"`
          axios
            .post('/graph', {
              query:
                                    '{\n' +
                                    'abuserStoryByProject(project:' +
                                    project +
                                    '){\n' +
                                    'id \n' +
                                    'shortName \n' +
                                    'description \n' +
                                    '}\n' +
                                    '}'
            })
            .then(res => {
              const singelresponseData = res.data.data.abuserStoryByProject
              for (const single of singelresponseData) {
                if (this.selectedNode.label === single.shortName) {
                  this.title = ''
                  this.title = this.selectedNode.title
                  this.selectedAbuserStory.push({
                    title: this.selectedNode.title,
                    label: this.selectedNode.label,
                    desc: single.description
                  })
                }
              }
            }).catch(error => {
            })
        }
      }

      if (this.selectedNode.type === 'mod') {
        const vulName = `"${this.selectedNode.name}"`
        axios
          .post('/graph', {
            query:
                                '{\n' +
                                'searchThreatScenario(name:' +
                                vulName +
                                '){\n' +
                                'name \n' +
                                'cwe \n' +
                                'severity \n' +
                                'mitigations \n' +
                                '}\n' +
                                '}'
          })
          .then(res => {
            const singelresponseData = res.data.data.searchThreatScenario
            for (const single of singelresponseData) {
              const mitigation = JSON.parse(single.mitigations[0])
              this.title = ''
              this.title = this.selectedNode.title
              this.selectedVulDetail.push({
                title: this.selectedNode.title,
                label: this.selectedNode.label,
                desc: single.description,
                cwe: single.cwe,
                severity: single.severity,
                mitigations: mitigation
              })
              if (single.cwe > 0) {
                const cweName = single.cwe
                axios
                  .post('/graph', {
                    query:
                                                '{\n' +
                                                'vulsByCwe(cwe:' +
                                                cweName +
                                                '){\n' +
                                                'cwe \n' +
                                                'name \n' +
                                                'severity \n' +
                                                'tool \n' +
                                                '}\n' +
                                                '}'
                  })
                  .then(res => {
                    const singelresponseVulData = res.data.data.vulsByCwe
                    for (const vul of singelresponseVulData) {
                      this.selectedRelatedVulDetail.push({
                        name: vul.name,
                        cwe: vul.cwe,
                        severity: vul.severity,
                        tool: vul.tool
                      })
                    }
                  }).catch(error => {
                  })
                axios.post('/graph', {
                  query: '{\n' +
                        'asvsByCwe(cwe:' + cweName + '){\n' +
                        'cwe\n' +
                        'description\n' +
                        'item\n' +
                        'l1\n' +
                        'l2\n' +
                        'l3\n' +
                        'name\n' +
                        'nist\n' +

                        '}\n' +
                        '}'
                })
                  .then(res => {
                    this.asvsData = ''
                    if (res.data.data.asvsByCwe.length > 0) {
                      this.asvsData = ''
                      this.asvsData = (res.data.data.asvsByCwe)
                    }
                  })
                  .catch(error => {
                  })
              }
            }
          }).catch(error => {
          })
      }

      if (this.selectedNode.type === 'tm') {
        this.title = ''
        this.title = this.selectedNode.title
        this.selectedTestCases.push({
          title: this.selectedNode.title,
          label: this.selectedNode.label,
          testCase: this.selectedNode.testCase,
          testType: this.selectedNode.testType,
          tools: this.selectedNode.tools
        })
      }
    }
  }
}
</script>

<style scoped>
  .label-high {
    width: 60px;
    border-radius: 0;
    text-shadow: none;
    font-size: 11px;
    font-weight: 600;
    padding: 3px 5px 3px;
    text-align: center;
    color: #ffffff;
    background-color: #d11d55 !important;
    font-family: Avenir, Helvetica, sans-serif;
  }

  .label-medium {
    width: 60px;
    border-radius: 0;
    text-shadow: none;
    font-size: 11px;
    font-weight: 600;
    padding: 3px 5px 3px;
    text-align: center;
    color: #ffffff;
    background-color: #ff9c2c !important;
    font-family: Avenir, Helvetica, sans-serif;
  }

  .label-low {
    width: 60px;
    border-radius: 0;
    text-shadow: none;
    font-size: 11px;
    font-weight: 600;
    padding: 3px 5px 3px;
    text-align: center;
    color: #ffffff;
    background-color: #008b8f !important;
    font-family: Avenir, Helvetica, sans-serif;
  }
  label-title{
    font-size: 14px;
    color: #6b7784;
    font-family: Avenir, Helvetica, sans-serif;
  }
  div.ex1 {
  /*background-color: lightblue;*/
  width: 100%;
  height: 100vh;
  overflow: scroll;
    margin-bottom: 2%;
}
</style>
