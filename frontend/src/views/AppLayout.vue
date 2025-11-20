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
  <div class="app-layout">
    <header class="navbar">
      <div class="navbar-left">
        <span class="brand">Recomendador</span>

        <RouterLink
          :to="{ name: 'Dashboard' }"
          class="nav-link"
          :class="{ active: isDashboard }"
        >
          Mi Panel
        </RouterLink>

        <RouterLink
          :to="{ name: 'Recommender' }"
          class="nav-link"
          :class="{ active: isRecommender }"
        >
          Recomendador
        </RouterLink>
      </div>

      <div class="navbar-right">
        <span v-if="alumno" class="alumno-label">
          {{ alumno.nombre || alumno.id }}
        </span>
        <button class="logout-button" @click="handleLogout">
          Cerrar Sesión
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

/* NAVBAR */
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
  font-weight: 700;
  font-size: 1.25rem;
  color: var(--color-primary, #2563eb);
}

.nav-link {
  font-size: 0.95rem;
  color: #4b5563;
  text-decoration: none;
  padding-bottom: 0.25rem;
  border-bottom: 2px solid transparent;
}

.nav-link.active {
  color: #111827;
  border-color: var(--color-primary, #2563eb);
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
  border: none;
  background-color: #dc2626;
  color: #fff;
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
}

.main-content {
  max-width: 1280px;
  width: 100%;
  margin: 0 auto;
  padding: 2rem;
  box-sizing: border-box;
}
</style>