import axios from 'axios'
// import conf from '../../configure.json'
// eslint-disable-next-line camelcase
// var api_url = process.env.API_URL
// var baseURL = conf.API_URL
const baseURL = 'http://127.0.0.1:5042'
const jwtToken = localStorage.getItem('token')

const instance = axios.create({
  baseURL,
  headers: {
    Authorization: jwtToken
  }
})
export default instance
