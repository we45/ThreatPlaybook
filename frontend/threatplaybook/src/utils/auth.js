import axios from 'axios'
import conf from '../../configure'

var api_url = process.env.VUE_APP_API_URL
var jwtToken = sessionStorage.getItem('token')

const instance = axios.create({
  baseURL: api_url,
  headers: {
    'Authorization': jwtToken
  }
})
export default instance
