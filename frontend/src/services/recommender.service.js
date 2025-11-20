const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000'

async function getJson(path) {
  const res = await fetch(`${API_URL}${path}`)
  if (!res.ok) throw new Error(`HTTP ${res.status} en ${path}`)
  return res.json()
}

export function fetchAlumnos() {
  return getJson('/alumnos')
}

// --------- RECOMENDACIONES ---------
// Algoritmo 1 – principal (endpoint /recomendar)
export function fetchRecomendacionesMain(idAlumno) {
  return getJson(`/alumnos/${idAlumno}/recomendar`)
}

// Algoritmo 2 – simple por temas (endpoint /recomendaciones)
export function fetchRecomendacionesSoloTemas(idAlumno) {
  return getJson(`/alumnos/${idAlumno}/recomendaciones`)
}

// Algoritmo 3 – misma facultad (endpoint /recomendacion)
export function fetchRecomendacionesMismaFacultad(idAlumno) {
  return getJson(`/alumnos/${idAlumno}/recomendacion`)
}

// Extra – aleatorio (endpoint /recomendaciones_aleatorio)
export function fetchRecomendacionesAleatorio(idAlumno) {
  return getJson(`/alumnos/${idAlumno}/recomendaciones_aleatorio`)
}

// Función única según modo
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

// ------- CURSOS/APROBADOS ---------
// Trae los cursos relacionados al alumno usando el endpoint
// GET /alumnos/<id_alumno>/cursos?rel_type=Directed
export function fetchCursosAprobados(idAlumno, relType = 'Directed') {
  return getJson(
    `/alumnos/${encodeURIComponent(idAlumno)}/cursos?rel_type=${encodeURIComponent(relType)}`
  )
}

// Alias que usa el Dashboard (último ciclo = cursos aprobados registrados)
export function fetchCursosUltimoCiclo(idAlumno) {
  // Por ahora es lo mismo: todos los cursos con r.type = 'Directed'
  return fetchCursosAprobados(idAlumno, 'Directed')
}

// ------- DETALLES DE CURSO ---------
export function fetchCursoDetalle(idCurso) {
  return getJson(`/cursos/${idCurso}`)
}

export function fetchCursoTemas(idCurso) {
  return getJson(`/cursos/${idCurso}/temas`)
}

export function fetchCursoRelaciones(idCurso) {
  return getJson(`/cursos/${idCurso}/relaciones`)
}