export const state = () => ({
  isLoading: false,
  data: [],
  projectCount: 0,
  userStoriesCount: 0,
  threatScenarioCount: 0,
  scanCount: 0,
  threatScenarioSevChart: [],
  severityChart: []
})
export const mutations = {
  IS_PAGE_LOADING(state, data) {
    state.isLoading = data
  },
  FETCH_DATA(state, data) {
    state.data = data
  },
  FETCH_PROJECT_COUNT(state, data) {
    state.projectCount = data
  },
  FETCH_USER_STORIES_COUNT(state, data) {
    state.userStoriesCount = data
  },
  FETCH_THREAT_SCENARIO_COUNT(state, data) {
    state.threatScenarioCount = data
  },
  FETCH_SCAN_COUNT(state, data) {
    state.scanCount = data
  },
  FETCH_THREAT_SCENARIO_SEVERITY_CHART(state, data) {
    state.threatScenarioSevChart = data
  },
  FETCH_SEVERITY_CHART(state, data) {
    state.severityChart = data
  }
}
export const actions = {
  showPageLoading({ commit }, data) {
    commit('IS_PAGE_LOADING', data)
  },
  fetchData({ commit }) {
    commit("IS_PAGE_LOADING", false);
  }    
}
export const getters = {
  isPageLoading(state) {
    return state.isLoading
  },
  getProjectCount(state) {
    if (state.projectCount) {
      return state.projectCount
    }
  },
  getUserStoriesCount(state) {
    if (state.userStoriesCount) {
      return state.userStoriesCount
    }
  },
  getThreatScenarioCount(state) {
    if (state.threatScenarioCount) {
      return state.threatScenarioCount
    }
  },
  getScanCount(state) {
    if (state.scanCount) {
      return state.scanCount
    }
  },
  getCountList(state) {
    if (state.data) {
      return state.data
    }
  },
  fetchThreatScenarioSevChartData(state) {
    if (state.threatScenarioSevChart) {
      return state.threatScenarioSevChart
    }
  },
  fetchSeverityChartData(state) {
    if (state.severityChart) {
      return state.severityChart
    }
  }
}
