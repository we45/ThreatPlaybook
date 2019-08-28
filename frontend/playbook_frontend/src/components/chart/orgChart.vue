<template>
  <div>
    <Container :datasource="chartData" @node-click="test_user($event)" :pan="pan" :zoom="zoom"></Container>

    <el-drawer
      :title="dialogData.type"
      :visible.sync="dialog"
      direction="rtl"
      size="60%">
      <div class="ex1">
      <br>
      <br>
      <br>
      <span style="margin-left: 3%;">{{ dialogData.type }}  Name : </span>
      <p style="margin-left: 5%;"> {{ dialogData.name }} </p>
      <el-divider></el-divider>
      <span style="margin-left: 3%;">Description:</span>
      <p style="margin-left: 5%;">{{ dialogData.title }}</p>
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
      </div>
    </el-drawer>
  </div>
</template>

<script>
import Container from '@/components/chart/OrganizationChartContainer'
import axios from '../../utils/auth'
export default {
  name: 'orgChart',
  components: {
    // OrganizationChart,
    Container
  },
  props: {
    chartData: {
      required: false,
      default: {}
    }
  },
  data () {
    return {
      pan: true,
      zoom: false,
      dialog: false,
      dialogData: '',
      asvsData: ''
    }
  },
  methods: {
    test_user (data) {
      this.dialog = true
      this.dialogData = ''
      this.dialogData = data
      if (data.type === 'Scenarios') {
        console.log('From Modal =>', data.cwe)
        axios.post('/graph', {
          query: '{\n' +
                        'asvsByCwe(cwe:' + data.cwe + '){\n' +
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
  }
}
</script>

<style scoped>
  div.ex1 {
  /*background-color: lightblue;*/
  width: 100%;
  height: 100vh;
  overflow: scroll;
    margin-bottom: 2%;
}
</style>
