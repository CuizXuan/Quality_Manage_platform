<template>
  <footer class="status-bar">
    <span class="status-item">
      📊 当前会话: {{ requestCount }} 次请求
    </span>
    <span class="status-item" :class="backendStatus">
      {{ backendStatus === 'connected' ? '🟢' : '🔴' }}
      后端服务 {{ backendStatus === 'connected' ? '正常' : '异常' }}
    </span>
    <span class="status-tip">💡 双击集合快速加载</span>
  </footer>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import axios from 'axios'

const requestCount = ref(0)
const backendStatus = ref('disconnected')

async function checkBackend() {
  try {
    await axios.get('http://localhost:8000/', { timeout: 3000 })
    backendStatus.value = 'connected'
  } catch (e) {
    backendStatus.value = 'disconnected'
  }
}

let interval
onMounted(() => {
  checkBackend()
  interval = setInterval(checkBackend, 30000)
})

onUnmounted(() => {
  clearInterval(interval)
})

// 监听发送请求事件
window.addEventListener('request-sent', () => {
  requestCount.value++
})
</script>

<style scoped>
.status-bar {
  height: var(--status-bar-height);
  background: var(--bg);
  border-top: 1px solid var(--border);
  display: flex;
  align-items: center;
  padding: 0 16px;
  gap: 24px;
  font-size: 11px;
  color: var(--text);
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
}
.status-item {
  display: flex;
  align-items: center;
  gap: 4px;
}
</style>
