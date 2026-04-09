import { defineStore } from 'pinia'
import { ref, watch } from 'vue'

export const useThemeStore = defineStore('theme', () => {
  const isDark = ref(true)

  function toggle() {
    isDark.value = !isDark.value
    applyTheme()
    localStorage.setItem('theme', isDark.value ? 'dark' : 'light')
  }

  function applyTheme() {
    if (isDark.value) {
      document.documentElement.removeAttribute('data-theme')
    } else {
      document.documentElement.setAttribute('data-theme', 'light')
    }
  }

  function init() {
    const saved = localStorage.getItem('theme')
    if (saved === 'light') {
      isDark.value = false
    }
    applyTheme()
  }

  // 初始化
  init()

  return { isDark, toggle, applyTheme }
})
