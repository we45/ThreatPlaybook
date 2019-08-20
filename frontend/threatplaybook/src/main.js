import Vue from "vue";
import App from "./App.vue";
import Buefy from "buefy";
// import "buefy/dist/buefy.css";
import VueRouter from "vue-router";
import { routes } from "./routes";
import { ApolloClient } from "apollo-client";
import { HttpLink } from "apollo-link-http";
import { InMemoryCache } from "apollo-cache-inmemory";
import VueApollo from "vue-apollo";
import { setContext } from "apollo-link-context";
import conf from "../configure";
import BootstrapVue from "bootstrap-vue";
import "bootstrap/dist/css/bootstrap.css";
import "bootstrap-vue/dist/bootstrap-vue.css";
import ApexCharts from "apexcharts";
import { library } from "@fortawesome/fontawesome-svg-core";
import { faSync } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/vue-fontawesome";
import VueApexCharts from "vue-apexcharts";
import VueFilterDateFormat from "vue-filter-date-format";
import BootstrapVueTreeview from 'bootstrap-vue-treeview'
Vue.use(BootstrapVueTreeview)

library.add(faSync);

Vue.component("font-awesome-icon", FontAwesomeIcon);

Vue.use(VueFilterDateFormat, {
  monthNames: [
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December"
  ],
  monthNamesShort: [
    "Jan",
    "Feb",
    "Mar",
    "Apr",
    "May",
    "Jun",
    "Jul",
    "Aug",
    "Sep",
    "Oct",
    "Nov",
    "Dec"
  ]
});

Vue.config.productionTip = false;
// Vue.use(Buefy);
Vue.use(VueApexCharts);
Vue.use(VueRouter);
Vue.use(VueApollo);
Vue.use(BootstrapVue);
Vue.component("apexchart", VueApexCharts);
const router = new VueRouter({
  routes,
  mode: "history"
});

// const baseURL = process.env.VUE_APP_API_URL;
const baseURL = 'http://127.0.0.1:5042'
const graphURL = baseURL + "/graph";
const httpLink = new HttpLink({
  uri: graphURL
});

const authLink = setContext((_, { headers }) => {
  // const token = localStorage.getItem("token");
  const token = sessionStorage.getItem("token");
  return {
    headers: {
      authorization: token ? `${token}` : ""
    }
  };
});

const link = authLink.concat(httpLink);
const apolloClient = new ApolloClient({
  link,
  cache: new InMemoryCache(),
  connectToDevTools: true
});
const apolloProvider = new VueApollo({
  defaultClient: apolloClient
});

new Vue({
  el: "#app",
  router,
  provide: apolloProvider.provide(),
  render: h => h(App)
});
