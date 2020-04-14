import gql from 'graphql-tag'
export const state = () => ({
  isLoading: false,
  data: []
})
export const mutations = {
  IS_PAGE_LOADING(state, data) {
    state.isLoading = data
  },
  FETCH_DATA(state, data) {
    state.data = data
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
          id
          name
        }
      }
    `
    client.query({ query }).then(({ data }) => {
      const items = []
      if (data.projects.length > 0) {
        for (const project of data.projects) {
          items.push({ name: project.name, id: project.id })
        }
      }
      commit('FETCH_DATA', items)
    })
    commit('IS_PAGE_LOADING', false)
  }
}
export const getters = {
  isPageLoading(state) {
    return state.isLoading
  },
  getProjects(state) {
    if (state.data.length > 0) {
      return state.data
    } else {
      return []
    }
  }
}
