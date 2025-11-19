<script setup>
import { ref, onMounted } from 'vue'
const alumnos = ref([])
const estado = ref('Cargando alumnos...')
const API_URL = 'http://localhost:5000'
const emit = defineEmits(['alumno-seleccionado'])
onMounted(async () => {
  try {
    const response = await fetch(`${API_URL}/alumnos`)
    alumnos.value = await response.json()
    estado.value = 'OK'
  } catch (error) { estado.value = 'Error al cargar alumnos' }
})
</script>

<template>
  <div class="card">
    <h3 class="card-title">Paso 1: Selecciona un Alumno</h3>
    <select 
      class="select-input"
      @change="emit('alumno-seleccionado', $event.target.value)"
    >
      <option value="">-- Selecciona un alumno --</option>
      <option v-for="item in alumnos" :key="item.alumno.id" :value="item.alumno.id">
        {{ item.alumno.nombre || item.alumno.id }}
      </option>
    </select>
  </div>
</template>

<style scoped>
.card {
  background-color: var(--color-card);
  padding: 1.5rem;
  border-radius: var(--border-radius);
  box-shadow: var(--shadow);
}

.card-title {
  font-size: 1.25rem;
  font-weight: 600;
  margin: 0 0 1rem 0;
}

.select-input {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #d1d5db; /* Borde gris */
  border-radius: 0.375rem;
  background-color: #fff;
  font-size: 1rem;
}
</style>