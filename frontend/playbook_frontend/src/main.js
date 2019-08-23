// The Vue build version to load with the `import` command
// (runtime-only or standalone) has been set in webpack.base.conf with an alias.
import Vue from 'vue'
import App from './App'
import router from './router'
import Element from 'element-ui'
import 'element-ui/lib/theme-chalk/index.css'
import { ApolloClient } from 'apollo-client'
import { HttpLink } from 'apollo-link-http'
import { InMemoryCache } from 'apollo-cache-inmemory'
import VueApollo from 'vue-apollo'
import { setContext } from 'apollo-link-context'
import VueApexCharts from 'vue-apexcharts'
import conf from '../configure.json'

Vue.config.productionTip = false

Vue.use(Element)
Vue.use(VueApollo)
Vue.use(VueApexCharts)
Vue.component('apexchart', VueApexCharts)
// const baseURL = process.env.API_URL;
const baseURL = conf.API_URL
// const baseURL = 'http://127.0.0.1:5042'
const graphURL = baseURL + 'graph'
const httpLink = new HttpLink({
  uri: graphURL
})

const authLink = setContext((_, { headers }) => {
  // const token = localStorage.getItem("token");
  const token = localStorage.getItem('token')
  return {
    headers: {
      authorization: token ? `${token}` : ''
    }
  }
})

const link = authLink.concat(httpLink)
const apolloClient = new ApolloClient({
  link,
  cache: new InMemoryCache(),
  connectToDevTools: true
})
const apolloProvider = new VueApollo({
  defaultClient: apolloClient
})

/* eslint-disable no-new */
new Vue({
  el: '#app',
  router,
  provide: apolloProvider.provide(),
  components: { App },
  template: '<App/>'
})
