import { createRouter, createWebHistory } from 'vue-router'
import Dashboard from '../views/Dashboard.vue'

const routes = [
  {
    path: '/',
    name: 'Dashboard',
    component: Dashboard,
  },
  {
    path: '/cases',
    name: 'Cases',
    component: () => import('../views/CaseManagement.vue'),
  },
  {
    path: '/scenarios',
    name: 'Scenarios',
    component: () => import('../views/ScenarioEditor.vue'),
  },
  {
    path: '/environments',
    name: 'Environments',
    component: () => import('../views/EnvironmentManage.vue'),
  },
  {
    path: '/history',
    name: 'History',
    component: () => import('../views/ExecutionHistory.vue'),
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
