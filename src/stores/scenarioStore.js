import { defineStore } from 'pinia'
import { ref } from 'vue'
import { scenariosApi } from '../api/scenario'

export const useScenarioStore = defineStore('scenario', () => {
  const scenarios = ref([])
  const loading = ref(false)

  async function fetchScenarios() {
    loading.value = true
    try {
      const res = await scenariosApi.list()
      scenarios.value = res.data
    } finally {
      loading.value = false
    }
  }

  async function createScenario(data) {
    const res = await scenariosApi.create(data)
    scenarios.value.push(res.data)
    return res.data
  }

  async function updateScenario(id, data) {
    const res = await scenariosApi.update(id, data)
    const idx = scenarios.value.findIndex(s => s.id === id)
    if (idx !== -1) scenarios.value[idx] = res.data
    return res.data
  }

  async function deleteScenario(id) {
    await scenariosApi.delete(id)
    scenarios.value = scenarios.value.filter(s => s.id !== id)
  }

  async function addStep(scenarioId, data) {
    const res = await scenariosApi.addStep(scenarioId, data)
    return res.data
  }

  async function updateStep(scenarioId, stepId, data) {
    const res = await scenariosApi.updateStep(scenarioId, stepId, data)
    return res.data
  }

  async function deleteStep(scenarioId, stepId) {
    await scenariosApi.deleteStep(scenarioId, stepId)
  }

  async function runScenario(id, data = {}) {
    const res = await scenariosApi.run(id, data)
    return res.data
  }

  return {
    scenarios, loading,
    fetchScenarios, createScenario, updateScenario, deleteScenario,
    addStep, updateStep, deleteStep, runScenario,
  }
})
