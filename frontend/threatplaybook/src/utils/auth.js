import axios from "axios";

// var api_url = process.env.VUE_APP_API_URL
var api_url = "http://127.0.0.1:5042";
var jwtToken = sessionStorage.getItem("token");

const instance = axios.create({
  baseURL: api_url,
  headers: {
    Authorization: jwtToken
  }
});
export default instance;
