const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000'

async function getJson(path) {
  const res = await fetch(`${API_URL}${path}`)
  if (!res.ok) throw new Error(`HTTP ${res.status} en ${path}`)
  return res.json()
}

export function fetchAlumnos() {
  return getJson('/alumnos')
}

export function fetchRecomendaciones(idAlumno) {
  return getJson(`/alumnos/${idAlumno}/recomendaciones`)
}

export function fetchCursoDetalle(idCurso) {
  return getJson(`/cursos/${idCurso}`)
}

export function fetchCursoTemas(idCurso) {
  return getJson(`/cursos/${idCurso}/temas`)
}

export function fetchCursoRelaciones(idCurso) {
  return getJson(`/cursos/${idCurso}/relaciones`)
}

export function fetchCursosAprobados(idAlumno, relType = 'APROBADO') {
  return getJson(`/alumnos/${idAlumno}/cursos?rel_type=${relType}`)
}

export function fetchAllCursos() {
  return getJson('/cursos')
}

export async function agregarCursoAprobado(idAlumno, { id_curso, nota }) {
  const res = await fetch(`${API_URL}/alumnos/${idAlumno}/cursos`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ id_curso, nota })
  })

  if (!res.ok) {
    throw new Error(`HTTP ${res.status} al agregar curso`)
  }
}