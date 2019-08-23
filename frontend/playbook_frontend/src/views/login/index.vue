<template>
  <div v-loading="loading">
    <login @loginUser="loginUser($event)"></login>
  </div>
</template>

<script>
import axios from 'axios'
import conf from '../../../configure.json'
import login from '@/components/login/login'

export default{
  name: 'loginIndex',
  components: {
    login
  },
  data () {
    return {
      loading: false
    }
  },
  methods: {
    signout () {
      localStorage.removeItem('token')
      this.$router.push('/login')
    },
    loginUser (event) {
      this.loading = true
      const baseURL = conf.API_URL
      const loginUrl = baseURL + 'login'
      axios
        .post(loginUrl, {
          email: event.email,
          password: event.password
        })
        .then(response => {
          if (response.data.token !== undefined) {
            localStorage.removeItem('token')
            localStorage.setItem('token', response.data.token)
            this.$router.push('/home')
            this.loading = false
          } else {
            this.signout()
            this.loading = false
          }
          this.loading = false
        })
        .catch(error => {
          console.log('Error', error)
          this.signout()
          this.loading = false
        })
    }
  }
}

</script>

<style lang="scss" scoped>
</style>
