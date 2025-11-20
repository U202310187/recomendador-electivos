<script setup>
import { ref, onMounted } from 'vue'
import RecommendationList from '../components/RecommendationList.vue'
import CourseDetails from '../components/CourseDetails.vue'
import { getAlumnoActual } from '../services/auth.service'

const alumnoId = ref(null)
const alumnoNombre = ref('')
const cursoSeleccionadoId = ref(null)
const modo = ref(1) // 1, 2, 3 o 4 (extra aleatorio)
const estado = ref('Cargando información del alumno...')

onMounted(() => {
  const a = getAlumnoActual()

  if (!a || !a.id) {
    estado.value = 'Primero inicia sesión con tu código de alumno.'
    return
  }

  alumnoId.value = a.id
  alumnoNombre.value = a.nombre || a.codigo || a.id
  estado.value = 'OK'
})

function onCursoSeleccionado(id) {
  cursoSeleccionadoId.value = id
}
</script>

<template>
  <div>
    <h1 class="title">Recomendador de Cursos</h1>

    <p class="subtitle">
      <span v-if="estado === 'OK'">
        Recomendaciones personalizadas para
        <strong>{{ alumnoNombre }}</strong>, basadas en tus cursos
        obligatorios aprobados.
      </span>
      <span v-else>
        {{ estado }}
      </span>
    </p>

    <!-- Solo se muestra el resto si hay alumno logueado -->
    <div v-if="estado === 'OK'">
      <!-- Selector de modo / algoritmo -->
      <div class="card mode-card">
        <h3 class="card-title">Modo de recomendación</h3>
        <div class="mode-options">
          <label>
            <input type="radio" value="1" v-model.number="modo" />
            Algoritmo 1 – Preparación + afinidad temática (principal)
          </label>
          <label>
            <input type="radio" value="2" v-model.number="modo" />
            Algoritmo 2 – Recomendación simple por temas comunes
          </label>
          <label>
            <input type="radio" value="3" v-model.number="modo" />
            Algoritmo 3 – Misma facultad + umbral de afinidad
          </label>
          <label>
            <input type="radio" value="4" v-model.number="modo" />
            Extra – Exploración aleatoria (Fisher–Yates sobre candidatos)
          </label>
        </div>
      </div>

      <div class="content-grid">
        <div class="column-left">
          <!-- Ya NO hay StudentSelector; usamos el alumno logueado -->
          <RecommendationList
            :alumno-id="alumnoId"
            :modo="modo"
            @curso-seleccionado="onCursoSeleccionado"
          />
        </div>

        <div class="column-right">
          <CourseDetails
            :curso-id="cursoSeleccionadoId"
            @curso-seleccionado="onCursoSeleccionado"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.title {
  font-size: 2.25rem;
  font-weight: 700;
  color: #111827;
  margin-bottom: 0.5rem;
}

.subtitle {
  font-size: 1.125rem;
  color: var(--color-text-light);
  margin-bottom: 2rem;
}

.content-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 2rem;
}

@media (min-width: 1024px) {
  .content-grid {
    grid-template-columns: 1fr 1fr;
  }
}

.column-left {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

/* Tarjeta de modos */
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

.mode-card {
  margin-bottom: 2rem;
}

.mode-options {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  font-size: 0.95rem;
}

.mode-options label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
}
</style>