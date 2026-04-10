<template>
  <div class="request-bar">
    <!-- Method 选择器 -->
    <div class="method-select-wrapper">
      <select v-model="method" class="method-select" :class="'method-' + method.toLowerCase()">
        <option v-for="m in methods" :key="m" :value="m">{{ m }}</option>
      </select>
    </div>

    <!-- URL 输入框 -->
    <div class="url-input-wrapper">
      <input
        v-model="url"
        class="url-input"
        placeholder="ENTER_TARGET_URL..."
        @keydown.meta.enter="send"
        @keydown.ctrl.enter="send"
        ref="urlInputRef"
      />
      <span class="url-prefix" v-if="url">&gt;</span>
    </div>

    <!-- 发送按钮 -->
    <button
      class="send-btn"
      @click="send"
      :disabled="loading || !url.trim()"
      :class="{ loading: loading }"
    >
      <span v-if="loading" class="loading-icon">⟳</span>
      <span v-else class="send-icon">▶</span>
      {{ loading ? 'SENDING...' : 'SEND' }}
    </button>

    <!-- 保存按钮 -->
    <button class="save-btn" @click="showSaveDialog = true" title="保存到集合">
      💾
    </button>

    <!-- 保存弹窗 -->
    <div v-if="showSaveDialog" class="save-dialog-overlay" @click.self="showSaveDialog = false">
      <div class="modal">
        <div class="modal-title">// SAVE TO COLLECTION</div>
        <div class="dialog-body">
          <div class="form-group">
            <label>INTERFACE_NAME</label>
            <input v-model="saveName" placeholder="如：获取用户列表" />
          </div>
          <div class="form-group">
            <label>SELECT_COLLECTION</label>
            <select v-model="selectedCollection">
              <option value="">-- NEW COLLECTION --</option>
              <option v-for="col in collections" :key="col.id" :value="col.id">
                {{ col.name }}
              </option>
            </select>
          </div>
          <div v-if="!selectedCollection" class="form-group">
            <label>NEW_COLLECTION_NAME</label>
            <input v-model="newCollectionName" placeholder="如：用户模块" />
          </div>
        </div>
        <div class="dialog-actions">
          <button class="btn" @click="showSaveDialog = false">CANCEL</button>
          <button class="btn primary" @click="saveToCollection">SAVE</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { storeToRefs } from 'pinia'
import { useRequestStore } from '../../stores/request'
import { useCollectionStore } from '../../stores/collection'
import { useHistoryStore } from '../../stores/history'
import { proxyApi } from '../../api/client'

const emit = defineEmits(['response-received'])

const requestStore = useRequestStore()
const collectionStore = useCollectionStore()
const historyStore = useHistoryStore()

// 使用 storeToRefs 保持响应式
const { method, url, headers, params, body } = storeToRefs(requestStore)

const methods = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD', 'OPTIONS']
const loading = ref(false)
const showSaveDialog = ref(false)
const saveName = ref('')
const selectedCollection = ref('')
const newCollectionName = ref('')
const collections = collectionStore.collections

async function send() {
  if (!url.value?.trim() || loading.value) return

  loading.value = true
  requestStore.loading = true
  requestStore.error = null

  // 触发状态栏计数
  window.dispatchEvent(new CustomEvent('request-sent'))

  // 构建 headers 对象
  const headersObj = {}
  requestStore.headers.forEach(h => {
    if (h.key.trim() && h.enabled !== false) {
      headersObj[h.key] = h.value
    }
  })

  // 构建 params 对象
  const paramsObj = {}
  requestStore.params.forEach(p => {
    if (p.key.trim() && p.enabled !== false) {
      paramsObj[p.key] = p.value
    }
  })

  // 完整 URL
  let fullUrl = url.value.trim()
  try {
    const urlObj = new URL(fullUrl.startsWith('http') ? fullUrl : 'http://' + fullUrl)
    Object.entries(paramsObj).forEach(([k, v]) => urlObj.searchParams.set(k, v))
    fullUrl = urlObj.toString()
  } catch (e) {
    // URL 解析失败
  }

  requestStore.fullUrl = fullUrl

  try {
    const response = await proxyApi.send({
      method: requestStore.method,
      url: fullUrl,
      headers: headersObj,
      params: {},
      body: ['POST', 'PUT', 'PATCH'].includes(requestStore.method) ? requestStore.body : undefined,
      timeout: 30,
    })
    requestStore.response = response.data
    emit('response-received', response.data)

    historyStore.addItem({
      method: method.value,
      url: url.value,
      fullUrl: fullUrl,
      headers: headersObj,
      params: paramsObj,
      body: requestStore.body,
      statusCode: response.data.status_code,
      duration: response.data.duration_ms,
    })
  } catch (e) {
    const errorDetail = e.response?.data?.detail || e.message
    requestStore.error = errorDetail
    historyStore.addItem({
      method: method.value,
      url: url.value,
      fullUrl: fullUrl,
      headers: headersObj,
      params: paramsObj,
      body: requestStore.body,
      statusCode: e.response?.status || 0,
      duration: 0,
      error: true,
    })
  } finally {
    loading.value = false
    requestStore.loading = false
  }
}

