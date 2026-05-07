<template>
  <footer class="status-bar">
    <div class="status-left">
      <span class="status-item">
        <span class="status-dot online"></span>
        <span>SYSTEM ONLINE</span>
      </span>
      <span class="status-item">
        <span class="separator">|</span>
        <span>v1.0.0</span>
      </span>
    </div>
    <div class="status-right">
      <span class="status-item">
        <span class="label">ENV:</span>
        <span class="value">{{ envName }}</span>
      </span>
      <span class="status-item">
        <span class="separator">|</span>
        <span>{{ currentTime }}</span>
      </span>
    </div>
  </footer>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'

const envName = ref('DEV')
const currentTime = ref('')
let timeInterval = null

function updateTime() {
  const now = new Date()
  currentTime.value = now.toLocaleTimeString('en-US', { hour12: false }) + ' UTC'
}

onMounted(() => {
  updateTime()
  timeInterval = setInterval(updateTime, 1000)
})

onUnmounted(() => {
  if (timeInterval) clearInterval(timeInterval)
})
</script>

<style scoped>
.status-bar {
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 16px;
  background: var(--bg-secondary);
  border-top: 1px solid var(--neon-cyan);
  box-shadow: 0 -1px 0 rgba(0, 255, 255, 0.2);
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  z-index: 100;
  font-family: var(--font-mono);
  font-size: 10px;
  letter-spacing: 1px;
  color: var(--text-secondary);
}

.status-left, .status-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.status-item {
  display: flex;
  align-items: center;
  gap: 6px;
}

.status-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  animation: pulse-glow 2s infinite;
}

.status-dot.online {
  background: var(--neon-green);
  box-shadow: 0 0 5px var(--neon-green);
}

.status-dot.offline {
  background: #f00;
  box-shadow: 0 0 5px #f00;
}

.separator {
  color: var(--border-default);
}

.label {
  color: var(--text-secondary);
}

.value {
  color: var(--neon-cyan);
  font-weight: 600;
}

@keyframes pulse-glow {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}
</style>
