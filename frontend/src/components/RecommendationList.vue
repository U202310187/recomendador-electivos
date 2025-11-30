<script setup>
import { ref, watch, computed } from 'vue'
import LoadingSpinner from './LoadingSpinner.vue'
import { fetchRecomendacionesPorModo } from '@/services/recommender.service'

const props = defineProps({
  alumnoId: String,
  modo: {
    type: [Number, String],
    default: 1
  }
})

const recomendaciones = ref([])
const estado = ref('Selecciona un modo para ver recomendaciones.')
const cargando = ref(false)
const fmt = (n) => (typeof n === 'number' ? n.toFixed(2) : '0.00')

// --- PAGINACIÓN ---
const pageSize = 5
const currentPage = ref(1)

const totalPages = computed(() =>
  recomendaciones.value.length === 0
    ? 1
    : Math.ceil(recomendaciones.value.length / pageSize)
)

const paginatedRecomendaciones = computed(() => {
  const start = (currentPage.value - 1) * pageSize
  return recomendaciones.value.slice(start, start + pageSize)
})

function goToPage(page) {
  if (page < 1 || page > totalPages.value) return
  currentPage.value = page
}

watch(
  () => [props.alumnoId, props.modo],
  async ([nuevoId, nuevoModo]) => {
    if (!nuevoId) {
      recomendaciones.value = []
      estado.value = 'Aún no hay cursos obligatorios aprobados registrados.'
      return
    }

    cargando.value = true
    estado.value = 'Buscando...'

    try {
      const data = await fetchRecomendacionesPorModo(nuevoId, nuevoModo)
      recomendaciones.value = Array.isArray(data) ? data : []
      // cada vez que cambian las recomendaciones, volvemos a la página 1
      currentPage.value = 1

      estado.value =
        recomendaciones.value.length > 0
          ? 'OK'
          : 'No se encontraron recomendaciones.'
    } catch (e) {
      console.error(e)
      recomendaciones.value = []
      currentPage.value = 1
      estado.value = 'Error al cargar recomendaciones.'
    } finally {
      cargando.value = false
    }
  },
  { immediate: true }
)

defineExpose({ fmt })
</script>

<template>
  <div class="card">
    <h3 class="card-title">Cursos Recomendados</h3>
    <div class="content">
      <LoadingSpinner v-if="estado === 'Buscando...'" />

      <div v-else-if="recomendaciones.length === 0" class="empty-state">
        <p>{{ estado }}</p>
      </div>

      <div v-else>
        <ul class="list">
          <li
            v-for="rec in paginatedRecomendaciones"
            :key="rec.curso.id"
            class="list-item"
          >
            <strong
              class="course-name"
              @click="$emit('curso-seleccionado', rec.curso.id)"
            >
              {{ rec.curso.nombre }}
            </strong>

            <div class="badge-container">
              <span class="badge score-badge">Score: {{ fmt(rec.score) }}</span>
              <span class="badge">Afinidad: {{ fmt(rec.affinity) }}</span>
              <span class="badge">Prep: {{ fmt(rec.prep) }}</span>
            </div>
          </li>
        </ul>

        <!-- Controles de paginación -->
        <div class="pagination" v-if="recomendaciones.length > pageSize">
          <button
            class="page-btn"
            @click="goToPage(currentPage - 1)"
            :disabled="currentPage === 1"
          >
            Anterior
          </button>

          <span class="page-info">
            Página {{ currentPage }} de {{ totalPages }}
          </span>

          <button
            class="page-btn"
            @click="goToPage(currentPage + 1)"
            :disabled="currentPage === totalPages"
          >
            Siguiente
          </button>
        </div>
      </div>
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
  gap: 0.5rem;
}

.list-item {
  border: 1px solid #e5e7eb;
  padding: 1rem;
  border-radius: 0.375rem;
  transition: background-color 0.2s ease-in-out, box-shadow 0.2s ease-in-out;
}

.list-item:hover {
  background-color: #fafafa;
  box-shadow: 0 1px 3px 0 rgb(0 0 0 / 0.1);
}

.course-name {
  color: var(--color-primary);
  font-weight: 600;
  font-size: 1.125rem;
  cursor: pointer;
  display: block;
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
  background-color: #dbeafe;
  color: #1e40af;
  font-weight: 700;
}

/* Paginación */
.pagination {
  margin-top: 1rem;
  display: flex;
  gap: 0.75rem;
  align-items: center;
  justify-content: center;
}

.page-btn {
  padding: 0.35rem 0.9rem;
  border-radius: 9999px;
  border: 1px solid #e5e7eb;
  background-color: white;
  font-size: 0.85rem;
  cursor: pointer;
}
.page-btn:disabled {
  opacity: 0.5;
  cursor: default;
}
.page-info {
  font-size: 0.85rem;
  color: #4b5563;
}
</style>
