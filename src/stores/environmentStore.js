import { defineStore } from 'pinia'
import { ref } from 'vue'
import { environmentsApi } from '../api/environment'

export const useEnvironmentStore = defineStore('environment', () => {
  const environments = ref([])
  const loading = ref(false)

  async function fetchEnvironments() {
    loading.value = true
    try {
      const res = await environmentsApi.list()
      environments.value = res.data
    } finally {
      loading.value = false
    }
  }

  async function createEnvironment(data) {
    const res = await environmentsApi.create(data)
    environments.value.push(res.data)
    return res.data
  }

  async function updateEnvironment(id, data) {
    const res = await environmentsApi.update(id, data)
    const idx = environments.value.findIndex(e => e.id === id)
    if (idx !== -1) environments.value[idx] = res.data
    return res.data
  }

  async function deleteEnvironment(id) {
    await environmentsApi.delete(id)
    environments.value = environments.value.filter(e => e.id !== id)
  }

  async function setDefault(id) {
    await environmentsApi.setDefault(id)
    environments.value.forEach(e => {
      e.is_default = e.id === id
    })
  }

  function getDefault() {
    return environments.value.find(e => e.is_default)
  }

  return {
    environments, loading,
    fetchEnvironments, createEnvironment, updateEnvironment, deleteEnvironment, setDefault, getDefault,
  }
})
