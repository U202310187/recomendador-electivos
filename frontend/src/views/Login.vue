<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { loginPorCodigo } from '../services/auth.service'

const router = useRouter()

// Código de alumno, estado y error
const codigo = ref('')           // puedes poner 'A_1' aquí para probar rápido
const loading = ref(false)
const error = ref(null)

async function handleLogin() {
  error.value = null

  const limpio = (codigo.value || '').trim()
  if (!limpio) {
    error.value = 'Debes ingresar tu código de alumno (por ejemplo: A_1)'
    return
  }

  try {
    loading.value = true

    // 1. Llamamos al backend: GET /alumnos/by_codigo/<codigo>
    const alumno = await loginPorCodigo(limpio)
    console.log('Login OK, alumno:', alumno)

    // 2. Navegamos al dashboard por NOMBRE de ruta
    await router.push({ name: 'Dashboard' })
  } catch (e) {
    console.error('Error en login:', e)
    error.value = e.message || 'No se pudo iniciar sesión.'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="auth-container">
    <div class="auth-card">
      <h1 class="auth-title">Bienvenido</h1>

      <form @submit.prevent="handleLogin">
        <div class="input-group">
          <label for="codigo">Código de alumno</label>
          <input
          v-model="codigo"
          type="text"
          id="codigo"
          class="input-field"
          placeholder="Ejemplo: A_1"
          :disabled="loading"
          />
        </div>

        <p v-if="error" class="error-message">{{ error }}</p>

        <button
          type="submit"
          class="auth-button"
          :disabled="loading"
        >
          {{ loading ? 'Ingresando...' : 'Entrar' }}
        </button>
      </form>
    </div>
  </div>
</template>

<style scoped>
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
  box-shadow: var(
    --shadow,
    0 10px 15px -3px rgba(0, 0, 0, 0.1)
  );
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
  box-sizing: border-box;
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
.auth-button:disabled {
  opacity: 0.7;
  cursor: default;
}
.error-message {
  color: #dc2626;
  font-size: 0.875rem;
  text-align: center;
  margin-bottom: 1rem;
}
</style>