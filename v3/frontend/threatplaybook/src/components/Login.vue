<template>
  <div class="container">
    <div class="card">
      <header class="card-header">
        <img alt="ThreatPlaybook Logo" src="../assets/tp-logo.png" />
      </header>
      <div class="card-content">
        <b-field label="Email">
          <b-input
            type="email"
            value="john@"
            maxlength="30"
            v-model="form.email"
          >
          </b-input>
        </b-field>
        <b-field label="Password">
          <b-input
            value="123"
            type="password"
            maxlength="30"
            v-model="form.password"
          ></b-input>
        </b-field>
        <button class="button is-primary" @click="loginAction">Login</button>
      </div>
    </div>
  </div>
</template>
<script>
import axios from "axios";
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
      axios
        .post("http://localhost:5042/login", {
          email: this.form.email,
          password: this.form.password
        })
        .then(response => {
          if ("token" in response.data) {
            if (localStorage.getItem("token") !== null) {
              localStorage.removeItem("token");
            } else {
              localStorage.setItem("token", response.data.token);
            }
            this.$toast.open({
              duration: 5000,
              message: "Successfully logged in",
              position: "is-top",
              type: "is-success"
            });
            this.$router.push("/projects");
          }
        })
        .catch(error => {
          console.log(error);
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
