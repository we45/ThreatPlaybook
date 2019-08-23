<template>
  <div>
    <img src="../../assets/threat_logo.png" alt="ThreatPlaybook Logo"
                         class="img-center">
    <el-form @submit.prevent.native="submitForm" :model="loginForm" :rules="rules" ref="loginForm" label-position="left" label-width="0px"
             class="demo-loginForm login-container" >
      <el-form-item label="Email" prop="checkEmail">
        <el-input type="email" v-model="loginForm.email" auto-complete="off"></el-input>
      </el-form-item>
      <el-form-item label="Password" prop="checkPass">
        <el-input type="password" v-model="loginForm.password" auto-complete="off"></el-input>
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="submitForm('loginForm')" style="float: right;" round>Login</el-button>
      </el-form-item>
    </el-form>
  </div>
</template>

<script>
export default {
  name: 'login',
  data () {
    return {
      loginForm: {
        email: '',
        password: ''
      },
      rules: {
        checkEmail: [
          {required: false, message: 'Please enter a email', trigger: 'blur'}
        ],
        checkPass: [
          {required: false, message: 'Please enter a password', trigger: 'blur'}
        ]
      }
    }
  },
  methods: {
    submitForm (formName) {
      this.$refs[formName].validate((valid) => {
        if (valid) {
          this.$emit('loginUser', {email: this.loginForm.email, password: this.loginForm.password})
        } else {
          return false
        }
      })
    }
  }
}
</script>

<style lang="scss" scoped>

  .login-container {
    -webkit-border-radius: 5px;
    border-radius: 5px;
    -moz-border-radius: 5px;
    background-clip: padding-box;
    margin: 10px auto;
    width: 450px;
    padding: 35px 35px 15px 35px;
    background: #fff;
    border: 1px solid #eaeaea;
    box-shadow: 0 0 25px #cac6c6;

    .title {
      margin: 0px auto 40px auto;
      text-align: center;
      color: #505458;
    }

    .remember {
      margin: 0px 0px 35px 0px;
    }
  }
  .img-center {
      display: block;
      margin-left: auto;
      margin-right: auto;
      /*width: 50%;*/
      border-style: none;
      border: none;
      margin-top: 5%;
    }
</style>
