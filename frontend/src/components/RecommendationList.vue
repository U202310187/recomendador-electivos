<script setup>
import { ref, watch } from 'vue'
import LoadingSpinner from './LoadingSpinner.vue'
import { fetchRecomendaciones } from '../services/recommender.service'

const props = defineProps({ alumnoId: String })
const recomendaciones = ref([])
const estado = ref('Selecciona un alumno para ver sus recomendaciones.')

watch(() => props.alumnoId, async (newId) => {
  if (!newId) {
    recomendaciones.value = []
    estado.value = 'Selecciona un alumno para ver sus recomendaciones.'
    return
  }

  try {
    estado.value = 'Buscando...'
    const data = await fetchRecomendaciones(newId)
    recomendaciones.value = data
    estado.value = data.length > 0 ? 'OK' : 'No se encontraron recomendaciones.'
  } catch (error) {
    console.error(error)
    estado.value = 'Error al cargar recomendaciones.'
  }
})
</script>

<template>
  <div class="card">
    <h3 class="card-title">Paso 2: Cursos Recomendados</h3>
    <div class="content">
      <LoadingSpinner v-if="estado === 'Buscando...'" />
      <div v-else-if="recomendaciones.length === 0" class="empty-state">
        <p>{{ estado }}</p>
      </div>
      <ul v-else class="list">
        <li v-for="rec in recomendaciones" :key="rec.curso.id" class="list-item">
          <strong 
            class="course-name"
            @click="$emit('curso-seleccionado', rec.curso.id)"
          >
            {{ rec.curso.nombre }}
          </strong>
          <div class="badge-container">
            <span class="badge score-badge">Score: {{ (rec.score ?? 0).toFixed(2) }}</span>
            <span class="badge">Afinidad: {{ (rec.affinity ?? 0).toFixed(2) }}</span>
            <span class="badge">Prep: {{ (rec.prep ?? 0).toFixed(2) }}</span>
          </div>
        </li>
      </ul>
    </div>
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
.content {
  min-height: 200px;
}
.empty-state {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 200px;
  color: var(--color-text-light);
}
.list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 0.5rem; /* Reducimos el espacio */
}

/* --- ESTILOS MEJORADOS --- */
.list-item {
  border: 1px solid #e5e7eb; /* Borde sutil */
  padding: 1rem;
  border-radius: 0.375rem; /* Bordes redondeados */
  transition: background-color 0.2s ease-in-out, box-shadow 0.2s ease-in-out;
}
/* Efecto hover intuitivo */
.list-item:hover {
  background-color: #fafafa; /* Fondo gris muy claro */
  box-shadow: 0 1px 3px 0 rgb(0 0 0 / 0.1);
}

.course-name {
  color: var(--color-primary);
  font-weight: 600;
  font-size: 1.125rem;
  cursor: pointer;
  display: block; /* Hacemos que todo el nombre sea un bloque */
}
.course-name:hover {
  text-decoration: underline;
}
.badge-container {
  display: flex;
  gap: 0.5rem;
  margin-top: 0.5rem;
  flex-wrap: wrap;
}
.badge {
  font-size: 0.75rem;
  font-weight: 500;
  background-color: #f3f4f6;
  color: #374151;
  padding: 0.25rem 0.75rem;
  border-radius: 9999px;
}
.score-badge {
  background-color: #dbeafe; /* Azul claro */
  color: #1e40af; /* Azul oscuro */
  font-weight: 700;
}
</style>