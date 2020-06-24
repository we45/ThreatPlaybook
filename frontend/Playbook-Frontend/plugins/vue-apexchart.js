import Vue from "vue";
import VueApexCharts from "vue-apexcharts";

Vue.use({
  install(Vue, options) {
    Vue.component("apexchart", VueApexCharts);
  }
});
