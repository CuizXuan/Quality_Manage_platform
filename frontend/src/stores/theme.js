import { defineStore } from 'pinia'

export const useThemeStore = defineStore('theme', () => {
  // 跟随系统 prefers-color-scheme，不做手动切换
  const isDark = window.matchMedia('(prefers-color-scheme: dark)').matches

  return { isDark }
})
