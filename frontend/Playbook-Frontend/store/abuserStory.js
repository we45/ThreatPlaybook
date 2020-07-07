import axios from "axios";
const loginUrl = process.env.VUE_APP_API_URL;

export const state = () => ({
  isLoading: false,
  projectAbuserStoryTree: []
});
export const mutations = {
  IS_PAGE_LOADING(state, data) {
    state.isLoading = data;
  },
  FETCH_PROJECT_ABUSER_STORY_TREE(state, data) {
    state.projectAbuserStoryTree = data;
  }
};
export const actions = {
  showPageLoading({ commit }, data) {
    commit("IS_PAGE_LOADING", data);
  },
  fetchAbuserStoryTreeByProject({ commit }, payload) {
    axios
      .post(loginUrl+"/api/abuser-story/project", payload, {
        headers: {
          Authorization: localStorage.getItem("token")
        }
      })
      .then(res => {
        if (res.data.success) {
          commit("FETCH_PROJECT_ABUSER_STORY_TREE", res.data.data);
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
  isPageLoading(state) {
    return state.isLoading;
  },
  getAbuserStoryProjectTree(state) {
    if (state.projectAbuserStoryTree) {
      return state.projectAbuserStoryTree;
    }
  }
};
