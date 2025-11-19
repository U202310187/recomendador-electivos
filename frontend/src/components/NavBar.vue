<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()

function handleLogout() {
  localStorage.removeItem('user') // Borra al usuario
  router.push('/login') // Lo manda al login
}
</script>

<template>
  <nav class="navbar">
    <div class="navbar-container">
      <div class="logo">Recomendador</div>
      <div class="nav-links">
        <RouterLink to="/" class="nav-link">Mi Panel</RouterLink>
        <RouterLink to="/recomendador" class="nav-link">Recomendador</RouterLink>
      </div>
      <button @click="handleLogout" class="logout-button">Cerrar Sesión</button>
    </div>
  </nav>
</template>

<style scoped>
.navbar {
  background-color: var(--color-card);
  box-shadow: var(--shadow);
  padding: 0 2rem;
  border-bottom: 1px solid #e5e7eb;
}
.navbar-container {
  display: flex;
  align-items: center;
  justify-content: space-between;
  max-width: 1280px;
  margin: 0 auto;
  height: 64px;
}
.logo {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--color-primary);
}
.nav-links {
  display: flex;
  gap: 1.5rem;
}
.nav-link {
  font-size: 1rem;
  font-weight: 500;
  color: var(--color-text-light);
  text-decoration: none;
  padding: 0.5rem 0;
  border-bottom: 2px solid transparent;
}
.nav-link:hover {
  color: var(--color-text);
}
/* Estilo para la ruta activa */
.router-link-exact-active {
  color: var(--color-primary);
  border-bottom-color: var(--color-primary);
}
.logout-button {
  background-color: #ef4444; /* Rojo */
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 0.375rem;
  font-weight: 500;
  cursor: pointer;
}
.logout-button:hover {
  background-color: #dc2626;
}
</style>