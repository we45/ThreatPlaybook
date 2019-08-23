<template>
  <div>
    <el-aside width="80px">
        <el-menu default-active="2" class="el-menu-vertical-demo" :collapse="isCollapse">
          <el-menu-item index="2" style="margin-top: 30%;">
            <span slot="title">Home</span>
            <router-link to="/home">
              <i class="el-icon-menu"></i>
            </router-link>
          </el-menu-item>
          <el-menu-item index="3" style="margin-top: 30%;">
            <span slot="title">Projects</span>
            <router-link to="/project">
            <i class="el-icon-document"></i>
            </router-link>
          </el-menu-item>
<!--          <el-menu-item index="4" style="margin-top: 30%;">-->
<!--            <i class="el-icon-setting"></i>-->
<!--            <span slot="title">Settings</span>-->
<!--          </el-menu-item>-->
        </el-menu>
      </el-aside>
  </div>
</template>

<script>
export default {
  name: 'sidebar',
  data () {
    return {
      isCollapse: true
    }
  }
}
</script>

<style rel="stylesheet/scss" lang="scss" scoped>
.el-menu-vertical-demo{
  height: 100vh;
}
</style>
