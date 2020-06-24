import axios from "axios";
const loginUrl = process.env.VUE_APP_API_URL;

export const state = () => ({
  isLoading: false,
  data: [],
  userStorydata: [],
  projecytuserStorydata: [],
  projecytuserStoryID: [],
  projecytuserStoryTree: [],
  abuserStoryCount: 0
});
export const mutations = {
  IS_PAGE_LOADING(state, data) {
    state.isLoading = data;
  },
  FETCH_DATA(state, data) {
    state.data = data;
  },
  FETCH_PROJECT_USER_STORY_DATA(state, data) {
    state.projecytuserStorydata = data;
  },
  FETCH_PROJECT_ABUSER_STORY_COUNT(state, data) {
    state.abuserStoryCount = data;
  },
  FETCH_PROJECT_USER_STORY_ID(state, data) {
    state.projecytuserStoryID = data;
  },
  FETCH_PROJECT_USER_STORY_TREE(state, data) {
    state.projecytuserStoryTree = data;
  }
};
export const actions = {
  showPageLoading({ commit }, data) {
    commit("IS_PAGE_LOADING", data);
  },
  fetchUserStoryData({ commit }) {
    axios
      .get("/api/feature/read", {
        headers: {
          Authorization: localStorage.getItem("token")
        }
      })
      .then(response => {
        if (response.data.success) {
          const UserStoryData = [];
          for (const data of response.data.data) {
            UserStoryData.push({
              name: data.short_name
            });
          }
          commit("FETCH_DATA", UserStoryData);
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
  fetchUserStoryByProject({ commit }, payload) {
    axios
      .post("/api/feature/read", payload, {
        headers: {
          Authorization: localStorage.getItem("token")
        }
      })
      .then(res => {
        if (res.data.success) {
          const uStoryData = [];
          const aStoryData = [];
          const uStoryid = [];
          for (const u of res.data.data) {
            uStoryData.push({
              name: u.short_name
            });
            uStoryid.push(u._id.$oid);
            for (const c in u.abuses) {
              aStoryData.push(c.$oid);
            }
          }
          commit("FETCH_PROJECT_ABUSER_STORY_COUNT", aStoryData.length);
          commit("FETCH_PROJECT_USER_STORY_DATA", uStoryData);
          commit("FETCH_PROJECT_USER_STORY_ID", uStoryid);
        }
        commit("IS_FETCHING", false);
      })
      .catch(error => {
        commit("IS_FETCHING", false);
        if (error.response.status === 401) {
        }
      });
  },
  fetchUserStoryTreeByProject({ commit }, payload) {
    axios
      .post("/api/user-story/project", payload, {
        headers: {
          Authorization: localStorage.getItem("token")
        }
      })
      .then(res => {
        if (res.data.success) {
          commit("FETCH_PROJECT_USER_STORY_TREE", res.data.data);
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
  getUserStoryCount(state) {
    if (state.data) {
      return state.data.length;
    }
  },
  getUserStoryProjectCount(state) {
    if (state.projecytuserStorydata) {
      return state.projecytuserStorydata.length;
    }
  },
  getUserStoryProjectdata(state) {
    if (state.projecytuserStorydata) {
      return state.projecytuserStorydata;
    }
  },
  getAbuserStoryProjectCount(state) {
    if (state.abuserStoryCount) {
      return state.abuserStoryCount;
    }
  },
  getUserStoryProjectID(state) {
    if (state.projecytuserStoryID) {
      return state.projecytuserStoryID;
    }
  },
  getUserStoryProjectTree(state) {
    if (state.projecytuserStoryTree) {
      return state.projecytuserStoryTree;
    }
  }
};
