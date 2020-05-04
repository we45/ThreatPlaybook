import Vue from 'vue'
import Router from 'vue-router'
import { interopDefault } from './utils'
import scrollBehavior from './router.scrollBehavior.js'

const _4e0b1342 = () => interopDefault(import('../pages/home/index.vue' /* webpackChunkName: "pages/home/index" */))
const _7b13b92c = () => interopDefault(import('../pages/inspire.vue' /* webpackChunkName: "pages/inspire" */))
const _42c925c6 = () => interopDefault(import('../pages/projects/index.vue' /* webpackChunkName: "pages/projects/index" */))
const _5760f5f8 = () => interopDefault(import('../pages/scan/_name.vue' /* webpackChunkName: "pages/scan/_name" */))
const _250d97c4 = () => interopDefault(import('../pages/projects/_name/abuser-story.vue' /* webpackChunkName: "pages/projects/_name/abuser-story" */))
const _333f71bf = () => interopDefault(import('../pages/projects/_name/project.vue' /* webpackChunkName: "pages/projects/_name/project" */))
const _1dac4192 = () => interopDefault(import('../pages/projects/_name/test-cases.vue' /* webpackChunkName: "pages/projects/_name/test-cases" */))
const _417365f3 = () => interopDefault(import('../pages/projects/_name/threat-map.vue' /* webpackChunkName: "pages/projects/_name/threat-map" */))
const _794f6989 = () => interopDefault(import('../pages/projects/_name/threat-scenario.vue' /* webpackChunkName: "pages/projects/_name/threat-scenario" */))
const _9bc84b86 = () => interopDefault(import('../pages/projects/_name/user-story.vue' /* webpackChunkName: "pages/projects/_name/user-story" */))
const _727df380 = () => interopDefault(import('../pages/projects/_name/vulnerabilities.vue' /* webpackChunkName: "pages/projects/_name/vulnerabilities" */))
const _233b7b62 = () => interopDefault(import('../pages/index.vue' /* webpackChunkName: "pages/index" */))

// TODO: remove in Nuxt 3
const emptyFn = () => {}
const originalPush = Router.prototype.push
Router.prototype.push = function push (location, onComplete = emptyFn, onAbort) {
  return originalPush.call(this, location, onComplete, onAbort)
}

Vue.use(Router)

export const routerOptions = {
  mode: 'history',
  base: decodeURI('/'),
  linkActiveClass: 'nuxt-link-active',
  linkExactActiveClass: 'nuxt-link-exact-active',
  scrollBehavior,

  routes: [{
    path: "/home",
    component: _4e0b1342,
    name: "home"
  }, {
    path: "/inspire",
    component: _7b13b92c,
    name: "inspire"
  }, {
    path: "/projects",
    component: _42c925c6,
    name: "projects"
  }, {
    path: "/scan/:name?",
    component: _5760f5f8,
    name: "scan-name"
  }, {
    path: "/projects/:name/abuser-story",
    component: _250d97c4,
    name: "projects-name-abuser-story"
  }, {
    path: "/projects/:name/project",
    component: _333f71bf,
    name: "projects-name-project"
  }, {
    path: "/projects/:name/test-cases",
    component: _1dac4192,
    name: "projects-name-test-cases"
  }, {
    path: "/projects/:name/threat-map",
    component: _417365f3,
    name: "projects-name-threat-map"
  }, {
    path: "/projects/:name/threat-scenario",
    component: _794f6989,
    name: "projects-name-threat-scenario"
  }, {
    path: "/projects/:name/user-story",
    component: _9bc84b86,
    name: "projects-name-user-story"
  }, {
    path: "/projects/:name/vulnerabilities",
    component: _727df380,
    name: "projects-name-vulnerabilities"
  }, {
    path: "/",
    component: _233b7b62,
    name: "index"
  }],

  fallback: false
}

export function createRouter () {
  return new Router(routerOptions)
}
