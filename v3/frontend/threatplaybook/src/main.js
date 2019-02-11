import Vue from "vue";
import App from "./App.vue";
import Buefy from "buefy";
import "buefy/dist/buefy.css";
import VueRouter from "vue-router";
import { routes } from "./routes";
import { ApolloClient } from "apollo-client";
import { HttpLink } from "apollo-link-http";
import { InMemoryCache } from "apollo-cache-inmemory";
import VueApollo from "vue-apollo";
import { setContext } from "apollo-link-context";

Vue.config.productionTip = false;
Vue.use(Buefy);
Vue.use(VueRouter);
Vue.use(VueApollo);

const router = new VueRouter({
  routes,
  mode: "history"
});

const httpLink = new HttpLink({
  uri: `http://localhost:5042/graph`
});

const authLink = setContext((_, { headers }) => {
  const token = localStorage.getItem("token");
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
