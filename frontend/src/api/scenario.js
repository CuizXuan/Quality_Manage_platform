import axios from 'axios'

const client = axios.create({
  baseURL: 'http://localhost:8000',
  timeout: 60000,
})

export const scenariosApi = {
  list: () => client.get('/api/scenarios'),
  get: (id) => client.get(`/api/scenarios/${id}`),
  create: (data) => client.post('/api/scenarios', data),
  update: (id, data) => client.put(`/api/scenarios/${id}`, data),
  delete: (id) => client.delete(`/api/scenarios/${id}`),
  run: (id, data) => client.post(`/api/scenarios/${id}/run`, data),
  addStep: (scenarioId, data) => client.post(`/api/scenarios/${scenarioId}/steps`, data),
  updateStep: (scenarioId, stepId, data) => client.put(`/api/scenarios/${scenarioId}/steps/${stepId}`, data),
  deleteStep: (scenarioId, stepId) => client.delete(`/api/scenarios/${scenarioId}/steps/${stepId}`),
  reorderSteps: (scenarioId, stepIds) => client.put(`/api/scenarios/${scenarioId}/steps/reorder`, stepIds),
}
