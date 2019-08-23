import Vue from 'vue'
import Router from 'vue-router'
// import HelloWorld from '@/components/HelloWorld'
import loginIndex from '@/views/login/index'
import homeIndex from '@/views/home/index'
import projectIndex from '@/views/project/index'
import singleProject from '@/views/project/singleProject'
import threatMap from '@/views/project/threatMap'
import userStories from '@/views/project/userStories'
import abuseStories from '@/views/project/abuseStories'
import threatScenarios from '@/views/project/threatScenarios'
import testCases from '@/views/project/testCases'
import scans from '@/views/project/scans'
import scan from '@/views/scan/scan'
import userStoryMap from '@/views/project/userStoryMap'

Vue.use(Router)

const routes = [
  {
    path: '/home',
    name: 'Home',
    component: homeIndex
  },
  {
    path: '/login',
    name: 'Login',
    component: loginIndex
  },
  {
    path: '/',
    name: 'Login',
    component: loginIndex
  },
  {
    path: '/project',
    name: 'project',
    component: projectIndex
  },
  {
    path: '/threat_map/:projectName',
    name: 'threatMap',
    component: threatMap
    // props: route => ({ projectName: route.params.projectName })
  },
  {
    path: '/user_story_map/:projectName',
    name: 'userStoryMap',
    component: userStoryMap
    // props: route => ({ projectName: route.params.projectName })
  },
  {
    path: '/user_stories/:projectName',
    name: 'userStories',
    component: userStories
    // props: route => ({ projectName: route.params.projectName })
  },
  {
    path: '/abuser_stories/:projectName',
    name: 'abuseStories',
    component: abuseStories
    // props: route => ({ projectName: route.params.projectName })
  },
  {
    path: '/threat_scenarios/:projectName',
    name: 'threatScenarios',
    component: threatScenarios
    // props: route => ({ projectName: route.params.projectName })
  },
  {
    path: '/test_cases/:projectName',
    name: 'testCases',
    component: testCases
    // props: route => ({ projectName: route.params.projectName })
  },
  {
    path: '/scans/:projectName',
    name: 'scans',
    component: scans
    // props: route => ({ projectName: route.params.projectName })
  },
  {
    path: '/project/:projectName',
    component: singleProject,
    props: route => ({ projectName: route.params.projectName })
  },
  {
    path: '/scan/:scanName/:projectName',
    component: scan
    // props: route => ({ projectName: route.params.projectName })
  }
]

export default new Router({
  scrollBehavior: () => ({ y: 0 }),
  mode: 'history',
  routes: routes
})
