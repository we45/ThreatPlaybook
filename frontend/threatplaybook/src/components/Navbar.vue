<template>
    <div>
        <b-navbar toggleable="lg" type="dark" style="background-color: #f9f2f4;">
            <b-navbar-brand href="/home">
                <img src="../assets/tp-logo.png" alt="ThreatPlayBook" />
            </b-navbar-brand>

            <b-navbar-toggle target="nav_collapse"/>

            <b-collapse is-nav>
                <b-navbar-nav>
                    <b-nav-item href="#" @click="goToProject" >Projects</b-nav-item>
                </b-navbar-nav>

                <!-- Right aligned nav items -->
                <b-navbar-nav class="ml-auto">

                    <b-nav-item-dropdown right style="color: #1C1D21">
                        <!-- Using button-content slot -->
                        <template slot="button-content"><em style="color: #1C1D21">User</em></template>
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
                this.$router.push("/");
            },
            goToProject() {
                this.$router.push("/projects");
            }
        }
    }
</script>

<style scoped>
    .navbar-dark .navbar-nav .nav-link{
      color:#1C1D21;
    }
    .navbar-dark .navbar-nav:hover .nav-link{
      color:#1C1D21;
    }
</style>
