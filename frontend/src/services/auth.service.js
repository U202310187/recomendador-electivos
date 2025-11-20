const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000';

export async function loginPorCodigo(codigo) {
  const limpio = (codigo || '').trim();

  if (!limpio) {
    throw new Error('Debes ingresar tu código de alumno (por ejemplo: A_1)');
  }

  const url = `${API_URL}/alumnos/by_codigo/${encodeURIComponent(limpio)}`;

  let res;
  try {
    res = await fetch(url);
  } catch (err) {
    console.error('Error de red al hacer login:', err);
    throw new Error('No se pudo conectar con el servidor.');
  }

  if (!res.ok) {
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
  } catch (err) {
    console.warn('No se pudo parsear alumnoActual desde localStorage:', err);
    return null;
  }
}

export function isLoggedIn() {
  return !!getAlumnoActual();
}

export function logout() {
  localStorage.removeItem('alumnoActual');
}