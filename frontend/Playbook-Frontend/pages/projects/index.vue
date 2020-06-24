<template>
  <div>
    <v-breadcrumbs :items="breadcrumbData">
      <template v-slot:divider>
        <v-icon>mdi-forward</v-icon>
      </template>
    </v-breadcrumbs>
    <ProjectsPage></ProjectsPage>
  </div>
</template>
<script>
import { mapActions } from 'vuex'
import ProjectsPage from '@/components/projects/ProjectsPage'
export default {
  layout: 'main',
  name: 'Project',
  components: {
    ProjectsPage
  },
  data() {
    return {
      breadcrumbData: [
        {
          text: 'Home',
          disabled: false,
          to: '/home'
        },
        {
          text: 'Project',
          disabled: false,
          to: '/projects'
        }
      ]
    }
  },
  mounted() {
    this.showPageLoading(true)
    this.fetchProjectData()
  },
  methods: {
    ...mapActions('projects', ['showPageLoading', 'fetchProjectData'])
  }
}
</script>
