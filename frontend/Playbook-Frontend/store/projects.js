import axios from "axios";
const loginUrl = process.env.VUE_APP_API_URL;

export const state = () => ({
  isLoading: false,
  data: []
});
export const mutations = {
  IS_PAGE_LOADING(state, data) {
    state.isLoading = data;
  },
  FETCH_DATA(state, data) {
    state.data = data;
  }
};
export const actions = {
  showPageLoading({ commit }, data) {
    commit("IS_PAGE_LOADING", data);
  },
  fetchProjectData({ commit }) {
    axios
      .get("/api/project/read", {
        headers: {
          Authorization: localStorage.getItem("token")
        }
      })
      .then(response => {
        if (response.data.success) {
          const projectData = [];
          for (const data of response.data.data) {
            projectData.push({ name: data.name });
          }
          commit("FETCH_DATA", projectData);
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
  getProjectCount(state) {
    if (state.data) {
      return state.data.length;
    }
  },
  getProjectData(state) {
    if (state.data) {
      return state.data;
    }
  }
};
