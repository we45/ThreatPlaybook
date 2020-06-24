import axios from "axios";
const loginUrl = process.env.VUE_APP_API_URL;

export const state = () => ({
  isLoading: false,
  data: [],
  sevData: [],
  projectScenarioData: [],
  projectScenarioTree: []
});
export const mutations = {
  IS_PAGE_LOADING(state, data) {
    state.isLoading = data;
  },
  FETCH_DATA(state, data) {
    state.data = data;
  },
  FETCH_SEV_DATA(state, data) {
    state.sevData = data;
  },
  FETCH_PROJECT_THREAT_SCENARIO_DATA(state, data) {
    state.projectScenarioData = data;
  },
  FETCH_PROJECT_THREAT_SCENARIO_TREE(state, data) {
    state.projectScenarioTree = data;
  }
};
export const actions = {
  showPageLoading({ commit }, data) {
    commit("IS_PAGE_LOADING", data);
  },
  fetchThreatScenarioData({ commit }) {
    axios
      .get("/api/scenarios/read", {
        headers: {
          Authorization: localStorage.getItem("token")
        }
      })
      .then(response => {
        if (response.data.success) {
          const threatScenarioData = [];
          for (const data of response.data.data) {
            threatScenarioData.push({ name: data.name });
          }
          commit("FETCH_DATA", threatScenarioData);
          commit("IS_PAGE_LOADING", false);
        }
        commit("PAGE_LOADING", false);
      })
      .catch(error => {
        if (error.response.status === 401) {
          commit("PAGE_LOADING", false);
        }
      });
  },
  fetchThreatScenarioSevData({ commit }) {
    axios
      .get("/api/scenario/severity", {
        headers: {
          Authorization: localStorage.getItem("token")
        }
      })
      .then(response => {
        if (response.data.success) {
          const donutSeries = [];
          const highCount = [];
          const mediumCount = [];
          const lowCount = [];
          for (const data of response.data.data) {
            if (data.severity === 3) {
              highCount.push(data.severity);
            } else if (data.severity === 2) {
              mediumCount.push(data.severity);
            } else {
              lowCount.push(data.severity);
            }
          }
          donutSeries.push(highCount.length);
          donutSeries.push(mediumCount.length);
          donutSeries.push(lowCount.length);
          commit("FETCH_SEV_DATA", donutSeries);
          commit("IS_PAGE_LOADING", false);
        }
        commit("PAGE_LOADING", false);
      })
      .catch(error => {
        if (error.response.status === 401) {
          commit("PAGE_LOADING", false);
        }
      });
  },
  fetchProjectThreatScenarioData({ commit }, payload) {
    axios
      .post("/api/scenarios/project", payload, {
        headers: {
          Authorization: localStorage.getItem("token")
        }
      })
      .then(response => {
        if (response.data.success) {
          const threatScenarioData = [];
          for (const data of response.data.data) {
            threatScenarioData.push({
              name: data.name
            });
          }
          commit("FETCH_PROJECT_THREAT_SCENARIO_DATA", threatScenarioData);
          commit("IS_PAGE_LOADING", false);
        }
        commit("PAGE_LOADING", false);
      })
      .catch(error => {
        if (error.response.status === 401) {
          commit("PAGE_LOADING", false);
        }
      });
  },
  fetchThreatScenarioTreeByProject({ commit }, payload) {
    axios
      .post("/api/threat-scenario/project", payload, {
        headers: {
          Authorization: localStorage.getItem("token")
        }
      })
      .then(res => {
        if (res.data.success) {
          commit("FETCH_PROJECT_THREAT_SCENARIO_TREE", res.data.data);
        }
        commit("IS_FETCHING", false);
      })
      .catch(error => {
        commit("IS_FETCHING", false);
        if (error.response.status === 401) {
        }
      });
  }
};
export const getters = {
  get_project_scenario_count(state) {
    if (state.projectScenarioData) {
      return state.projectScenarioData.length;
    }
  },
  isPageLoading(state) {
    return state.isLoading;
  },
  getThreatScenarioCount(state) {
    if (state.data) {
      return state.data.length;
    }
  },
  getThreatScenarioSevData(state) {
    if (state.sevData) {
      return state.sevData;
    }
  },
  getThreatScenarioProjectTree(state) {
    if (state.projectScenarioTree) {
      return state.projectScenarioTree;
    }
  }
};
