import axios from 'axios'

const client = axios.create({
  baseURL: 'http://localhost:8000',
  timeout: 60000,
})

export const environmentsApi = {
  list: () => client.get('/api/environments'),
  get: (id) => client.get(`/api/environments/${id}`),
  create: (data) => client.post('/api/environments', data),
  update: (id, data) => client.put(`/api/environments/${id}`, data),
  delete: (id) => client.delete(`/api/environments/${id}`),
  setDefault: (id) => client.post(`/api/environments/${id}/set-default`),
}
