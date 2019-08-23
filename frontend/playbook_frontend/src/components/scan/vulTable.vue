<template>
    <div>

       <el-table
          :data="vulData"
          style="width: 100%">
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
         <el-table-column
        fixed="right"
        label="Operations"
        width="120">
           <template slot-scope="scope">
           <el-tooltip class="item" effect="dark" content="View" placement="top">
          <el-button type="text" size="small" @click="viewClick(scope.row)">
            <i class="el-icon-position" style="font-size: 16px;"></i></el-button>
          </el-tooltip>
           </template>
         </el-table-column>
        </el-table>

      <el-drawer
      title="Vunerability Information"
      :visible.sync="dialog"
      direction="ltr"
      size="80%">
        <div class="ex1">
          <span style="margin-left: 3%;font-family: Avenir, Helvetica, sans-serif;font-size: 16px;color: #6b7784" v-if="data.name">Name :</span>
          <p style="margin-left: 5%;font-family: Avenir, Helvetica, sans-serif;font-size: 14px;color: #6b7784" v-if="data.name"> {{ data.name }} </p>
         <el-row :gutter="20">
            <el-col :span="6">
              <p style="margin-left: 5%;font-family: Avenir, Helvetica, sans-serif;font-size: 14px;color: #6b7784" v-if="data.cwe">
              <span style="margin-left: 3%;font-family: Avenir, Helvetica, sans-serif;font-size: 16px;color: #6b7784" v-if="data.cwe">CWE :</span>

                {{ data.cwe }}</p>

            </el-col>
            <el-col :span="8">
              <p style="margin-left: 5%;" v-if="data.severity">
              <span style="margin-left: 3%;font-family: Avenir, Helvetica, sans-serif;font-size: 16px;color: #6b7784" v-if="data.severity">Severity :</span>
                <span class="label-high" v-if="data.severity === 4">High</span>
                <span class="label-high" v-if="data.severity === 3">High</span>
                <span class="label-medium" v-if="data.severity === 2"
                >Medium</span>
                <span class="label-low" v-if="data.severity === 1"
                >Low</span>
              </p>
            </el-col>
           <el-col :span="6">
             <p style="margin-left: 5%;font-family: Avenir, Helvetica, sans-serif;font-size: 14px;color: #6b7784" v-if="data.tool">
              <span style="margin-left: 3%;font-family: Avenir, Helvetica, sans-serif;font-size: 16px;color: #6b7784" v-if="data.tool">Tool :</span>
                {{ data.tool }}</p>
           </el-col>
          </el-row>
        <span style="margin-left: 3%;font-family: Avenir, Helvetica, sans-serif;font-size: 16px;color: #6b7784" v-if="data.description">Description :</span>
          <p style="margin-left: 5%;font-family: Avenir, Helvetica, sans-serif;font-size: 14px;color: #6b7784" v-if="data.description"> {{ data.description }} </p>
        <span style="margin-left: 3%;font-family: Avenir, Helvetica, sans-serif;font-size: 16px;color: #6b7784" v-if="data.remediation">Remediation :</span>
          <p style="margin-left: 5%;font-family: Avenir, Helvetica, sans-serif;font-size: 14px;color: #6b7784" v-if="data.remediation"> {{ data.remediation }} </p>
        <span style="margin-left: 3%;font-family: Avenir, Helvetica, sans-serif;font-size: 16px;color: #6b7784" v-if="data.observation">Observation :</span>
          <p style="margin-left: 5%;font-family: Avenir, Helvetica, sans-serif;font-size: 14px;color: #6b7784" v-if="data.observation"> {{ data.observation }} </p>

        <br>
        <template v-if="asvsData.length > 0 && data.cwe !== 0 ">
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
import axios from '../../utils/auth'
export default {
  name: 'vulTable',
  props: {
    vulData: {
      required: false
    }
  },
  data () {
    return {
      dialog: false,
      data: '',
      cwe: 0,
      asvsData: ''
    }
  },
  methods: {
    viewClick (data) {
        this.cwe = 0
        this.cwe = data.cwe
      if (this.cwe > 0) {
        const cweNumber = parseInt(this.cwe)
       axios.post('/graph', {
          query: '{\n' +
                        'asvsByCwe(cwe:' + cweNumber + '){\n' +
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
            if(res.data.data.asvsByCwe.length > 0){
                this.asvsData = ''
            this.asvsData = (res.data.data.asvsByCwe)
            }
          })
          .catch(error => {
          })
      }
      this.dialog = true
      this.data = ''
      this.data = data
    }
  }
}
</script>

<style  scoped>

.label-high {
        width: 60px;
        border-radius: 0;
        text-shadow: none;
        font-size: 11px;
        font-weight: 600;
        padding: 3px 5px 3px;
        text-align: center;
        color: #FFFFFF;
        background-color: #d11d55 !important
    }

    .label-medium {
        width: 60px;
        border-radius: 0;
        text-shadow: none;
        font-size: 11px;
        font-weight: 600;
        padding: 3px 5px 3px;
        text-align: center;
        color: #FFFFFF;
        background-color: #ff9c2c !important
    }

    .label-low {
        width: 60px;
        border-radius: 0;
        text-shadow: none;
        font-size: 11px;
        font-weight: 600;
        padding: 3px 5px 3px;
        text-align: center;
        color: #FFFFFF;
        background-color: #008b8f !important
    }
div.ex1 {
  /*background-color: lightblue;*/
  width: 100%;
  height: 100vh;
  overflow: scroll;
}
</style>
