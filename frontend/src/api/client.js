import axios from 'axios';

const API_BASE = 'http://localhost:8000/api';

const client = axios.create({
  baseURL: API_BASE,
  headers: { 'Content-Type': 'application/json' },
});

// Attach JWT token to every request
client.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle 401 responses
client.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401) {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(err);
  }
);

// ── Auth ──────────────────────────────────────────────────────
export const authAPI = {
  register: (data) => client.post('/auth/register', data),
  login: (data) => client.post('/auth/login', data),
  me: () => client.get('/auth/me'),
};

// ── Models ────────────────────────────────────────────────────
export const modelsAPI = {
  upload: (formData) => client.post('/models/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  }),
  list: () => client.get('/models/'),
  get: (id) => client.get(`/models/${id}`),
  delete: (id) => client.delete(`/models/${id}`),
};

// ── Datasets ──────────────────────────────────────────────────
export const datasetsAPI = {
  upload: (formData) => client.post('/datasets/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  }),
  list: () => client.get('/datasets/'),
  get: (id) => client.get(`/datasets/${id}`),
  delete: (id) => client.delete(`/datasets/${id}`),
};

// ── Audits ────────────────────────────────────────────────────
export const auditsAPI = {
  create: (data) => client.post('/audits/', data),
  run: (id) => client.post(`/audits/${id}/run`),
  status: (id) => client.get(`/audits/${id}/status`),
  results: (id) => client.get(`/audits/${id}/results`),
  list: () => client.get('/audits/'),
  preview: (id) => client.post(`/audits/${id}/preview`),
};

// ── Reports ───────────────────────────────────────────────────
export const reportsAPI = {
  generate: (auditId) => client.post(`/reports/${auditId}/generate`),
  list: () => client.get('/reports/'),
  downloadPdf: (id) => `${API_BASE}/reports/${id}/download/pdf`,
  downloadCsv: (id) => `${API_BASE}/reports/${id}/download/csv`,
};

export default client;
