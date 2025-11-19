<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const email = ref('')
const password = ref('')
const error = ref(null)

// Esta es la lógica de SIMULACIÓN de login
function handleLogin() {
  error.value = null
  if (email.value && password.value) {
    console.log('Login exitoso (simulado)');
    
    // 1. Guarda la variable "userLoggedIn" (la de la simulación)
    localStorage.setItem('userLoggedIn', 'true');
    
    // 2. Redirige al NUEVO panel de cursos
    router.push('/'); 
    
  } else {
    error.value = 'Por favor, ingresa tus credenciales.';
  }
}
</script>

<template>
  <div class="auth-container">
    <div class="auth-card">
      <h1 class="auth-title">Bienvenido</h1>
      
      <form @submit.prevent="handleLogin">
        <div class="input-group">
          <label for="email">Usuario (Email)</label>
          <input v-model="email" type="email" id="email" class="input-field" />
        </div>
        
        <div class="input-group">
          <label for="password">Contraseña</label>
          <input v-model="password" type="password" id="password" class="input-field" />
        </div>
        
        <p v-if="error" class="error-message">{{ error }}</p>

        <button type="submit" class="auth-button">Entrar</button>
      </form>

      <div class="auth-link">
        ¿No tienes cuenta? <RouterLink to="/registro">Regístrate</RouterLink>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* Estilos inspirados en tus wireframes (rojo + tarjetas) */
.auth-container {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  background-color: #991b1b; /* Rojo oscuro */
}
.auth-card {
  background-color: var(--color-card, #fff);
  padding: 2.5rem;
  border-radius: var(--border-radius, 8px);
  box-shadow: var(--shadow, 0 10px 15px -3px rgba(0,0,0,0.1));
  width: 100%;
  max-width: 400px;
}
.auth-title {
  font-size: 1.875rem;
  font-weight: 700;
  text-align: center;
  margin-bottom: 1.5rem;
  color: #000;
}
.input-group {
  margin-bottom: 1rem;
}
.input-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
  color: var(--color-text-light, #6b7280);
}
.input-field {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 0.375rem;
  box-sizing: border-box; /* Importante para el padding */
}
.auth-button {
  width: 100%;
  padding: 0.75rem;
  border: none;
  border-radius: 0.375rem;
  background-color: var(--color-primary, #2563eb);
  color: white;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  margin-top: 1rem;
}
.auth-link {
  margin-top: 1.5rem;
  text-align: center;
  color: var(--color-text-light, #6b7280);
}
.auth-link a {
  color: var(--color-primary, #2563eb);
  font-weight: 500;
  text-decoration: none;
}
.auth-link a:hover {
  text-decoration: underline;
}
.error-message {
  color: #dc2626; /* Rojo de error */
  font-size: 0.875rem;
  text-align: center;
  margin-bottom: 1rem;
}
</style>