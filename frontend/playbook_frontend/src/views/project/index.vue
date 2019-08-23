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
          <el-breadcrumb-item>Projects</el-breadcrumb-item>
        </el-breadcrumb>
<!--        <br>-->
<!--        <br>-->
<!--        <el-button type="primary" @click="createProject()" style="float: left;" round>Create</el-button>-->
        <br>
        <br>
        <br>
        <project-table :tableData="projectQuery" @viewproject="viewproject($event)"></project-table>
      </el-col>
    </el-row>
  </div>
</template>

<script>
import navBarIndex from '@/components/navbar/index'
import sidebar from '@/components/navbar/sidebar'
import projectTable from '@/components/project/projectTable'
import gql from 'graphql-tag'

export default {
  name: 'projectIndex',
  components: {
    sidebar,
    navBarIndex,
    projectTable
  },
  data () {
    return {
      tableData: [{
        id: '1',
        name: 'test_project'
      }, {
        id: '2',
        name: 'Demo'
      }]
    }
  },
  apollo: {
    projectQuery: {
      query: gql`
        query {
          projects {
            id
            name
          }
        }
      `,
      update: result => result.projects
    }
  },
  methods: {
    viewproject (event) {
      // this.$router.push('/project/' + btoa(event.name))
      //   window.location.href('/project/' + btoa(event.name))
      //   this.$router.go('/project/' + btoa(event.name))
            this.$router.push('/project/' + btoa(event.name))
    }
  }
}
</script>

<style scoped>

</style>
