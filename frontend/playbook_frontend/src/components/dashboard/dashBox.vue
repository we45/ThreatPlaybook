<template>
  <el-row :gutter="40" class="panel-group">
    <el-col :xs="12" :sm="12" :lg="6" class="card-panel-col">
      <div class="card-panel" style="cursor: default;">
        <div class="card-panel-icon-wrapper icon-people">
          <i class="el-icon-money" style="font-size: 30px;"></i>
        </div>
        <div class="card-panel-description">
          <div class="card-panel-text">
            Projects
          </div>
          {{ projectCount }}
        </div>
      </div>
    </el-col>
    <el-col :xs="12" :sm="12" :lg="6" class="card-panel-col">
      <div class="card-panel"  style="cursor: default;">
        <div class="card-panel-icon-wrapper icon-message">
          <i class="el-icon-document-checked" style="font-size: 30px;"></i>
        </div>
        <div class="card-panel-description">
          <div class="card-panel-text">
            Features/User Stories
          </div>
          {{ user_story_count }}
        </div>
      </div>
    </el-col>
    <el-col :xs="12" :sm="12" :lg="6" class="card-panel-col">
      <div class="card-panel" style="cursor: default;">
        <div class="card-panel-icon-wrapper icon-money">
         <i class="el-icon-share" style="font-size: 30px;"></i>
        </div>
        <div class="card-panel-description">
          <div class="card-panel-text">
            Threat Scenarios
          </div>
          {{ threat_scenario_count }}
        </div>
      </div>
    </el-col>
    <el-col :xs="12" :sm="12" :lg="6" class="card-panel-col">
      <div class="card-panel" style="cursor: default;">
        <div class="card-panel-icon-wrapper icon-shopping">
          <i class="el-icon-s-marketing" style="font-size: 30px;"></i>
        </div>
        <div class="card-panel-description">
          <div class="card-panel-text">
            Scans
          </div>
          {{ scan_count }}
        </div>
      </div>
    </el-col>
  </el-row>
</template>

<script>
export default {
  name: 'dashBox',
  props: {
    projectCount: {
      default: 0
    },
    user_story_count: {
      default: 0
    },
    threat_scenario_count: {
      default: 0
    },
    scan_count: {
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
    height: 108px;
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

      .card-panel-text {
        line-height: 18px;
        color: rgba(0, 0, 0, 0.45);
        font-size: 16px;
        margin-bottom: 12px;
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
