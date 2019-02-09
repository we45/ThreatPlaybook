import Login from "./components/Login.vue";
import ProjectHome from "./components/ProjectHome.vue";

export const routes = [
  { path: "/", component: Login },
  { path: "/projects", component: ProjectHome }
];
