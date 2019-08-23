<template>
  <el-row :gutter="40" class="panel-group">
    <el-col :xs="4" :sm="4" :lg="4"  class="card-panel-col">
      <div class="card-panel" @click="userStoryView()">
        <div class="card-panel-icon-wrapper icon-message">
          <i class="el-icon-document-checked" style="font-size: 10px;"></i>
        </div>
        <div class="card-panel-description">
          <div class="card-panel-text">
          User Stories
          </div>
          {{ user_story_count }}
        </div>
      </div>
    </el-col>
    <el-col :xs="4" :sm="4" :lg="4"  class="card-panel-col">
      <div class="card-panel" @click="abuserStoryView()">
        <div class="card-panel-icon-wrapper icon-message">
          <i class="el-icon-document-checked" style="font-size: 10px;"></i>
        </div>
        <div class="card-panel-description">
          <div class="card-panel-text">
            Abuse Stories
          </div>
          {{ abuse_count }}
        </div>
      </div>
    </el-col>
    <el-col :xs="4" :sm="4" :lg="4"  class="card-panel-col">
      <div class="card-panel" @click="threatScenarioView()">
        <div class="card-panel-icon-wrapper icon-money">
         <i class="el-icon-share" style="font-size: 10px;"></i>
        </div>
        <div class="card-panel-description">
          <div class="card-panel-text">
            Threat Scenarios
          </div>
          {{ threat_scenario_count }}
        </div>
      </div>
    </el-col>
    <el-col :xs="4" :sm="4" :lg="4"  class="card-panel-col">
      <div class="card-panel" @click="testCasesView()">
        <div class="card-panel-icon-wrapper icon-money">
         <i class="el-icon-share" style="font-size: 10px;"></i>
        </div>
        <div class="card-panel-description">
          <div class="card-panel-text">
            Test Cases
          </div>
          {{ test_case_count }}
        </div>
      </div>
    </el-col>
    <el-col :xs="4" :sm="4" :lg="4"  class="card-panel-col">
      <div class="card-panel" @click="scansView()">
        <div class="card-panel-icon-wrapper icon-shopping">
          <i class="el-icon-s-marketing" style="font-size: 10px;"></i>
        </div>
        <div class="card-panel-description">
          <div class="card-panel-text">
            Scans
          </div>
          {{ scan_count }}
        </div>
      </div>
    </el-col>
    <el-col :xs="4" :sm="4" :lg="4"  class="card-panel-col">
      <div class="card-panel">
        <div class="card-panel-icon-wrapper icon-shopping">
          <i class="el-icon-s-marketing" style="font-size: 10px;"></i>
        </div>
        <div class="card-panel-description">
          <div class="card-panel-text">
            Vulnerabilities
          </div>
          {{ vul_count }}
        </div>
      </div>
    </el-col>
  </el-row>
</template>

<script>
export default {
  name: 'singleProjectDashBox',
  methods: {
    handleSetLineChartData (type) {
      this.$emit('handleSetLineChartData', type)
    },
    userStoryView () {
      this.$emit('userStoryView')
    },
      abuserStoryView () {
      this.$emit('abuserStoryView')
    },
      threatScenarioView () {
      this.$emit('threatScenarioView')
    },
      testCasesView () {
      this.$emit('testCasesView')
    },
      scansView () {
      this.$emit('scansView')
    }
  },
  props: {
    user_story_count: {
      default: 0
    },
    abuse_count: {
      default: 0
    },
    threat_scenario_count: {
      default: 0
    },
    test_case_count: {
      default: 0
    },
    scan_count: {
      default: 0
    },
    vul_count: {
      default: 0
    }
  }
}
</script>

<style lang="scss" scoped>
.panel-group {
  margin-top: 18px;

  .card-panel-col {
    margin-bottom: 32px;
  }

  .card-panel {
    height: 90px;
    cursor: pointer;
    font-size: 12px;
    position: relative;
    overflow: hidden;
    color: #666;
    background: #fff;
    box-shadow: 4px 4px 40px rgba(0, 0, 0, .05);
    border-color: rgba(0, 0, 0, .05);

    & {
      .card-panel-icon-wrapper {
        color: #fff;
      }

      .icon-people {
        background: #40c9c6;
        color: #fff;
      }

      .icon-message {
        background: #36a3f7;
        color: #fff;
      }

      .icon-money {
        background: #f4516c;
        color: #fff;
      }

      .icon-shopping {
        background: #34bfa3;
        color: #fff;
      }
    }

    .icon-people {
      color: #40c9c6;
      color: #fff;
    }

    .icon-message {
      color: #36a3f7;
      color: #fff;
    }

    .icon-money {
      color: #f4516c;
      color: #fff;
    }

    .icon-shopping {
      color: #34bfa3;
      color: #fff;
    }

    .card-panel-icon-wrapper {
      float: left;
      margin: 14px 0 0 14px;
      padding: 16px;
      transition: all 0.38s ease-out;
      border-radius: 6px;
    }

    .card-panel-icon {
      float: left;
      font-size: 48px;
    }

    .card-panel-description {
      float: right;
      font-weight: bold;
      margin: 26px;
      margin-left: 0px;
      font-family: Avenir, Helvetica, sans-serif;

      .card-panel-text {
        line-height: 4px;
        color: rgba(0, 0, 0, 0.45);
        font-size: 12px;
        margin-bottom: 12px;
        font-family: Avenir, Helvetica, sans-serif;
      }

      .card-panel-num {
        font-size: 20px;
      }
    }
  }
}

@media (max-width:550px) {
  .card-panel-description {
    display: none;
  }

  .card-panel-icon-wrapper {
    float: none !important;
    width: 100%;
    height: 100%;
    margin: 0 !important;

    .svg-icon {
      display: block;
      margin: 14px auto !important;
      float: none !important;
    }
  }
}
</style>
