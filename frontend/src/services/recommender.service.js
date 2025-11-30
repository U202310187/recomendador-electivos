const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000'

async function getJson(path) {
  const res = await fetch(`${API_URL}${path}`)
  if (!res.ok) throw new Error(`HTTP ${res.status} en ${path}`)
  return res.json()
}

export function fetchAlumnos() {
  return getJson('/alumnos')
}

export function fetchRecomendacionesMain(idAlumno) {
  return getJson(`/alumnos/${idAlumno}/recomendar`)
}

export function fetchRecomendacionesSoloTemas(idAlumno) {
  return getJson(`/alumnos/${idAlumno}/recomendaciones`)
}

export function fetchRecomendacionesMismaFacultad(idAlumno) {
  return getJson(`/alumnos/${idAlumno}/recomendacion`)
}

export function fetchRecomendacionesAleatorio(idAlumno) {
  return getJson(`/alumnos/${idAlumno}/recomendaciones_aleatorio`)
}

export function fetchRecomendacionesPorModo(idAlumno, modo) {
  const m = Number(modo) || 1

  switch (m) {
    case 2:
      return fetchRecomendacionesSoloTemas(idAlumno)
    case 3:
      return fetchRecomendacionesMismaFacultad(idAlumno)
    case 4:
      return fetchRecomendacionesAleatorio(idAlumno)
    default:
      return fetchRecomendacionesMain(idAlumno)
  }
}

export function fetchCursosAprobados(idAlumno, relType = 'Directed') {
  return getJson(
    `/alumnos/${encodeURIComponent(idAlumno)}/cursos?rel_type=${encodeURIComponent(relType)}`
  )
}

export function fetchCursosUltimoCiclo(idAlumno) {
  return fetchCursosAprobados(idAlumno, 'Directed')
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