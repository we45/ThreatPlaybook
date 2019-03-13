import Login from "./components/Login.vue";
import ProjectHome from "./components/ProjectHome.vue";
import SingleProject from "./components/SingleProject";
import ThreatMap from './components/ThreatMap'
import Home from './components/Home'
import UserStoryMap from './components/UserStoryMap'

export const routes = [
  { path: "/", component: Login },
  { path: "/home", component: Home },
  { path: "/projects", component: ProjectHome },
  {
    path: "/project/:projectName",
    component: SingleProject,
    props: route => ({ projectName: route.params.projectName })
  },
  {
    path: "/map/:projectName",
    component: ThreatMap,
    props: route => ({ projectName: route.params.projectName })
  },
  {
    path: "/story/:projectName",
    component: UserStoryMap,
    props: route => ({ projectName: route.params.projectName })
  }
];
