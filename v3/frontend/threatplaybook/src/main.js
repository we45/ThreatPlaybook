import Vue from "vue";
import App from "./App.vue";
import Buefy from "buefy";
import "buefy/dist/buefy.css";
import VueRouter from "vue-router";
import { routes } from "./routes";

Vue.config.productionTip = false;
Vue.use(Buefy);
Vue.use(VueRouter);

const router = new VueRouter({
  routes,
  mode: "history"
});

new Vue({
  el: "#app",
  router,
  render: h => h(App)
});