<template>
    <div>
        <div class="task-container columns is-multiline" style="margin-top: 5%;text-align: center">
            <div class="card column is-half is-offset-one-quarter">
                <img alt="ThreatPlaybook Logo" src="../assets/tp-logo.png"/>
                <hr>
                <form @submit.prevent="loginAction">
                <div class="card-content" align="left">
                    <b-field label="Email">
                        <b-input
                                placeholder="Enter Email"
                                type="email"
                                value="john@"
                                v-model="form.email"

                        >
                        </b-input>
                    </b-field>
                    <br>
                    <b-field label="Password">
                        <b-input
                                placeholder="Enter Password"
                                value="123"
                                type="password"
                                v-model="form.password"
                        ></b-input>
                    </b-field>
                    <br>
                    <button class="button is-primary is-large is-fullwidth"
                            @click="loginAction">Login
                    </button>
                </div>
            </form>
            </div>
        </div>

    </div>
</template>
<script>
    import axios from "axios";
    import conf from '../../configure'

    export default {
        data() {
            return {
                form: {
                    email: "",
                    password: ""
                }
            };
        },
        methods: {
            loginAction() {
                const baseURL = conf.API_URL
                const loginUrl = baseURL + '/login'
                axios
                    .post(loginUrl, {
                        email: this.form.email,
                        password: this.form.password
                    })
                    .then(response => {
                        localStorage.removeItem('token')
                        localStorage.setItem('token', response.data.token)
                        this.$router.push("/projects");
                    })
                    .catch(error => {
                        localStorage.removeItem('token')
                        this.$toast.open({
                            duration: 7000,
                            message: "Invalid Credentials",
                            position: "is-top",
                            type: "is-danger"
                        });
                    });
            }
        }
    };
</script>
