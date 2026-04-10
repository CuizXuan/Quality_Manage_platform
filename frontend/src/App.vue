<template>
  <div class="app-layout" :class="themeClass">
    <DigitalRain v-if="isDark" />
    <AppHeader :is-dark="isDark" @toggle-theme="toggleTheme" />
    <div class="app-body">
      <Sidebar :is-dark="isDark" @load-request="onLoadRequest" />
      <main class="app-main">
        <router-view />
      </main>
    </div>
    <StatusBar />
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import AppHeader from './components/common/AppHeader.vue'
import Sidebar from './components/common/Sidebar.vue'
import StatusBar from './components/common/StatusBar.vue'
import DigitalRain from './components/common/DigitalRain.vue'

const isDark = ref(true)

onMounted(() => {
  const saved = localStorage.getItem('cyber-theme')
  if (saved !== null) {
    isDark.value = saved === 'dark'
  }
  // Apply theme class to html element
  updateThemeClass()
})

function updateThemeClass() {
  if (isDark.value) {
    document.documentElement.classList.add('theme-dark')
    document.documentElement.classList.remove('theme-light')
  } else {
    document.documentElement.classList.add('theme-light')
    document.documentElement.classList.remove('theme-dark')
  }
}

function toggleTheme() {
  isDark.value = !isDark.value
  localStorage.setItem('cyber-theme', isDark.value ? 'dark' : 'light')
  updateThemeClass()
}

const themeClass = computed(() => {
  return isDark.value ? 'theme-dark' : 'theme-light'
})

function onLoadRequest() {
  // Sidebar 加载请求后，可以在这里做后续处理
}
</script>

<style>
.app-layout {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: var(--bg-primary);
  position: relative;
}

.app-body {
  display: flex;
  flex: 1;
  margin-top: var(--header-height);
  margin-bottom: 28px;
  position: relative;
  z-index: 1;
}

.app-main {
  flex: 1;
  margin-left: var(--sidebar-width);
  overflow-y: auto;
  padding: 16px;
}
</style>