function saveToCollection() {
  let colId = selectedCollection.value
  if (!colId && newCollectionName.value.trim()) {
    const newCol = collectionStore.createCollection(newCollectionName.value.trim())
    colId = newCol.id
  }
  if (colId) {
    collectionStore.addRequest(colId, {
      name: saveName.value || url.value,
      method: method.value,
      url: url.value,
      fullUrl: url.value,
      headers: Object.fromEntries(
        requestStore.headers.filter(h => h.key.trim()).map(h => [h.key, h.value])
      ),
      params: Object.fromEntries(
        requestStore.params.filter(p => p.key.trim()).map(p => [p.key, p.value])
      ),
      body: requestStore.body,
    })
    showSaveDialog.value = false
    saveName.value = ''
    newCollectionName.value = ''
    selectedCollection.value = ''
  }
}
</script>

<style scoped>
.request-bar {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 16px;
}

.method-select-wrapper {
  flex-shrink: 0;
}

.method-select {
  width: 110px;
  padding: 10px 12px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-default);
  font-family: var(--font-title);
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 1px;
  cursor: pointer;
  outline: none;
  transition: all var(--transition-fast);
}

.method-select:focus {
  border-color: var(--neon-cyan);
  box-shadow: 0 0 10px rgba(0, 255, 255, 0.3);
}

.method-select.method-get { color: var(--neon-cyan); border-color: var(--neon-cyan); }
.method-select.method-post { color: var(--neon-green); border-color: var(--neon-green); }
.method-select.method-put { color: var(--neon-orange); border-color: var(--neon-orange); }
.method-select.method-delete { color: #f00; border-color: #f00; }
.method-select.method-patch { color: var(--neon-pink); border-color: var(--neon-pink); }

.url-input-wrapper {
  flex: 1;
  position: relative;
}

.url-input {
  width: 100%;
  padding: 10px 14px;
  padding-left: 30px;
  font-family: var(--font-mono);
  font-size: 13px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-default);
  color: var(--neon-cyan);
  outline: none;
  transition: all var(--transition-fast);
}

.url-input:focus {
  border-color: var(--neon-cyan);
  box-shadow: 0 0 15px rgba(0, 255, 255, 0.3), inset 0 0 15px rgba(0, 255, 255, 0.05);
}

.url-input::placeholder {
  color: rgba(0, 255, 255, 0.3);
  letter-spacing: 1px;
}

.url-prefix {
  position: absolute;
  left: 12px;
  top: 50%;
  transform: translateY(-50%);
  color: var(--neon-magenta);
  font-weight: bold;
  animation: blink 1s infinite;
}

.send-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 24px;
  background: var(--neon-cyan);
  border: 1px solid var(--neon-cyan);
  color: var(--bg-primary);
  font-family: var(--font-title);
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 2px;
  cursor: pointer;
  position: relative;
  overflow: hidden;
  transition: all var(--transition-fast);
  clip-path: polygon(0 0, calc(100% - 8px) 0, 100% 8px, 100% 100%, 8px 100%, 0 calc(100% - 8px));
}

.send-btn::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.4), transparent);
  transition: left 0.5s;
}

.send-btn:hover:not(:disabled)::before {
  left: 100%;
}

.send-btn:hover:not(:disabled) {
  background: transparent;
  color: var(--neon-cyan);
  box-shadow: 0 0 20px rgba(0, 255, 255, 0.5), inset 0 0 20px rgba(0, 255, 255, 0.1);
}

.send-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.send-btn.loading {
  background: var(--neon-magenta);
  border-color: var(--neon-magenta);
}

.loading-icon {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.send-icon {
  text-shadow: 0 0 5px currentColor;
}

.save-btn {
  width: 44px;
  height: 44px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  border: 1px solid var(--border-default);
  color: var(--text-secondary);
  font-size: 16px;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.save-btn:hover {
  border-color: var(--neon-cyan);
  color: var(--neon-cyan);
  box-shadow: 0 0 15px rgba(0, 255, 255, 0.3);
}

.save-dialog-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.85);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 200;
}

.modal {
  background: var(--bg-panel);
  border: 1px solid var(--neon-cyan);
  box-shadow: 0 0 30px rgba(0, 255, 255, 0.3), inset 0 0 60px rgba(0, 255, 255, 0.05);
  padding: 24px;
  width: 420px;
  clip-path: polygon(0 0, calc(100% - 16px) 0, 100% 16px, 100% 100%, 16px 100%, 0 calc(100% - 16px));
}

.modal-title {
  font-family: var(--font-title);
  font-size: 14px;
  font-weight: 600;
  color: var(--neon-cyan);
  letter-spacing: 2px;
  margin-bottom: 20px;
  padding-bottom: 10px;
  border-bottom: 1px solid var(--border-default);
}

.dialog-body {
  margin-bottom: 20px;
}

.form-group {
  margin-bottom: 16px;
}

.form-group label {
  display: block;
  font-family: var(--font-title);
  font-size: 10px;
  color: var(--text-secondary);
  letter-spacing: 1px;
  margin-bottom: 6px;
}

.form-group input,
.form-group select {
  width: 100%;
  padding: 10px 12px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-default);
  color: var(--neon-cyan);
  font-family: var(--font-mono);
  font-size: 12px;
  outline: none;
}

.form-group input:focus,
.form-group select:focus {
  border-color: var(--neon-cyan);
  box-shadow: 0 0 10px rgba(0, 255, 255, 0.3);
}

.dialog-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

.btn {
  font-family: var(--font-title);
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 1px;
  padding: 8px 16px;
  background: transparent;
  border: 1px solid var(--border-default);
  color: var(--text-secondary);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.btn:hover {
  border-color: var(--neon-cyan);
  color: var(--neon-cyan);
}

.btn.primary {
  background: var(--neon-cyan);
  border-color: var(--neon-cyan);
  color: var(--bg-primary);
}

.btn.primary:hover {
  background: transparent;
  color: var(--neon-cyan);
}
</style>
