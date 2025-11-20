const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000';

export async function loginPorCodigo(codigo) {
  const limpio = (codigo || '').trim();

  if (!limpio) {
    throw new Error('Debes ingresar tu código de alumno (por ejemplo: A_1)');
  }

  const res = await fetch(
    `${API_URL}/alumnos/by_codigo/${encodeURIComponent(limpio)}`
  );

  if (!res.ok) {
    // 404 u otro error desde el backend
    throw new Error('Alumno no encontrado');
  }

  const data = await res.json();
  const alumno = data.alumno || data;

  localStorage.setItem('alumnoActual', JSON.stringify(alumno));

  return alumno;
}

export function getAlumnoActual() {
  const raw = localStorage.getItem('alumnoActual');
  if (!raw) return null;
  try {
    return JSON.parse(raw);
  } catch {
    return null;
  }
}

export function logout() {
  localStorage.removeItem('alumnoActual');
}