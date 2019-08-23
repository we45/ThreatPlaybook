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
          <el-breadcrumb-item>Home</el-breadcrumb-item>
        </el-breadcrumb>
        <br>
        <br>

        <!--      Content from here-->

        <dash-box :projectCount="dashboardQuery.projects.length"
                  :user_story_count="dashboardQuery.userStories.length"
                  :threat_scenario_count="dashboardQuery.scenarios.length"
                  :scan_count="dashboardQuery.scans.length">
        </dash-box>

        <br>
        <el-row :gutter="20">
          <el-col :span="12">
            <p class="title">Threat model severity</p>
            <hr>
            <apexchart type="donut" :options="donutOptions" :series="donutSeries" height="300"></apexchart>
          </el-col>
          <el-col :span="12">
            <p class="title">Vulnerabilities by Severity</p>
            <hr>
            <apexchart type="pie" :options="pieOptions" :series="pieSeries" height="300"></apexchart>
          </el-col>
        </el-row>
        <br>
        <br>
      </el-col>
    </el-row>
  </div>
</template>

<script>

import navBarIndex from '@/components/navbar/index'
import sidebar from '@/components/navbar/sidebar'
import dashBox from '@/components/dashboard/dashBox'
import gql from 'graphql-tag'
// import { GET_ALL_USERS_QUERY } from '../../gql_queries/dashboard'

export default {
  name: 'homeIndex',
  components: {
    sidebar,
    navBarIndex,
    dashBox
  },
  data () {
    return {
      donutOptions: {
        labels: ['High', 'Medium', 'Low'],
        colors: ['#d11d55', '#ff9c2c', '#008b8f']
      },
      donutSeries: [],
      pieOptions: {
        labels: ['High', 'Medium', 'Low'],
        colors: ['#d11d55', '#ff9c2c', '#008b8f']
      },
      pieSeries: [],
      projectCount: 0,
      dashboardQuery: [],
      isData: false
    }
  },
  mounted () {
    this.token = sessionStorage.getItem('token')
    this.fetchData()
    // if (this.isData) {
    if (this.dashboardQuery.scenarios) {
      const highCount = []
      const mediumCount = []
      const lowCount = []
      for (const a of this.dashboardQuery.scenarios) {
        if (a.severity === 3) {
          highCount.push(a.severity)
        } else if (a.severity === 2) {
          mediumCount.push(a.severity)
        } else {
          lowCount.push(a.severity)
        }
      }
      this.donutSeries.push(highCount.length)
      this.donutSeries.push(mediumCount.length)
      this.donutSeries.push(lowCount.length)
      this.isData = false
    }
    if (this.dashboardQuery.scans) {
      const highPieCount = []
      const mediumPieCount = []
      const lowPieCount = []
      for (const scan of this.dashboardQuery.scans) {
        for (const vulSev of scan.vulnerabilities) {
          if (vulSev.severity === 3) {
            highPieCount.push(vulSev.severity)
          } else if (vulSev.severity === 2) {
            mediumPieCount.push(vulSev.severity)
          } else {
            lowPieCount.push(vulSev.severity)
          }
        }
      }
      this.pieSeries.push(highPieCount.length)
      this.pieSeries.push(mediumPieCount.length)
      this.pieSeries.push(lowPieCount.length)
    }
    // }
  },
  created () {
    this.getChartData()
  },
  updated () {
    this.$nextTick(() => {
      this.getChartData()
    })
  },
  apollo: {
    dashboardQuery: {
      query: gql`
            query {
              projects{
              name
            }
              userStories{
                id
              }
              scenarios{
                severity
              }
              scans {
                name
                vulnerabilities{
                  severity
                }
              }
        }
      `,
      update: result => result
    }
  },
  methods: {
    fetchData () {
      this.isData = true
    },
    goToProject () {
      this.$router.push('/projects')
    },

    getChartData () {
      if (this.isData) {
        if (this.dashboardQuery.scenarios) {
          const highCount = []
          const mediumCount = []
          const lowCount = []
          for (const a of this.dashboardQuery.scenarios) {
            if (a.severity === 3) {
              highCount.push(a.severity)
            } else if (a.severity === 2) {
              mediumCount.push(a.severity)
            } else {
              lowCount.push(a.severity)
            }
          }
          this.donutSeries.push(highCount.length)
          this.donutSeries.push(mediumCount.length)
          this.donutSeries.push(lowCount.length)
          this.isData = false
        }
        if (this.dashboardQuery.scans) {
          const highPieCount = []
          const mediumPieCount = []
          const lowPieCount = []
          for (const scan of this.dashboardQuery.scans) {
            for (const vulSev of scan.vulnerabilities) {
              if (vulSev.severity === 3) {
                highPieCount.push(vulSev.severity)
              } else if (vulSev.severity === 2) {
                mediumPieCount.push(vulSev.severity)
              } else {
                lowPieCount.push(vulSev.severity)
              }
            }
          }
          this.pieSeries.push(highPieCount.length)
          this.pieSeries.push(mediumPieCount.length)
          this.pieSeries.push(lowPieCount.length)
        }
      }
    }
  }
  // async mounted () {
  //   this.users = await this.$apollo.query({ query: GET_ALL_USERS_QUERY })
  //   if (await this.users.length > 0) {
  //     console.log('this.users', this.users)
  //   }
  // }

}
</script>

