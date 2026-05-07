import { defineStore } from 'pinia'
import { ref } from 'vue'
import { datasetApi } from '../api/dataset'

export const useDatasetStore = defineStore('dataset', () => {
  const datasets = ref([])
  const loading = ref(false)
  const currentDataset = ref(null)
  const previewData = ref({ headers: [], rows: [] })

  async function fetchDatasets(params = {}) {
    loading.value = true
    try {
      const res = await datasetApi.list(params)
      datasets.value = res.data
    } finally {
      loading.value = false
    }
  }

  async function createDataset(data) {
    const res = await datasetApi.create(data)
    datasets.value.push(res.data)
    return res.data
  }

  async function updateDataset(id, data) {
    const res = await datasetApi.update(id, data)
    const idx = datasets.value.findIndex(d => d.id === id)
    if (idx !== -1) datasets.value[idx] = res.data
    return res.data
  }

  async function deleteDataset(id) {
    await datasetApi.delete(id)
    datasets.value = datasets.value.filter(d => d.id !== id)
  }

  async function fetchPreview(id, params = {}) {
    try {
      const res = await datasetApi.getPreview(id, params)
      previewData.value = res.data
    } catch (e) {
      console.error('fetchPreview failed', e)
    }
  }

  function setCurrentDataset(ds) {
    currentDataset.value = ds
  }

  return {
    datasets, loading, currentDataset, previewData,
    fetchDatasets, createDataset, updateDataset, deleteDataset, fetchPreview, setCurrentDataset,
  }
})
