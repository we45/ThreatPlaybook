<template>
  <div class="container">
    <nav-bar></nav-bar>
    <h1 class="title">Projects</h1>
    <template>
      <div v-if="projectQuery">
        <div class="tile">
          <div class="tile is-parent is-vertical" v-for="item in projectQuery">
            <article class="tile is-child notification is-primary">
              <a href="#" @click="goToProject(item.name)" class="title">{{
                item.name
              }}</a>
            </article>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>
<script>
import Navbar from "./Navbar.vue";
import gql from "graphql-tag";
export default {
  components: {
    "nav-bar": Navbar
  },
  data() {
    return {};
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
    goToProject(item_name) {
      this.$router.push("/project/" + btoa(item_name));
    }
  }
};
</script>
