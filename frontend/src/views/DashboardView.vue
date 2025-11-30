<script setup>
import { ref, onMounted } from 'vue'
import LoadingSpinner from '../components/LoadingSpinner.vue'
import { getAlumnoActual } from '../services/auth.service'
import { fetchCursosUltimoCiclo } from '../services/recommender.service'

const cursos = ref([])
const estado = ref('CARGANDO')
const alumnoNombre = ref('')

onMounted(async () => {
  const alumno = getAlumnoActual()

  if (!alumno) {
    estado.value = 'SIN_LOGIN'
    return
  }

  alumnoNombre.value = alumno.nombre || alumno.id

  try {
    estado.value = 'CARGANDO'
    const data = await fetchCursosUltimoCiclo(alumno.id)
    const obligatoriosAprobados = data.filter(item => {
      const esObligatorio = item.curso?.tipo_curso === 'obligatorio'
      const nota = Number(item.relacion?.nota)
      const estaAprobado = !Number.isNaN(nota) ? nota >= 13 : false
      return esObligatorio && estaAprobado
    })

    cursos.value = obligatoriosAprobados
    estado.value = obligatoriosAprobados.length ? 'OK' : 'VACIO'
  } catch (e) {
    console.error(e)
    estado.value = 'ERROR'
  }
})
</script>

<template>
  <div>
    <h1 class="title">Mi Panel de Cursos</h1>
    <p class="subtitle">
      Aquí puedes ver los cursos obligatorios que has aprobado (post-ciclo),
      según la información registrada en el sistema académico.
    </p>

    <div class="dashboard-grid">
      <div class="card">
        <h3 class="card-title">Mis Cursos Obligatorios Aprobados</h3>
          <div class="content">
          <LoadingSpinner v-if="estado === 'CARGANDO'" />

          <p v-else-if="estado === 'SIN_LOGIN'" class="empty-state">
          Primero inicia sesión con tu código de alumno.
          </p>

          <p v-else-if="estado === 'VACIO'" class="empty-state">
          Aún no hay cursos obligatorios aprobados registrados.
          </p>

          <p v-else-if="estado === 'ERROR'" class="empty-state">
            Ocurrió un error al cargar tus cursos.
          </p>

          <ul v-else class="list">
            <li
              v-for="item in cursos"
              :key="item.curso.id"
              class="list-item"
            >
              <span class="curso-nombre">{{ item.curso.nombre }}</span>
              <span class="curso-nota">Nota: {{ item.relacion.nota }}</span>
            </li>
          </ul>
        </div>
      </div>

      <div class="card cta-card">
        <h3 class="card-title">¿Listo para el siguiente paso?</h3>
        <p>
          Usa el recomendador para encontrar tus próximos cursos electivos,
          basados en tu historial académico.
        </p>
        <RouterLink to="/recomendador" class="auth-button recommend-button">
          Ir al Recomendador
        </RouterLink>
      </div>
    </div>
  </div>
</template>

<style scoped>
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
  border-radius: 0.375rem;
  background-color: #e4002b;      /* rojo inicial */
  color: #ffffff;
  font-size: 1rem;
  font-weight: 700;
  text-decoration: none;
  cursor: pointer;
  display: inline-block;
  transition: all 0.2s ease-in-out;
  font-family: 'Solano Gothic MVB', 'Solano', sans-serif; /* opcional, igual que MI UPC */
}

.auth-button:hover {
  background-color: #b30021;   /* rojo más oscuro */
  color: #ffffff;              /* mantiene blanco */
  transform: translateY(-1px); /* efecto premium opcional */
}
.cta-card {
  text-align: center;
}
.recommend-button {
  margin-top: 1rem;
}
</style>