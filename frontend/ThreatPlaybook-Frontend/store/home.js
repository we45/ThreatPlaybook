import gql from 'graphql-tag'
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
    const client = this.app.apolloProvider.defaultClient
    const query = gql`
      query {
        projects {
          name
        }
        userStories {
          id
        }
        scenarios {
          severity
        }
        scans {
          name
          vulnerabilities {
            severity
          }
        }
      }
    `
    client.query({ query }).then(({ data }) => {
      commit('FETCH_PROJECT_COUNT', data.projects.length)
      commit('FETCH_USER_STORIES_COUNT', data.userStories.length)
      commit('FETCH_THREAT_SCENARIO_COUNT', data.scenarios.length)
      commit('FETCH_SCAN_COUNT', data.scans.length)
      const items = [
        {
          color: '#009688',
          title: 'Projects',
          count: data.projects.length,
          icon: 'mdi-home'
        },
        {
          color: '#952175',
          title: 'User Stories',
          count: data.userStories.length,
          icon: 'mdi-home'
        },
        {
          color: '#E53935',
          title: 'Threat Scenarios',
          count: data.scenarios.length,
          icon: 'mdi-home'
        },
        {
          color: '#1F7087',
          title: 'Scans',
          count: data.scans.length,
          icon: 'mdi-home'
        }
      ]
      commit('FETCH_DATA', items)
      const donutSeries = []
      if (data.scenarios) {
        const highCount = []
        const mediumCount = []
        const lowCount = []
        for (const a of data.scenarios) {
          if (a.severity === 3) {
            highCount.push(a.severity)
          } else if (a.severity === 2) {
            mediumCount.push(a.severity)
          } else {
            lowCount.push(a.severity)
          }
        }
        donutSeries.push(highCount.length)
        donutSeries.push(mediumCount.length)
        donutSeries.push(lowCount.length)
        commit('FETCH_THREAT_SCENARIO_SEVERITY_CHART', donutSeries)
        const pieSeries = []
        if (data.scans) {
          const highPieCount = []
          const mediumPieCount = []
          const lowPieCount = []
          for (const scan of data.scans) {
            for (const vulSev of scan.vulnerabilities) {
              if (vulSev.severity === 3) {
                highPieCount.push(vulSev.severity)
              } else if (vulSev.severity === 2) {
                mediumPieCount.push(vulSev.severity)
              } else {
                lowPieCount.push(vulSev.severity)
              }
            }
          }
          pieSeries.push(highPieCount.length)
          pieSeries.push(mediumPieCount.length)
          pieSeries.push(lowPieCount.length)
          commit('FETCH_SEVERITY_CHART', pieSeries)
        }
      }
    })
    commit('IS_PAGE_LOADING', false)
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
