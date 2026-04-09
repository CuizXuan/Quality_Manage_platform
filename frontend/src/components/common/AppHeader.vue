<template>
  <header class="app-header glass">
    <div class="header-left">
      <span class="logo">
        <span class="logo-icon">⚡</span>
        <span class="logo-text">APIDebug</span>
      </span>
    </div>
    <div class="header-center">
      <span class="workspace-name">默认工作区</span>
    </div>
    <div class="header-right">
      <div class="env-switch">
        <span class="env-dot" :class="currentEnv"></span>
        <select v-model="currentEnv">
          <option value="dev">开发环境</option>
          <option value="test">测试环境</option>
          <option value="prod">生产环境</option>
        </select>
      </div>
      <button class="icon-btn theme-toggle" @click="themeStore.toggle" :title="themeStore.isDark ? '切换浅色主题' : '切换深色主题'">
        {{ themeStore.isDark ? '☀️' : '🌙' }}
      </button>
      <router-link to="/settings" class="icon-btn" title="设置">⚙</router-link>
      <router-link to="/shortcuts" class="icon-btn" title="快捷键">⌨</router-link>
    </div>
  </header>
</template>

<script setup>
import { ref } from 'vue'
import { useThemeStore } from '../../stores/theme'
const currentEnv = ref('dev')
const themeStore = useThemeStore()
</script>

<style scoped>
.app-header {
  height: var(--header-height);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 16px;
  border-bottom: 1px solid rgba(59, 130, 246, 0.1);
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 100;
}
.header-left, .header-right {
  display: flex;
  align-items: center;
  gap: 12px;
}
.logo {
  display: flex;
  align-items: center;
  gap: 8px;
}
.logo-icon {
  font-size: 20px;
}
.logo-text {
  font-size: 15px;
  font-weight: 600;
  background: var(--gradient-primary);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}
.workspace-name {
  color: var(--text-secondary);
  font-size: 13px;
}
.env-switch {
  display: flex;
  align-items: center;
  gap: 6px;
}
.env-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}
.env-dot.dev { background: var(--success); }
.env-dot.test { background: var(--warning); }
.env-dot.prod { background: var(--danger); }
.env-switch select {
  background: var(--bg-tertiary);
  border: 1px solid var(--border-color);
  color: var(--text-primary);
  border-radius: var(--radius-md);
  padding: 4px 8px;
  font-size: 12px;
  cursor: pointer;
}
.icon-btn {
  color: var(--text-secondary);
  font-size: 16px;
  text-decoration: none;
  padding: 4px 8px;
  border-radius: var(--radius-md);
  transition: all var(--transition-fast);
}
.icon-btn:hover {
  color: var(--text-primary);
  background: var(--bg-tertiary);
}
.theme-toggle {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 16px;
  padding: 4px 8px;
  border-radius: var(--radius-md);
  transition: all var(--transition-fast);
}
.theme-toggle:hover {
  background: var(--bg-tertiary);
}
</style>
