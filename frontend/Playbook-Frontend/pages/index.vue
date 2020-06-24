<template>
  <v-row align="center" justify="center">
    <v-col cols="12" sm="8" md="4">
      <center>
        <img src="/threat_logo.png" alt="Threat Playbook" />
      </center>
      <v-alert
        v-if="isLoginError"
        type="error"
        v-text="loginErrorMessage"
      ></v-alert>
      <v-card class="elevation-12">
        <v-toolbar color="primary" dark flat>
          <v-toolbar-title>Login</v-toolbar-title>
          <v-spacer />
        </v-toolbar>
        <v-card-text>
          <v-form @keyup.native.enter="onSubmit">
            <v-text-field
              id="email"
              v-model="email"
              :error-messages="emailErrors"
              label="Email"
              name="email"
              prepend-icon="mdi-face"
              type="email"
              required
              @input="$v.email.$touch()"
              @blur="$v.email.$touch()"
            />
            <v-text-field
              id="password"
              v-model="password"
              label="Password"
              name="password"
              prepend-icon="mdi-lock"
              type="password"
              :error-messages="passwordErrors"
              required
              @input="$v.password.$touch()"
              @blur="$v.password.$touch()"
            />
          </v-form>
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn
            v-if="!isPageLoading"
            type="submit"
            color="primary"
            @click="onSubmit()"
            >Login</v-btn
          >
          <v-btn
            v-if="isPageLoading"
            type="submit"
            color="primary"
            disabled
            @click="onSubmit()"
          >
            <v-progress-circular
              indeterminate
              color="primary"
            ></v-progress-circular>
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-col>
  </v-row>
</template>

<script>
import { mapActions, mapGetters } from 'vuex'
import { validationMixin } from 'vuelidate'
import { required, email } from 'vuelidate/lib/validators'
export default {
  mixins: [validationMixin],
  data() {
    return {
      email: '',
      password: ''
    }
  },
  validations: {
    email: { required, email },
    password: { required }
  },
  computed: {
    emailErrors() {
      const errors = []
      if (!this.$v.email.$dirty) return errors
      !this.$v.email.email && errors.push('Must be a valid e-mail')
      !this.$v.email.required && errors.push('E-mail is required')
      return errors
    },
    passwordErrors() {
      const errors = []
      if (!this.$v.password.$dirty) return errors
      !this.$v.password.required && errors.push('Password is required')
      return errors
    },
    ...mapGetters('login', {
      isPageLoading: 'isPageLoading',
      loginErrorMessage: 'loginErrorMessage',
      isLoginError: 'isLoginError'
    })
  },
  watch: {
    email: {
      handler() {
        if (this.loginErrorMessage) {
          this.pageLoadingError(false)
        }
      }
    },
    password: {
      handler() {
        if (this.loginErrorMessage) {
          this.pageLoadingError(false)
        }
      }
    }
  },
  methods: {
    ...mapActions('login', ['pageLoading', 'loginUser', 'pageLoadingError']),
    onSubmit() {
      this.$v.$touch()
      if (!this.$v.$invalid) {
        const data = {
          email: this.email,
          password: this.password
        }
        this.pageLoading(true)
        this.loginUser(data)
      }
    }
  }
}
</script>
