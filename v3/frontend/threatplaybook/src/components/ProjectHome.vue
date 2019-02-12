<template>
  <div>
    <nav-bar></nav-bar>
    <div class="column is-narrow"></div>
    <div class="column">
      <h1 class="has-text-left has-text-weight-semibold" style="font-size: 20px;">Projects</h1>
      <hr>
      <div class="columns is-multiline">
        <template v-for="item in projectQuery">
          <div class="column is-3">
            <div class="tile">
              <div class="tile is-parent is-vertical">
                <article class="tile is-child notification is-primary">
                  <a href="#" @click="goToProject(item.name)" class="title" style="text-decoration: none;">
                    {{ item.name }}
                  </a>
                  <br>
                  <br>
                  <a @click="goToProjectMap(item.name)">
                  <p class="has-text-right">Threat Map</p>
                  </a>
                </article>
              </div>
            </div>
          </div>
        </template>
      </div>
    </div>
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
    },
    goToProjectMap(item_name) {
      this.$router.push("/map/" + btoa(item_name));
    }
  }
};
</script>
