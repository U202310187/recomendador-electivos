<script setup>
import { ref } from 'vue'
import StudentSelector from '../components/StudentSelector.vue'
import RecommendationList from '../components/RecommendationList.vue'
import CourseDetails from '../components/CourseDetails.vue'

const alumnoSeleccionadoId = ref(null)
const cursoSeleccionadoId = ref(null)

function onAlumnoSeleccionado(id) {
  alumnoSeleccionadoId.value = id
  cursoSeleccionadoId.value = null
}

function onCursoSeleccionado(id) {
  cursoSeleccionadoId.value = id
}
</script>

<template>
  <h1 class="title">Recomendador de Cursos</h1>
  <p class="subtitle">
    Selecciona un alumno para descubrir cursos electivos basados en tu perfil académico.
  </p>

  <div class="content-grid">
    <div class="column-left">
      <StudentSelector @alumno-seleccionado="onAlumnoSeleccionado" />
      <RecommendationList 
        :alumno-id="alumnoSeleccionadoId"
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
</template>

<style scoped>
/* Estos estilos se aplican solo a esta vista */
.title {
  font-size: 2.25rem; font-weight: 700; color: #111827; margin-bottom: 0.5rem;
}
.subtitle {
  font-size: 1.125rem; color: var(--color-text-light); margin-bottom: 2rem;
}
.content-grid {
  display: grid; grid-template-columns: 1fr; gap: 2rem;
}
@media (min-width: 1024px) {
  .content-grid { grid-template-columns: 1fr 1fr; }
}
.column-left {
  display: flex; flex-direction: column; gap: 2rem;
}
</style>