import axios from "axios";
const loginUrl = process.env.VUE_APP_API_URL;

export const state = () => ({
  isLoading: false,
  data: [],
  projectScanData: [],
  individualScanData: []
});
export const mutations = {
  IS_PAGE_LOADING(state, data) {
    state.isLoading = data;
  },
  FETCH_DATA(state, data) {
    state.data = data;
  },
  FETCH_SCAN_DATA_PROJECT(state, data) {
    state.projectScanData = data;
  },
  FETCH_INDIVIDUAL_DATA(state, data) {
    state.individualScanData = data;
  }
};
export const actions = {
  showPageLoading({ commit }, data) {
    commit("IS_PAGE_LOADING", data);
  },
  fetchScanData({ commit }) {
    axios
      .get("/api/scan/read", {
        headers: {
          Authorization: localStorage.getItem("token")
        }
      })
      .then(response => {
        if (response.data.success) {
          const scanData = [];
          for (const data of response.data.data) {
            scanData.push({ name: data.name });
          }
          commit("FETCH_DATA", scanData);
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
  fetchIndividualScanData({ commit }, payload) {
    axios
      .post("/api/scan-vuls/project", payload, {
        headers: {
          Authorization: localStorage.getItem("token")
        }
      })
      .then(response => {
        if (response.data.success) {
          const scanData = [];
          for (const data of response.data.data) {
            scanData.push({
              name: data.name,
              cwe: data.cwe,
              severity: data.severity,
              description: data.description
            });
          }
          commit("FETCH_INDIVIDUAL_DATA", scanData);
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
  fetchScanbyProject({ commit }, payload) {
    axios
      .post("/api/scan/project", payload, {
        headers: {
          Authorization: localStorage.getItem("token")
        }
      })
      .then(response => {
        if (response.data.success) {
          const scanData = [];
          for (const scan of response.data.data.data) {
            scanData.push({
              name: scan.name,
              scan_type: scan.scan_type,
              tool: scan.tool
            });
          }
          commit("FETCH_SCAN_DATA_PROJECT", scanData);
          commit("IS_PAGE_LOADING", false);
        }
        commit("PAGE_LOADING", false);
      })
      .catch(error => {
        if (error.response.status === 401) {
          commit("PAGE_LOADING", false);
        }
      });
  }
};
export const getters = {
  isPageLoading(state) {
    return state.isLoading;
  },
  getScanCount(state) {
    if (state.data) {
      return state.data.length;
    }
  },
  getScanProjectData(state) {
    if (state.projectScanData) {
      return state.projectScanData;
    }
  },
  getScanIndividualData(state) {
    if (state.individualScanData) {
      return state.individualScanData;
    }
  }
};
