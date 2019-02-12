<template>
    <div>
        <nav class="navbar is-primary" role="navigation" aria-label="main navigation">
            <div class="navbar-brand">
                <a class="navbar-item" href="/projects">
                    <img src="../assets/tp-logo.png" alt="ThreatPlayBook" width="112" height="28">
                </a>
            </div>
            <div class="navbar-end">
                <div class="navbar-item has-dropdown is-hoverable is-right">
                    <a class="navbar-link">
                        Tilak.T
                    </a>
                    <div class="navbar-dropdown">
                        <a class="navbar-item">
                            Profile
                        </a>
                        <hr class="navbar-divider">
                        <div class="navbar-item" @click="logOut">
                            Logout
                        </div>
                    </div>
                </div>
            </div>
        </nav>
    </div>
</template>
<script>
export default {
    methods: {
        logOut() {
            localStorage.removeItem('token')
            this.$router.push("/");
        }
    }
}
</script>
