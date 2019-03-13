<template>
    <div>
        <b-navbar toggleable="lg" type="dark" style="background-color: #7957d5;color: #FFFFFF;">
    <b-navbar-brand href="/home">
        <img src="../assets/tp-logo.png" alt="ThreatPlayBook" width="112" height="28">
    </b-navbar-brand>

    <b-navbar-toggle target="nav_collapse" />

    <b-collapse is-nav id="nav_collapse">
      <b-navbar-nav>
        <b-nav-item href="#" @click="goToProject">Projects</b-nav-item>
      </b-navbar-nav>

      <!-- Right aligned nav items -->
      <b-navbar-nav class="ml-auto">

        <b-nav-item-dropdown right>
          <!-- Using button-content slot -->
          <template slot="button-content"><em>User</em></template>
          <!--<b-dropdown-item href="#">Profile</b-dropdown-item>-->
          <b-dropdown-item @click="logOut">Signout</b-dropdown-item>
        </b-nav-item-dropdown>
      </b-navbar-nav>
    </b-collapse>
  </b-navbar>
    </div>
</template>
<script>
export default {
    name: "Navbar",
    methods: {
        logOut() {
            this.token = sessionStorage.getItem('token')
            // localStorage.removeItem('token')
            this.$router.push("/");
        },
        goToProject() {
              this.$router.push("/projects");
            }
    }
}
</script>
