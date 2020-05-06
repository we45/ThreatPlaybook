import Vue from "vue";
import OrganizationChart from "vue-organization-chart";
import "vue-organization-chart/dist/orgchart.css";

Vue.use({
  install(Vue, options) {
    Vue.component("OrganizationChart", OrganizationChart);
  }
});
