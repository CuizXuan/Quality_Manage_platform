import axios from 'axios'

const client = axios.create({
  baseURL: 'http://localhost:8000',
  timeout: 60000,
})

export const casesApi = {
  list: (params = {}) => client.get('/api/cases', { params }),
  get: (id) => client.get(`/api/cases/${id}`),
  create: (data) => client.post('/api/cases', data),
  update: (id, data) => client.put(`/api/cases/${id}`, data),
  delete: (id) => client.delete(`/api/cases/${id}`),
  duplicate: (id) => client.post(`/api/cases/${id}/duplicate`),
  batchDelete: (ids) => client.post('/api/cases/batch-delete', ids),
  run: (id, data) => client.post(`/api/cases/${id}/run`, data),
}
