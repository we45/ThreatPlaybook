<template>
  <div>
    <el-menu class='navbar navbar-expand-sm' mode="horizontal">
      <img src="../../assets/tp-logo.png" alt="ThreatPlayBook" style="float: left;margin-left: 2%;"/>
      <!--<hamburger :toggleClick="toggleSideBar" :isActive="sidebar.opened"></hamburger>-->
      <!-- <img src="/static/img/logo.png" height="50px"/> -->
      <!--    <el-dropdown class="avatar-container" trigger="click">-->
      <!--      <div class="avatar-wrapper">-->
      <!--        <img class="user-avatar" src="/static/img/org.png" height="50px">-->
      <!--        <i class="el-icon-caret-bottom"></i>-->
      <!--      </div>-->
      <!--      <el-dropdown-menu class="user-dropdown" slot="dropdown">-->
      <!--        <router-link class="inlineBlock" to="/org/profile">-->
      <!--          <el-dropdown-item>-->
      <!--            Profile-->
      <!--          </el-dropdown-item>-->
      <!--        </router-link>-->
      <!--        <el-dropdown-item divided>-->
      <!--            <span style="display:block;" @click="logout">LogOut</span>-->
      <!--        </el-dropdown-item>-->
      <!--      </el-dropdown-menu>-->
      <!--    </el-dropdown>-->
      <i class="el-icon-switch-button" style="font-size: 20px;float: right;cursor: pointer;" @click="signout()"></i>
    </el-menu>
<!--     <el-menu default-active="2" class="el-menu-vertical-demo" :collapse="isCollapse">-->
<!--      &lt;!&ndash;      <el-submenu index="1">&ndash;&gt;-->
<!--      &lt;!&ndash;        <template slot="title">&ndash;&gt;-->
<!--      &lt;!&ndash;          <i class="el-icon-location"></i>&ndash;&gt;-->
<!--      &lt;!&ndash;          <span slot="title">Navigator One</span>&ndash;&gt;-->
<!--      &lt;!&ndash;        </template>&ndash;&gt;-->
<!--      &lt;!&ndash;        <el-menu-item-group>&ndash;&gt;-->
<!--      &lt;!&ndash;          <span slot="title">Group One</span>&ndash;&gt;-->
<!--      &lt;!&ndash;          <el-menu-item index="1-1">item one</el-menu-item>&ndash;&gt;-->
<!--      &lt;!&ndash;          <el-menu-item index="1-2">item two</el-menu-item>&ndash;&gt;-->
<!--      &lt;!&ndash;        </el-menu-item-group>&ndash;&gt;-->
<!--      &lt;!&ndash;        <el-menu-item-group title="Group Two">&ndash;&gt;-->
<!--      &lt;!&ndash;          <el-menu-item index="1-3">item three</el-menu-item>&ndash;&gt;-->
<!--      &lt;!&ndash;        </el-menu-item-group>&ndash;&gt;-->
<!--      &lt;!&ndash;        <el-submenu index="1-4">&ndash;&gt;-->
<!--      &lt;!&ndash;          <span slot="title">item four</span>&ndash;&gt;-->
<!--      &lt;!&ndash;          <el-menu-item index="1-4-1">item one</el-menu-item>&ndash;&gt;-->
<!--      &lt;!&ndash;        </el-submenu>&ndash;&gt;-->
<!--      &lt;!&ndash;      </el-submenu>&ndash;&gt;-->
<!--      <el-menu-item index="2" style="margin-top: 30%;">-->
<!--        <span slot="title">Home</span>-->
<!--        <router-link to="home">-->
<!--          <i class="el-icon-menu"></i>-->
<!--        </router-link>-->
<!--      </el-menu-item>-->
<!--      <el-menu-item index="3" style="margin-top: 30%;">-->
<!--        <i class="el-icon-document"></i>-->
<!--        <span slot="title">Projects</span>-->
<!--      </el-menu-item>-->
<!--      <el-menu-item index="4" style="margin-top: 30%;">-->
<!--        <i class="el-icon-setting"></i>-->
<!--        <span slot="title">Settings</span>-->
<!--      </el-menu-item>-->
<!--    </el-menu>-->
  </div>
</template>

<script>
export default {
  name: 'navBarIndex',
  data () {
    return {
      isCollapse: true
    }
  },
  methods: {
    signout () {
      localStorage.removeItem('token')
      this.$router.push('/login')
    }
  }
}
</script>

<style scoped>
  .el-menu-vertical-demo {
  /*  !*width: 200px;*!*/
  /*  min-height: 100vh;*/
  /*  !*max-height: 100vh;*!*/
  }
</style>
<style rel="stylesheet/scss" lang="scss" scoped>
  .navbar {
    height: 50px;
    line-height: 50px;
    border-radius: 0px !important
  }
</style>
