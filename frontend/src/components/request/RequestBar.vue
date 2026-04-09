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
        placeholder="输入请求 URL，如 https://api.example.com/users"
        @keydown.meta.enter="send"
        @keydown.ctrl.enter="send"
        ref="urlInputRef"
      />
    </div>

    <!-- 发送按钮 -->
    <button
      class="send-btn btn-primary"
      @click="send"
      :disabled="loading || !url.trim()"
    >
      <span v-if="loading" class="loading-icon">⟳</span>
      <span v-else>🚀</span>
      {{ loading ? '发送中...' : '发送' }}
    </button>

    <!-- 保存按钮 -->
    <button class="save-btn btn-secondary" @click="showSaveDialog = true" title="保存到集合">
      💾
    </button>

    <!-- 保存弹窗 -->
    <div v-if="showSaveDialog" class="save-dialog-overlay" @click.self="showSaveDialog = false">
      <div class="save-dialog panel">
        <div class="dialog-title">保存到集合</div>
        <div class="dialog-body">
          <div class="form-group">
            <label>接口名称</label>
            <input v-model="saveName" placeholder="如：获取用户列表" />
          </div>
          <div class="form-group">
            <label>选择集合</label>
            <select v-model="selectedCollection">
              <option value="">-- 新建集合 --</option>
              <option v-for="col in collections" :key="col.id" :value="col.id">
                {{ col.name }}
              </option>
            </select>
          </div>
          <div v-if="!selectedCollection" class="form-group">
            <label>新集合名称</label>
            <input v-model="newCollectionName" placeholder="如：用户模块" />
          </div>
        </div>
        <div class="dialog-actions">
          <button class="btn-secondary" @click="showSaveDialog = false">取消</button>
          <button class="btn-primary" @click="saveToCollection">保存</button>
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

  // 构建 headers 对象（直接从 store 的 ref 取值）
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

  // 完整 URL（含 query 参数）
  let fullUrl = url.value.trim()
  try {
    const urlObj = new URL(fullUrl.startsWith('http') ? fullUrl : 'http://' + fullUrl)
    Object.entries(paramsObj).forEach(([k, v]) => urlObj.searchParams.set(k, v))
    fullUrl = urlObj.toString()
  } catch (e) {
    // URL 解析失败，直接使用原 URL
  }

  // 保存完整 URL 到 store
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

    // 添加到历史
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
      fullUrl: fullUrl,
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
  margin-bottom: 12px;
}
.method-select-wrapper {
  flex-shrink: 0;
}
.method-select {
  width: 100px;
  padding: 8px 12px;
  background: var(--bg-tertiary);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  outline: none;
}
.method-select.method-get { color: var(--method-get); }
.method-select.method-post { color: var(--method-post); }
.method-select.method-put { color: var(--method-put); }
.method-select.method-delete { color: var(--method-delete); }
.method-select.method-patch { color: var(--method-patch); }
.url-input-wrapper {
  flex: 1;
}
.url-input {
  width: 100%;
  padding: 8px 12px;
  font-size: 13px;
}
.send-btn {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 20px;
  font-size: 13px;
}
.loading-icon {
  animation: spin 1s linear infinite;
}
@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
.save-btn {
  flex-shrink: 0;
  padding: 8px 12px;
  font-size: 14px;
}
.save-dialog-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 200;
}
.save-dialog {
  width: 400px;
  padding: 20px;
}
.dialog-title {
  font-size: 15px;
  font-weight: 600;
  margin-bottom: 16px;
}
.dialog-body {
  margin-bottom: 16px;
}
.form-group {
  margin-bottom: 12px;
}
.form-group label {
  display: block;
  font-size: 12px;
  color: var(--text-secondary);
  margin-bottom: 4px;
}
.form-group input,
.form-group select {
  width: 100%;
  padding: 8px 10px;
}
.dialog-actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}
</style>
