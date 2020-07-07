import axios from "axios";
const loginUrl = process.env.VUE_APP_API_URL;

export const state = () => ({
  isLoading: false,
  token: "",
  errorMessage: "",
  isError: false
});

export const mutations = {
  PAGE_LOADING(state, data) {
    state.isLoading = data;
  },
  STORE_TOKEN(state, data) {
    state.token = data;
    localStorage.setItem("token", data);
  },
  ERROR_MESSAGE(state, data) {
    state.errorMessage = data;
  },
  ERROR_MESSAGE_STATUS(state, data) {
    state.isError = data;
  }
};

export const actions = {
  pageLoadingError({ commit }, data) {
    commit("ERROR_MESSAGE_STATUS", data);
  },
  pageLoading({ commit }, data) {
    commit("PAGE_LOADING", data);
  },
  loginUser({ commit }, data) {
    axios
      .post("/api/login", data)
      .then(response => {
        if (response.data.success) {
          commit("STORE_TOKEN", response.data.data.token);
          commit("PAGE_LOADING", false);
          this.$router.push("/home");
        } else {
          localStorage.removeItem("token");
          commit("PAGE_LOADING", false);
          commit("ERROR_MESSAGE_STATUS", true);
          this.$router.push("/");
        }
        commit("PAGE_LOADING", false);
      })
      .catch(error => {
        if (error.response.status === 401) {
          commit("PAGE_LOADING", false);
          commit("ERROR_MESSAGE", "Invalid credentials");
          commit("ERROR_MESSAGE_STATUS", true);
        }
        if (error.response.status === 502) {
          commit("PAGE_LOADING", false);
          commit("ERROR_MESSAGE", "Bad Gateway");
          commit("ERROR_MESSAGE_STATUS", true);
        }
        if (error.response.status === 404) {
          commit("PAGE_LOADING", false);
          commit("ERROR_MESSAGE", "Page  Not found");
          commit("ERROR_MESSAGE_STATUS", true);
        }
        if (error.response.status === 403) {
          commit("PAGE_LOADING", false);
          commit("ERROR_MESSAGE", "Invalid credentials");
          commit("ERROR_MESSAGE_STATUS", true);
        }
        commit("PAGE_LOADING", false);
        commit("ERROR_MESSAGE_STATUS", true);
        localStorage.removeItem("token");
        this.$router.push("/");
      });
  }
};
export const getters = {
  isPageLoading(state) {
    if (state.isLoading) {
      return state.isLoading;
    }
  },
  userToken(state) {
    if (state.token) {
      return state.token;
    }
  },
  loginErrorMessage(state) {
    if (state.errorMessage) {
      return state.errorMessage;
    }
  },
  isLoginError(state) {
    if (state.isError) {
      return state.isError;
    }
  }
};
