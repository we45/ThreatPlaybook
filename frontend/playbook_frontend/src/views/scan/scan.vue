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
          <el-breadcrumb-item :to="{ path: '/scans/' + project_name }"> Scans</el-breadcrumb-item>
          <el-breadcrumb-item>Vulnerabilities</el-breadcrumb-item>
        </el-breadcrumb>
        <br>
        <br>
        <span style="float: left;font-family: Avenir, Helvetica, sans-serif;font-size: 16px;color: #6b7784"> Scan Name : {{ actual_scan_name }} </span>
        <br>
        <br>
        <el-card class="box-card">
          <div slot="header" class="clearfix">
            <span class="title" style="float: left;font-family: Avenir, Helvetica, sans-serif;font-size: 16px;color: #6b7784">List of Vulnerabilities</span>
          </div>
          <vul-table :vulData="vulData"></vul-table>
        </el-card>
      </el-col>
    </el-row>
    </div>
</template>

<script>
import navBarIndex from '@/components/navbar/index'
import sidebar from '@/components/navbar/sidebar'
import vulTable from '@/components/scan/vulTable'
import axios from '../../utils/auth'
export default {
  name: 'scan',
  components: {
    sidebar,
    navBarIndex,
    vulTable
  },
  data () {
    return {
      vulData: []
    }
  },
  created () {
    this.scan_name = this.$route.params.scanName
    this.project_name = this.$route.params.projectName
    this.actual_scan_name = atob(this.$route.params.scanName)
    this.getAllVuls()
  },
  methods: {
    getAllVuls () {
      const scanName = `"${this.actual_scan_name}"`
      axios.post('/graph', {
        query: '{\n' +
                        'vulsByScan(scanName:' + scanName + '){\n' +
                        'vulnerabilities{ \n' +
                        'name\n' +
                        'severity\n' +
                        'cwe\n' +
                        'tool\n' +
                        'description\n' +
                        'remediation\n' +
                        'observation\n' +

                        '}\n' +
                        '}\n' +
                        '}'
      })
        .then(res => {
          // this.scanVuls = res.data.data.vulsByScan
          this.vulData = res.data.data.vulsByScan.vulnerabilities
          // this.totalRows = this.items.length
        })
        .catch(error => {
        })
    }
  }
}
</script>

<style scoped>

</style>
