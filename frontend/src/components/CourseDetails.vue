<script setup>
import { ref, watch } from 'vue'
import LoadingSpinner from './LoadingSpinner.vue'
import {
  fetchCursoDetalle,
  fetchCursoTemas,
  fetchCursoRelaciones
} from '../services/recommender.service'

const props = defineProps({ cursoId: String })
const emit = defineEmits(['curso-seleccionado'])

const detalle = ref(null)
const temas = ref([])
const relaciones = ref([])
const estado = ref('Haz clic en un curso para ver sus detalles.')

// --- LÓGICA DE DIAGNÓSTICO ---
watch(() => props.cursoId, async (newId) => {
  if (!newId) {
    estado.value = 'Haz clic en un curso para ver sus detalles.'
    detalle.value = null
    temas.value = []
    relaciones.value = []
    return
  }

  // Limpiamos todo
  detalle.value = null
  temas.value = []
  relaciones.value = []

  try {
    estado.value = 'Cargando (1/3) Detalles...'
    const detalleData = await fetchCursoDetalle(newId)
    detalle.value = detalleData.curso

    estado.value = 'Cargando (2/3) Temas...'
    temas.value = await fetchCursoTemas(newId)

    estado.value = 'Cargando (3/3) Relaciones...'
    relaciones.value = await fetchCursoRelaciones(newId)

    estado.value = 'OK'
  } catch (error) {
    console.error('Error en el diagnóstico:', error)
    estado.value = `Error: ${error.message}`
  }
})
</script>

<template>
  <div class="card sticky-card">
    <h3 class="card-title">Detalle del Curso</h3>
    <div class="content">
      
      <LoadingSpinner v-if="estado.includes('Cargando')" />
      
      <div v-else-if="estado === 'OK' && detalle" class="details-container">
        <h4 class="detail-title">Nombre: {{ detalle.nombre }}</h4>
        <ul class="detail-list">
          <li><strong>Tipo:</strong> {{ detalle.tipo_curso }}</li>
          <li><strong>Mención:</strong> {{ detalle.mencion || 'N/A' }}</li>
        </ul>
        <div class="detail-section">
          <h5 class="section-title">Temas que cubre:</h5>
          <ul v-if="temas.length > 0" class="detail-list">
            <li v-for="item in temas" :key="item.tema.id">{{ item.tema.nombre }}</li>
          </ul>
          <p v-else class="empty-text">No se encontraron temas.</p>
        </div>
        <div class="detail-section">
          <h5 class="section-title">Relaciones (Prerrequisitos, etc.):</h5>
          <ul v-if="relaciones.length > 0" class="detail-list">
  <li
    v-for="item in relaciones"
    :key="item.vecino?.id ?? item.relCSV"
  >
    <span>{{ item.relCSV }} -> </span>

    <template
      v-if="
        item.vecino &&
        Array.isArray(item.vecino.labels) &&
        item.vecino.labels.includes('Curso')
      "
    >
      <strong
        class="course-link"
        @click="emit('curso-seleccionado', item.vecino.id)"
      >
        {{ item.vecino.nombre || item.vecino.id }}
      </strong>
    </template>

    <template v-else>
      <span class="node-text">
        {{ item.vecino?.nombre || item.vecino?.id || 'Nodo sin datos' }}
      </span>
    </template>
  </li>
</ul>
          <p v-else class="empty-text">No se encontraron relaciones.</p>
        </div>
      </div>
      
      <div v-else class="empty-state">
        <p>{{ estado }}</p>
      </div>

    </div>
  </div>
</template>

<style scoped>
/* Los estilos no cambian */
.card {
  background-color: var(--color-card);
  padding: 1.5rem;
  border-radius: var(--border-radius);
  box-shadow: var(--shadow);
}
.sticky-card {
  position: sticky;
  top: 2rem;
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
.details-container {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}
.detail-title {
  font-size: 1.5rem;
  font-weight: 700;
}
.detail-list {
  list-style-type: disc;
  list-style-position: inside;
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  padding-left: 0.25rem;
}
.section-title {
  font-size: 1.125rem;
  font-weight: 600;
  margin-bottom: 0.5rem;
  border-bottom: 1px solid #e5e7eb;
  padding-bottom: 0.25rem;
}
.empty-text {
  color: var(--color-text-light);
  font-size: 0.875rem;
}
.course-link {
  color: var(--color-primary);
  font-weight: 600;
  cursor: pointer;
}
.course-link:hover {
  text-decoration: underline;
}
.node-text {
  color: var(--color-text-light);
  font-style: italic;
}
</style>     