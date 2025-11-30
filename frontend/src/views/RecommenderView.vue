<script setup>
import { ref, onMounted } from 'vue'
import RecommendationList from '../components/RecommendationList.vue'
import CourseDetails from '../components/CourseDetails.vue'
import { getAlumnoActual } from '../services/auth.service'

const alumnoId = ref(null)
const alumnoNombre = ref('')
const cursoSeleccionadoId = ref(null)
const modo = ref(1)
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
        <strong>{{ alumnoNombre }}</strong>, estos son los algoritmos de recomendación que te ayudarán a elegir tus próximos cursos electivos.
      </span>
      <span v-else>{{ estado }}</span>
    </p>

    <div v-if="estado === 'OK'">
      <div class="card mode-card">
        <h3 class="card-title">Modos de recomendación</h3>
        <div class="mode-options">
          <button
            type="button"
            class="mode-button"
            :class="{ active: modo === 1 }"
            @click="modo = 1"
          >
            Algoritmo 1 – Recomendación por preparación y afinidad temática
          </button>

          <button
            type="button"
            class="mode-button"
            :class="{ active: modo === 2 }"
            @click="modo = 2"
          >
            Algoritmo 2 – Recomendación por temas comunes
          </button>

          <button
            type="button"
            class="mode-button"
            :class="{ active: modo === 3 }"
            @click="modo = 3"
          >
            Algoritmo 3 – Recomendación por misma facultad
          </button>

          <button
            type="button"
            class="mode-button"
            :class="{ active: modo === 4 }"
            @click="modo = 4"
          >
            Algoritmo 4 – Exploración aleatoria (Fisher–Yates)
          </button>
        </div>
      </div>

      <div class="content-grid">
        <div class="column-left">
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

.mode-card {
  margin-bottom: 2rem;
}

.mode-options {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  align-items: flex-start;
}

.mode-button {
  padding: 0.7rem 1.2rem;
  border-radius: 0.75rem;
  border: 1px solid #d1d5db;
  background-color: #ffffff;
  color: #374151;
  font-size: 0.95rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease-in-out;
  font-family: 'Solano Gothic MVB', 'Solano', sans-serif;
  width: auto;     
  display: inline-block;  
  text-align: left;
  min-width: 280px;
}

.mode-button:hover {
  color: #ffffff;
  border-color: #e4002b;
  background-image: linear-gradient(
    90deg,
    #d90429 0%,
    #e4002b 50%,
    #ff0033 100%
  );
}

.mode-button.active {
  color: #ffffff;
  border-color: #e4002b;
  background-image: linear-gradient(
    90deg,
    #d90429 0%,
    #e4002b 50%,
    #ff0033 100%
  );
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.15);
}
</style>
