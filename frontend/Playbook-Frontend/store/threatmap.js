import axios from "axios";
const loginUrl = process.env.VUE_APP_API_URL;

export const state = () => ({
  isLoading: false,
  threatMapDataProject: []
});
export const mutations = {
  IS_PAGE_LOADING(state, data) {
    state.isLoading = data;
  },
  FETCH_THREAT_MAP_PROJECT(state, data) {
    state.threatMapDataProject = data;
  }
};
export const actions = {
  showPageLoading({ commit }, data) {
    commit("IS_PAGE_LOADING", data);
  },
  fetchThreatMapbyProject({ commit }, payload) {
    axios
      .post("/api/threatmap/project", payload, {
        headers: {
          Authorization: localStorage.getItem("token")
        }
      })
      .then(response => {
        if (response.data.success) {
          commit("FETCH_THREAT_MAP_PROJECT", response.data.data);
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
  getThreatMapProjectData(state) {
    if (state.threatMapDataProject) {
      return state.threatMapDataProject;
    }
  }
};
