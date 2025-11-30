<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { loginPorCodigo } from '../services/auth.service'
import upcLogo from '@/assets/UPC_logo_transparente.png'
import sedeMonterrico from '@/assets/sedeMonterrico.jpeg'

const router = useRouter()

const codigo = ref('')
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

    const alumno = await loginPorCodigo(limpio)
    console.log('Login OK, alumno:', alumno)

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
      <img 
        :src="upcLogo"
        alt="Logo UPC"
        class="upc-logo"
      />
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

  /* Fondo con imagen */
  background-image: url('@/assets/sedeMonterrico.jpeg');
  background-size: cover;          /* que llene la pantalla */
  background-position: center;     /* centrada */
  background-repeat: no-repeat;
  background-attachment: fixed;    /* efecto bonito */
}
.upc-logo {
  width: 160px;          /* ajustable */
  display: block;
  margin: 0 auto 1rem;   /* centra + margen inferior */
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
  border-radius: 0.375rem;
  background-color: #e4002b; /* rojo MI UPC */
  color: #ffffff;
  font-size: 1rem;
  font-weight: 700;
  cursor: pointer;
  margin-top: 1rem;
  border: none;
  transition: all 0.2s ease-in-out;
  font-family: 'Solano Gothic MVB', 'Solano', sans-serif; /* opcional */
}

.auth-button:hover:not(:disabled) {
  background-color: #b30021; /* rojo oscuro */
  color: #ffffff;
  transform: translateY(-1px); /* efecto sutil */
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