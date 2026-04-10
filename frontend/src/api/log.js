import axios from 'axios'

const client = axios.create({
  baseURL: 'http://localhost:8000',
  timeout: 60000,
})

export const logsApi = {
  list: (params = {}) => client.get('/api/logs', { params }),
  get: (id) => client.get(`/api/logs/${id}`),
  delete: (id) => client.delete(`/api/logs/${id}`),
  batchDelete: (ids) => client.post('/api/logs/batch-delete', ids),
}
