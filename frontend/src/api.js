// Cliente HTTP único. La URL del backend se configura con VUE_APP_API_URL (ver .env.example).
import axios from 'axios';

export const API_URL = process.env.VUE_APP_API_URL || 'http://127.0.0.1:8000';

const api = axios.create({ baseURL: API_URL, timeout: 15000 });

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token && !config.headers.Authorization) {
    config.headers.Authorization = `Token ${token}`;
  }
  return config;
});

// Si el token expiró/es inválido en una ruta autenticada, limpiamos la sesión.
api.interceptors.response.use(
  (r) => r,
  (error) => {
    if (error.response && error.response.status === 401 && localStorage.getItem('token')) {
      localStorage.removeItem('token');
      localStorage.removeItem('username');
    }
    return Promise.reject(error);
  }
);

export function errorMessage(error, fallback = 'Ocurrió un error. Intentá de nuevo.') {
  const data = error && error.response && error.response.data;
  if (!data) return fallback;
  if (typeof data === 'string') return fallback;
  if (data.detail) return data.detail;
  if (data.error) return data.error;
  const first = Object.entries(data)[0];
  if (!first) return fallback;
  const [field, msgs] = first;
  return `${field}: ${Array.isArray(msgs) ? msgs[0] : JSON.stringify(msgs)}`;
}

export default api;
