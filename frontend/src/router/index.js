import { createRouter, createWebHistory } from 'vue-router'

// Importamos las Vistas y el Layout
import AppLayout from '../views/AppLayout.vue'
import DashboardView from '../views/DashboardView.vue'
import RecommenderView from '../views/RecommenderView.vue'
import Login from '../views/Login.vue'
import Register from '../views/Register.vue'

const routes = [
  // --- Rutas de Autenticación (fondo rojo, sin navbar) ---
  // Estas son rutas separadas que ya no usaremos por defecto
  {
    path: '/login',
    name: 'Login',
    component: Login
  },
  {
    path: '/registro',
    name: 'Register',
    component: Register
  },

  // --- Rutas de la Aplicación (fondo gris, CON navbar) ---
  // El "AppLayout" ahora es el componente para la ruta RAÍZ '/'
  {
    path: '/', 
    component: AppLayout, // Carga el layout (con Navbar)
    // No hay guardias, no hay redirecciones raras.
    children: [
      {
        path: '', // Si la ruta es SÓLO '/', muestra el Dashboard
        name: 'Dashboard',
        component: DashboardView
      },
      {
        path: 'recomendador', // La ruta es /recomendador
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

export default router