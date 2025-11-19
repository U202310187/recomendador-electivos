<script setup>
import { ref, onMounted } from 'vue'
import LoadingSpinner from '../components/LoadingSpinner.vue'
import {
  fetchCursosAprobados,
  fetchAllCursos,
  agregarCursoAprobado
} from '../services/recommender.service'

const aprobados = ref([])
const todosLosCursos = ref([])
const estado = ref('Cargando cursos aprobados...')

const cursoSeleccionado = ref('')
const notaSeleccionada = ref(13)
const idAlumnoSimulado = 'ALU_001'

onMounted(() => {
  loadCursosAprobados()
  loadTodosLosCursos()
})

async function loadCursosAprobados() {
  estado.value = 'Cargando cursos aprobados...'
  try {
    aprobados.value = await fetchCursosAprobados(idAlumnoSimulado, 'APROBADO')
    estado.value = 'OK'
  } catch (e) {
    console.error(e)
    estado.value = 'Error al cargar cursos'
  }
}

async function loadTodosLosCursos() {
  try {
    todosLosCursos.value = await fetchAllCursos()
  } catch (e) {
    console.error('Error al cargar lista total de cursos', e)
  }
}

async function handleAgregarCurso() {
  if (!cursoSeleccionado.value) return

  try {
    await agregarCursoAprobado(idAlumnoSimulado, {
      id_curso: cursoSeleccionado.value,
      nota: parseInt(notaSeleccionada.value)
    })

    await loadCursosAprobados()
    cursoSeleccionado.value = ''
    notaSeleccionada.value = 13
  } catch (e) {
    console.error('Error en handleAgregarCurso', e)
    alert('Error al agregar el curso.')
  }
}
</script>

<template>
  <div>
    <h1 class="title">Mi Panel de Cursos</h1>
    <p class="subtitle">Aquí puedes ver y gestionar tus cursos aprobados.</p>

    <div class="dashboard-grid">
      <div class="card">
        <h3 class="card-title">Agregar Curso Aprobado</h3>
        <form @submit.prevent="handleAgregarCurso" class="form-container">
          
          <div class="input-group">
            <label for="curso-select">Selecciona un Curso:</label>
            <select id="curso-select" v-model="cursoSeleccionado" class="select-input">
              <option value="">-- Cursos Disponibles --</option>
              <option v-for="curso in todosLosCursos" :key="curso.id" :value="curso.id">
                {{ curso.nombre }}
              </option>
            </select>
          </div>

          <div class="input-group">
            <label for="nota-input">Nota Obtenida:</label>
            <input 
              id="nota-input" 
              type="number" 
              v-model="notaSeleccionada" 
              min="13" 
              max="20" 
              class="select-input"
            />
          </div>
          
          <button type="submit" class="auth-button">Agregar Curso</button>
        </form>
      </div>

      <div class="card">
        <h3 class="card-title">Mis Cursos Aprobados (Alumno de Prueba)</h3>
        <div class="content">
          <LoadingSpinner v-if="estado.includes('Cargando')" />
          <div v-else-if="aprobados.length === 0" class="empty-state">
            <p>Aún no has agregado cursos aprobados.</p>
          </div>
          <ul v-else class="list">
            <li v-for="item in aprobados" :key="item.curso.id" class="list-item">
              <span class="curso-nombre">{{ item.curso.nombre }}</span>
              <span class="curso-nota">Nota: {{ item.relacion.nota }}</span>
            </li>
          </ul>
        </div>
      </div>
    </div>
    
    <div class="card cta-card">
      <h3 class="card-title">¿Listo para el siguiente paso?</h3>
      <p>Usa el recomendador para encontrar tus próximos cursos electivos.</p>
      <RouterLink to="/recomendador" class="auth-button recommend-button">
        Ir al Recomendador
      </RouterLink>
    </div>
  </div>
</template>

<style scoped>
/* LOS ESTILOS NO CAMBIAN, DEJA LOS QUE YA TENÍAS */
/* ... (todo el bloque <style scoped> anterior) ... */
.title {
  font-size: 2.25rem; font-weight: 700; color: #111827; margin-bottom: 0.5rem;
}
.subtitle {
  font-size: 1.125rem; color: var(--color-text-light); margin-bottom: 2rem;
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
.content { min-height: 150px; }
.empty-state {
  display: flex; justify-content: center; align-items: center;
  height: 150px; color: var(--color-text-light);
}
.list { list-style: none; padding: 0; margin: 0; }
.list-item {
  display: flex;
  justify-content: space-between;
  padding: 0.75rem 0;
  border-bottom: 1px solid #e5e7eb;
}
.list-item:first-child { padding-top: 0; }
.curso-nombre { font-weight: 500; }
.curso-nota { color: var(--color-text-light); }
.dashboard-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 2rem;
  margin-bottom: 2rem;
}
@media (max-width: 1024px) {
  .dashboard-grid { grid-template-columns: 1fr; }
}
.form-container { display: flex; flex-direction: column; gap: 1rem; }
.input-group { display: flex; flex-direction: column; gap: 0.25rem; }
.input-group label {
  font-weight: 500;
  color: var(--color-text-light);
  font-size: 0.875rem;
}
.select-input {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 0.375rem;
  background-color: #fff;
  font-size: 1rem;
  box-sizing: border-box;
}
.auth-button {
  width: auto;
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 0.375rem;
  background-color: var(--color-primary);
  color: white;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  text-decoration: none;
  display: inline-block;
}
.cta-card {
  text-align: center;
}
.recommend-button {
  margin-top: 1rem;
}
</style>