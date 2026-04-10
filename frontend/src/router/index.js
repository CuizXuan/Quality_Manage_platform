import { createRouter, createWebHistory } from 'vue-router'
import Dashboard from '../views/Dashboard.vue'

const routes = [
  {
    path: '/',
    name: 'Dashboard',
    component: Dashboard,
  },
  {
    path: '/settings',
    name: 'Settings',
    component: () => import('../views/Settings.vue'),
  },
  {
    path: '/shortcuts',
    name: 'Shortcuts',
    component: () => import('../views/Shortcuts.vue'),
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