<style scoped>
  .title {
    font-size: 14px;
    line-height: 1.33;
    color: #6b7784;
    text-align: left;
  }

  .dash-box {
    position: relative;
    background: rgb(255, 86, 65);
    background: -moz-linear-gradient(top, rgba(255, 86, 65, 1) 0%, rgba(253, 50, 97, 1) 100%);
    background: -webkit-linear-gradient(top, rgba(255, 86, 65, 1) 0%, rgba(253, 50, 97, 1) 100%);
    background: linear-gradient(to bottom, rgba(255, 86, 65, 1) 0%, rgba(253, 50, 97, 1) 100%);
    filter: progid:DXImageTransform.Microsoft.gradient(startColorstr='#ff5641', endColorstr='#fd3261', GradientType=0);
    border-radius: 4px;
    text-align: center;
    margin: 60px 0 50px;
  }

  .dash-box-icon {
    position: absolute;
    transform: translateY(-50%) translateX(-50%);
    left: 50%;
  }

  .dash-box-action {
    transform: translateY(-50%) translateX(-50%);
    position: absolute;
    left: 50%;
  }

  .dash-box-body {
    padding: 50px 20px;
  }

  .dash-box-icon:after {
    width: 60px;
    height: 60px;
    position: absolute;
    background: rgba(247, 148, 137, 0.91);
    content: '';
    border-radius: 50%;
    left: -10px;
    top: -10px;
    z-index: -1;
  }

  .dash-box-icon > i {
    background: #ff5444;
    border-radius: 50%;
    line-height: 40px;
    color: #FFF;
    width: 40px;
    height: 40px;
    font-size: 22px;
  }

  .dash-box-icon:before {
    width: 75px;
    height: 75px;
    position: absolute;
    background: rgba(253, 162, 153, 0.34);
    content: '';
    border-radius: 50%;
    left: -17px;
    top: -17px;
    z-index: -2;
  }

  .dash-box-action > button {
    border: none;
    background: #FFF;
    border-radius: 19px;
    padding: 7px 16px;
    text-transform: uppercase;
    font-weight: 500;
    font-size: 11px;
    letter-spacing: .5px;
    color: #003e85;
    box-shadow: 0 3px 5px #d4d4d4;
  }

  .dash-box-body > .dash-box-count {
    display: block;
    font-size: 30px;
    color: #FFF;
    font-weight: 300;
  }

  .dash-box-body > .dash-box-title {
    font-size: 13px;
    color: rgba(255, 255, 255, 0.81);
  }

  .dash-box.dash-box-color-2 {
    background: rgb(252, 190, 27);
    background: -moz-linear-gradient(top, rgba(252, 190, 27, 1) 1%, rgba(248, 86, 72, 1) 99%);
    background: -webkit-linear-gradient(top, rgba(252, 190, 27, 1) 1%, rgba(248, 86, 72, 1) 99%);
    background: linear-gradient(to bottom, rgba(252, 190, 27, 1) 1%, rgba(248, 86, 72, 1) 99%);
    filter: progid:DXImageTransform.Microsoft.gradient(startColorstr='#fcbe1b', endColorstr='#f85648', GradientType=0);
  }

  .dash-box-color-2 .dash-box-icon:after {
    background: rgba(254, 224, 54, 0.81);
  }

  .dash-box-color-2 .dash-box-icon:before {
    background: rgba(254, 224, 54, 0.64);
  }

  .dash-box-color-2 .dash-box-icon > i {
    background: #fb9f28;
  }

  .dash-box.dash-box-color-3 {
    background: rgb(183, 71, 247);
    background: -moz-linear-gradient(top, rgba(183, 71, 247, 1) 0%, rgba(108, 83, 220, 1) 100%);
    background: -webkit-linear-gradient(top, rgba(183, 71, 247, 1) 0%, rgba(108, 83, 220, 1) 100%);
    background: linear-gradient(to bottom, rgba(183, 71, 247, 1) 0%, rgba(108, 83, 220, 1) 100%);
    filter: progid:DXImageTransform.Microsoft.gradient(startColorstr='#b747f7', endColorstr='#6c53dc', GradientType=0);
  }

  .dash-box-color-3 .dash-box-icon:after {
    background: rgba(180, 70, 245, 0.76);
  }

  .dash-box-color-3 .dash-box-icon:before {
    background: rgba(226, 132, 255, 0.66);
  }

  .dash-box-color-3 .dash-box-icon > i {
    background: #8150e4;
  }

  .dash-box.dash-box-color-4 {
    background: rgb(183, 71, 247);
    background: -moz-linear-gradient(top, rgba(0, 128, 0) 0%, rgba(0, 255, 64) 100%);
    background: -webkit-linear-gradient(top, rgba(0, 128, 0) 0%, rgba(0, 255, 128, 1) 100%);
    background: linear-gradient(to bottom, rgba(0, 128, 0) 0%, rgba(0, 255, 128, 1) 100%);
    filter: progid:DXImageTransform.Microsoft.gradient(startColorstr='#b747f7', endColorstr='#6c53dc', GradientType=0);
  }

  .dash-box-color-4 .dash-box-icon:after {
    background: rgba(191, 255, 0, 0.76);
  }

  .dash-box-color-4 .dash-box-icon:before {
    background: rgba(64, 255, 0, 0.66);
  }

  .dash-box-color-4 .dash-box-icon > i {
    background: #00ff00;
  }
</style>
