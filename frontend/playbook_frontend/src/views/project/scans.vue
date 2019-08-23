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
          <el-breadcrumb-item>Scans</el-breadcrumb-item>
        </el-breadcrumb>
        <br>
        <br>
        <span style="float: left;font-family: Avenir, Helvetica, sans-serif;font-size: 16px;color: #6b7784">  Name : {{ actual_project_name }} </span>
        <br>
        <br>
        <el-card class="box-card">
          <div slot="header" class="clearfix">
            <span class="title" style="float: left;font-family: Avenir, Helvetica, sans-serif;font-size: 16px;color: #6b7784">Scans</span>
          </div>
          <scan-table :tableData="scanData" @viewScan="viewScan($event)"></scan-table>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script>
import navBarIndex from '@/components/navbar/index'
import sidebar from '@/components/navbar/sidebar'
import scanTable from '@/components/scan/scanTable'
import axios from '../../utils/auth'

export default {
  name: 'scans',
  components: {
    sidebar,
    navBarIndex,
    scanTable
  },
  data () {
    return {
      chartData: [],
      scanData: []
    }
  },
  created () {
    this.project_name = this.$route.params.projectName
    this.actual_project_name = atob(this.$route.params.projectName)
    this.getAllScans()
  },
  methods: {
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
          this.scanData = []
          for (const scans of res.data.data.tgtByProject) {
            for (const scan of scans.scans) {
              // this.scan_count.push(scan.name)
              this.scanData.push({
                name: scan.name
              })
            }
          }
        })
        .catch(error => {
          console.log('Error', error)
        })
    },
    viewScan (event) {
      this.$router.push('/scan/' + btoa(event.name) + '/' + this.project_name)
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
  }
</style>
