import { defineStore } from 'pinia'
import { ref } from 'vue'
import { casesApi } from '../api/case'
import { foldersApi } from '../api/folder'

export const useCaseStore = defineStore('case', () => {
  const cases = ref([])
  const folders = ref([])
  const loading = ref(false)
  const currentCase = ref(null)

  async function fetchCases(params = {}) {
    loading.value = true
    try {
      const res = await casesApi.list(params)
      cases.value = res.data
    } finally {
      loading.value = false
    }
  }

  async function fetchFolders() {
    try {
      const res = await foldersApi.getTree()
      folders.value = res.data
    } catch (e) {
      console.error('fetchFolders failed', e)
    }
  }

  async function createCase(data) {
    const res = await casesApi.create(data)
    cases.value.push(res.data)
    return res.data
  }

  async function updateCase(id, data) {
    const res = await casesApi.update(id, data)
    const idx = cases.value.findIndex(c => c.id === id)
    if (idx !== -1) cases.value[idx] = res.data
    return res.data
  }

  async function deleteCase(id) {
    await casesApi.delete(id)
    cases.value = cases.value.filter(c => c.id !== id)
  }

  async function duplicateCase(id) {
    const res = await casesApi.duplicate(id)
    cases.value.push(res.data)
    return res.data
  }

  async function runCase(id, data = {}) {
    const res = await casesApi.run(id, data)
    return res.data
  }

  function setCurrentCase(caseData) {
    currentCase.value = caseData
  }

  return {
    cases, folders, loading, currentCase,
    fetchCases, fetchFolders, createCase, updateCase, deleteCase, duplicateCase, runCase, setCurrentCase,
  }
})
