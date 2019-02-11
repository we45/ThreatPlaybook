import Login from "./components/Login.vue";
import ProjectHome from "./components/ProjectHome.vue";
import SingleProject from "./components/SingleProject";

export const routes = [
  { path: "/", component: Login },
  { path: "/projects", component: ProjectHome },
  {
    path: "/project/:projectName",
    component: SingleProject,
    props: (route) => ({ projectName: route.params.projectName })
  }
];
