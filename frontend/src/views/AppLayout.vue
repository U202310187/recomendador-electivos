<script setup>
import { computed } from 'vue'
import { useRoute, useRouter, RouterLink, RouterView } from 'vue-router'
import { getAlumnoActual, logout } from '../services/auth.service'

const route = useRoute()
const router = useRouter()

const alumno = computed(() => getAlumnoActual())

const isDashboard = computed(() => route.name === 'Dashboard')
const isRecommender = computed(() => route.name === 'Recommender')

function handleLogout() {
  logout()
  router.push('/login')
}
</script>

<template>
  <link rel="stylesheet" href="https://mi.upc.edu.pe/fonts/solano/solano-font.css" />

  <div class="app-layout">
    <header class="navbar">
      <div class="navbar-left">
        <div class="brand">
        <img src="@/assets/UPC_logo_transparente.png" alt="UPC Logo" class="brand-logo" />
        <span>MI UPC&nbsp;|&nbsp;RECOMENDADOR</span>
        </div>

        <RouterLink
          :to="{ name: 'Dashboard' }"
          class="nav-link"
          :class="{ active: isDashboard }"
        >
          MI PANEL
        </RouterLink>

        <RouterLink
          :to="{ name: 'Recommender' }"
          class="nav-link"
          :class="{ active: isRecommender }"
        >
          RECOMENDADOR
        </RouterLink>
      </div>

      <div class="navbar-right">
        <span v-if="alumno" class="alumno-label">
          Bienvenido, {{ alumno.nombre || alumno.id }}
        </span>
        <button class="logout-button" @click="handleLogout">
          CERRAR SESIÓN
        </button>
      </div>
    </header>

    <main class="main-content">
      <RouterView />
    </main>
  </div>
</template>

<style scoped>
.app-layout {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  background-color: var(--color-bg);
}

.navbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.75rem 2rem;
  background-color: #ffffff;
  border-bottom: 1px solid #e5e7eb;
}

.navbar-left {
  display: flex;
  align-items: center;
  gap: 1.5rem;
}

.brand {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  font-family: 'Solano Gothic MVB', 'Solano', sans-serif;
  font-weight: 700;
  font-size: 1.25rem;
  color: #221c63;
}

.brand-logo {
  height: 34px; 
  width: auto;
  display: block;
}

.nav-link {
  font-family: 'Solano Gothic MVB', 'Solano', sans-serif;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.2px;
  font-size: 0.92rem;

  color: #7a7575;
  text-decoration: none;
  padding: 0.4rem 0.8rem;
  border-radius: 4px;
  transition: all 0.2s ease-in-out;
}

.nav-link:hover {
  background-color: #e4002b;
  color: #ffffff;
}

.nav-link.active {
  font-family: 'Solano Gothic MVB', 'Solano', sans-serif;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.2px;
  color: #e4002b;
  background-color: transparent;
  display: flex;
  align-items: center;
}

.navbar-right {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.alumno-label {
  font-size: 0.9rem;
  color: #4b5563;
}

.logout-button {
  padding: 0.4rem 0.9rem;
  border-radius: 0.375rem;
  border: 2px solid #4b1fda;
  background-color: #ffffff;
  color: #4b1fda;
  font-size: 0.9rem;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s ease-in-out;
}

.logout-button:hover {
  background-color: #4b1fda;
  color: #ffffff;
}

.main-content {
  max-width: 1280px;
  width: 100%;
  margin: 0 auto;
  padding: 2rem;
  box-sizing: border-box;
}
</style>
