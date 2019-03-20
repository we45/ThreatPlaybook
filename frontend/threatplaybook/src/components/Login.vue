<template>
    <div>
        <loading :active.sync="isLoading" :can-cancel="true"></loading>
        <b-row>
            <b-col cols="3"></b-col>
            <b-col cols="6">
                <b-card style="margin-top: 10%;">
                    <img src="../assets/tp-logo.png" alt="ThreatPlaybook Logo"
                         class="img-center">
                    <br>
                    <br>
                    <p class="text-center error" v-if="inValidCredentials"> * Invalid Email or Password</p>
                    <br>
                    <form @submit.prevent="loginAction">
                        <b-form-input v-model="form.email"
                                      type="email" placeholder="Email"
                                      class="form-control"></b-form-input>
                        <br>
                        <br>
                        <b-form-input v-model="form.password"
                                      type="password"
                                      placeholder="Password"
                                      class="form-control"></b-form-input>
                        <br>
                        <br>
                        <br>
                        <button class="login-button"
                                v-if="!form.email || !form.password"
                                disabled="disabled">Login
                        </button>
                        <button class="login-button" v-if="form.email && form.password">Login</button>
                    </form>
                </b-card>
            </b-col>
            <b-col cols="3"></b-col>
        </b-row>

    </div>
</template>
<script>
    import axios from "axios";
    import Loading from 'vue-loading-overlay'
    import 'vue-loading-overlay/dist/vue-loading.css';
    import conf from '../../configure'

    export default {
        components: {
            Loading
        },
        data() {
            return {
                form: {
                    email: "",
                    password: ""
                },
                inValidCredentials: false,
                isLoading: false
            };
        },
        methods: {
            loginAction() {
                this.isLoading = true
                const baseURL = process.env.VUE_APP_API_URL
                // const baseURL = 'http://127.0.0.1:5042'
                const loginUrl = baseURL + '/login'
                axios
                    .post(loginUrl, {
                        email: this.form.email,
                        password: this.form.password
                    })
                    .then(response => {
                        if (response.data.token !== undefined) {
                            sessionStorage.removeItem('token')
                            sessionStorage.setItem('token', response.data.token)
                            this.$router.push("/home");
                        } else {
                            sessionStorage.removeItem('token')
                            this.inValidCredentials = true
                        }
                        this.isLoading = false
                    })
                    .catch(error => {
                        sessionStorage.removeItem('token')
                        this.inValidCredentials = true
                        // this.$toast.open({
                        //     duration: 7000,
                        //     message: "Invalid Credentials",
                        //     position: "is-top",
                        //     type: "is-danger"
                        // });
                        this.isLoading = false
                    });
            }
        }
    };
</script>

<style scoped>
    .login-button {
        position: relative;
        background-color: #7957d5;
        border: none;
        font-size: 24px;
        color: #FFFFFF;
        padding: 16px;
        width: 100%;
        text-align: center;
        -webkit-transition-duration: 0.4s; /* Safari */
        transition-duration: 0.4s;
        text-decoration: none;
        overflow: hidden;
        cursor: pointer;
        border-radius: 8px;
    }

    .login-button:after {
        content: "";
        background: #7957d5;
        display: block;
        position: absolute;
        padding-top: 300%;
        padding-left: 350%;
        margin-left: -20px !important;
        margin-top: -120%;
        opacity: 0;
        transition: all 0.8s
    }

    .login-button:active:after {
        padding: 0;
        margin: 0;
        opacity: 1;
        transition: 0s
    }

    .error {
        color: #F04E23;
        font-size: 16px;
        font-weight: bold;
    }

    .img-center {
        display: block;
        margin-left: auto;
        margin-right: auto;
        width: 50%;
        border-style: none;
        border: none;
    }
</style>
