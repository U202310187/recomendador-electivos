import { createRouter, createWebHistory } from 'vue-router'
import { getAlumnoActual } from '../services/auth.service'

import AppLayout from '../views/AppLayout.vue'
import DashboardView from '../views/DashboardView.vue'
import RecommenderView from '../views/RecommenderView.vue'
import Login from '../views/Login.vue'

const routes = [
  { path: '/login', name: 'Login', component: Login },

  {
    path: '/',
    component: AppLayout,
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        name: 'Dashboard',
        component: DashboardView
      },
      {
        path: 'recomendador',
        name: 'Recommender',
        component: RecommenderView
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  const logged = getAlumnoActual()

  if (to.meta.requiresAuth && !logged) {
    return next('/login')
  }

  if (to.path === '/login' && logged) {
    return next('/')
  }

  next()
})

export default router