import { defineStore } from 'pinia'
import { ref } from 'vue'
import { scheduleApi } from '../api/schedule'

export const useScheduleStore = defineStore('schedule', () => {
  const schedules = ref([])
  const loading = ref(false)

  async function fetchSchedules(params = {}) {
    loading.value = true
    try {
      const res = await scheduleApi.list(params)
      schedules.value = res.data
    } finally {
      loading.value = false
    }
  }

  async function createSchedule(data) {
    const res = await scheduleApi.create(data)
    schedules.value.push(res.data)
    return res.data
  }

  async function updateSchedule(id, data) {
    const res = await scheduleApi.update(id, data)
    const idx = schedules.value.findIndex(s => s.id === id)
    if (idx !== -1) schedules.value[idx] = res.data
    return res.data
  }

  async function deleteSchedule(id) {
    await scheduleApi.delete(id)
    schedules.value = schedules.value.filter(s => s.id !== id)
  }

  async function toggleSchedule(id, enabled) {
    const res = await scheduleApi.toggle(id, enabled)
    const idx = schedules.value.findIndex(s => s.id === id)
    if (idx !== -1) schedules.value[idx] = res.data
    return res.data
  }

  async function runSchedule(id) {
    const res = await scheduleApi.run(id)
    return res.data
  }

  return {
    schedules, loading,
    fetchSchedules, createSchedule, updateSchedule, deleteSchedule, toggleSchedule, runSchedule,
  }
})
