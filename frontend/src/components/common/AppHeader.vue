<template>
  <header class="app-header">
    <div class="header-left">
      <span class="logo">
        <span class="logo-icon">⚡</span>
        <span class="logo-text">CYBER<span class="highlight">API</span></span>
      </span>
      <nav class="main-nav">
        <router-link to="/" class="nav-item" :class="{ active: $route.path === '/' }">
          <span class="nav-icon">⌘</span>
          <span>终端</span>
        </router-link>
        <router-link to="/cases" class="nav-item" :class="{ active: $route.path === '/cases' }">
          <span class="nav-icon">☰</span>
          <span>用例</span>
        </router-link>
        <router-link to="/scenarios" class="nav-item" :class="{ active: $route.path === '/scenarios' }">
          <span class="nav-icon">⚙</span>
          <span>场景</span>
        </router-link>
        <router-link to="/environments" class="nav-item" :class="{ active: $route.path === '/environments' }">
          <span class="nav-icon">◈</span>
          <span>环境</span>
        </router-link>
        <router-link to="/history" class="nav-item" :class="{ active: $route.path === '/history' }">
          <span class="nav-icon">▤</span>
          <span>日志</span>
        </router-link>
      </nav>
    </div>
    <div class="header-right">
      <div class="env-switch">
        <span class="env-label">ENV:</span>
        <select v-model="currentEnv" class="cyber-select">
          <option value="dev">DEV</option>
          <option value="test">TEST</option>
          <option value="prod">PROD</option>
        </select>
        <span class="env-dot" :class="currentEnv"></span>
      </div>
      
      <!-- Theme Toggle -->
      <div class="theme-toggle" @click="emit('toggle-theme')">
        <span class="theme-icon" :class="{ dark: isDark }">
          {{ isDark ? '☾' : '☀' }}
        </span>
        <span class="theme-label">{{ isDark ? 'DARK' : 'LIGHT' }}</span>
      </div>
      
      <router-link to="/settings" class="icon-btn" title="Settings">⚙</router-link>
    </div>
    
    <!-- Scan line effect -->
    <div class="scan-line"></div>
  </header>
</template>

<script setup>
import { ref } from 'vue'

const props = defineProps({
  isDark: {
    type: Boolean,
    default: true
  }
})

const emit = defineEmits(['toggle-theme'])
const currentEnv = ref('dev')
</script>

<style scoped>
.app-header {
  height: var(--header-height);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  background: var(--bg-panel);
  border-bottom: 1px solid var(--border-default);
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 100;
}

.header-left, .header-right {
  display: flex;
  align-items: center;
  gap: 24px;
}

.logo {
  display: flex;
  align-items: center;
  gap: 10px;
}

.logo-icon {
  font-size: 24px;
  filter: drop-shadow(0 0 10px var(--neon-cyan));
  animation: pulse-glow 2s infinite;
}

.logo-text {
  font-family: var(--font-title);
  font-size: 18px;
  font-weight: 800;
  letter-spacing: 3px;
  color: #fff;
  text-shadow: 0 0 10px var(--neon-cyan);
}

.logo-text .highlight {
  color: var(--neon-cyan);
}

.main-nav {
  display: flex;
  gap: 4px;
  margin-left: 32px;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  border: 1px solid transparent;
  border-radius: 4px;
  font-family: var(--font-title);
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 2px;
  text-transform: uppercase;
  color: var(--text-secondary);
  text-decoration: none;
  position: relative;
  overflow: hidden;
  transition: all var(--transition-fast);
}

.nav-item::before {
  content: '';
  position: absolute;
  left: 0;
  top: 50%;
  width: 0;
  height: 2px;
  background: var(--neon-cyan);
  box-shadow: 0 0 10px var(--neon-cyan);
  transform: translateY(-50%);
  transition: width var(--transition-fast);
}

.nav-item:hover {
  color: var(--neon-cyan);
  background: rgba(0, 255, 255, 0.05);
  border-color: rgba(0, 255, 255, 0.3);
}

.nav-item.active {
  color: var(--neon-cyan);
  background: rgba(0, 255, 255, 0.1);
  border-color: var(--neon-cyan);
  box-shadow: 0 0 15px rgba(0, 255, 255, 0.3), inset 0 0 15px rgba(0, 255, 255, 0.1);
}

.nav-item.active::before {
  width: 100%;
}

.nav-icon {
  font-size: 14px;
}

.env-switch {
  display: flex;
  align-items: center;
  gap: 8px;
}

.env-label {
  font-family: var(--font-title);
  font-size: 10px;
  color: var(--text-secondary);
  letter-spacing: 2px;
}

.cyber-select {
  font-family: var(--font-title);
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 1px;
  padding: 4px 8px;
  background: var(--bg-secondary);
  border: 1px solid var(--neon-cyan);
  color: var(--neon-cyan);
  cursor: pointer;
  outline: none;
}

.cyber-select:focus {
  box-shadow: 0 0 10px rgba(0, 255, 255, 0.5);
}

.env-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  animation: pulse-glow 1.5s infinite;
}

.env-dot.dev { 
  background: var(--neon-green); 
  box-shadow: 0 0 10px var(--neon-green);
}
.env-dot.test { 
  background: var(--neon-yellow); 
  box-shadow: 0 0 10px var(--neon-yellow);
}
.env-dot.prod { 
  background: #f00; 
  box-shadow: 0 0 10px #f00;
}

.icon-btn {
  color: var(--text-secondary);
  font-size: 18px;
  text-decoration: none;
  padding: 6px 10px;
  border: 1px solid transparent;
  border-radius: 4px;
  transition: all var(--transition-fast);
}

.icon-btn:hover {
  color: var(--neon-cyan);
  border-color: var(--neon-cyan);
  box-shadow: 0 0 10px rgba(0, 255, 255, 0.5);
}

/* Scan line effect */
.scan-line {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, var(--neon-cyan), transparent);
  animation: scan-line 4s linear infinite;
  opacity: 0.3;
}

@keyframes scan-line {
  0% { top: -1px; opacity: 0; }
  10% { opacity: 0.3; }
  90% { opacity: 0.3; }
  100% { top: 100%; opacity: 0; }
}

@keyframes pulse-glow {
  0%, 100% { 
    filter: drop-shadow(0 0 5px currentColor);
  }
  50% { 
    filter: drop-shadow(0 0 15px currentColor) drop-shadow(0 0 25px currentColor);
  }
}

/* Theme Toggle */
.theme-toggle {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  background: rgba(0, 255, 255, 0.1);
  border: 1px solid var(--neon-cyan);
  border-radius: 4px;
  cursor: pointer;
  transition: all var(--transition-fast);
  user-select: none;
}

.theme-toggle:hover {
  background: rgba(0, 255, 255, 0.2);
  box-shadow: 0 0 15px rgba(0, 255, 255, 0.4);
  transform: scale(1.05);
}

.theme-icon {
  font-size: 16px;
  transition: all 0.3s ease;
}

.theme-icon.dark {
  filter: drop-shadow(0 0 5px var(--neon-cyan));
}

.theme-icon:not(.dark) {
  filter: drop-shadow(0 0 5px var(--neon-yellow));
}

.theme-label {
  font-family: var(--font-title);
  font-size: 10px;
  font-weight: 600;
  letter-spacing: 1px;
  color: var(--neon-cyan);
}

/* Theme-aware styles using CSS variables */
</style>
