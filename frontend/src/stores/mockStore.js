import { defineStore } from 'pinia'
import { ref } from 'vue'
import { mockApi } from '../api/mock'

export const useMockStore = defineStore('mock', () => {
  const rules = ref([])
  const loading = ref(false)

  async function fetchRules(params = {}) {
    loading.value = true
    try {
      const res = await mockApi.list(params)
      rules.value = res.data.data || []
    } finally {
      loading.value = false
    }
  }

  async function createRule(data) {
    const res = await mockApi.create(data)
    rules.value.push(res.data.data)
    return res.data.data
  }

  async function updateRule(id, data) {
    const res = await mockApi.update(id, data)
    const idx = rules.value.findIndex(r => r.id === id)
    if (idx !== -1) rules.value[idx] = res.data.data
    return res.data.data
  }

  async function deleteRule(id) {
    await mockApi.delete(id)
    rules.value = rules.value.filter(r => r.id !== id)
  }

  async function toggleRule(id, enabled) {
    const res = await mockApi.toggle(id, enabled)
    const idx = rules.value.findIndex(r => r.id === id)
    if (idx !== -1) rules.value[idx] = res.data.data
    return res.data.data
  }

  return {
    rules, loading,
    fetchRules, createRule, updateRule, deleteRule, toggleRule,
  }
})
