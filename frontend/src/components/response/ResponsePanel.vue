<template>
  <div class="response-panel panel">
    <div class="panel-header">
      <span class="panel-title">📊 响应</span>
      <div v-if="response" class="response-actions">
        <button class="action-btn" @click="copyResponse" title="复制">📋 复制</button>
        <button class="action-btn" @click="downloadResponse" title="下载">⬇ 下载</button>
      </div>
    </div>

    <!-- Loading 状态 -->
    <div v-if="loading" class="response-loading">
      <div class="loading-spinner">⟳</div>
      <span>等待响应...</span>
    </div>

    <!-- Error 状态 -->
    <div v-else-if="error" class="response-error">
      <div class="error-title">❌ 请求失败</div>
      <div class="error-detail">{{ error }}</div>
    </div>

    <!-- 响应内容 -->
    <div v-else-if="response" class="response-content">
      <!-- 概览栏 -->
      <div class="response-overview">
        <span class="status-badge" :class="getStatusClass(response.status_code)">
          {{ response.status_code }} {{ response.status_text }}
        </span>
        <span class="overview-item">⏱ {{ response.duration_ms }}ms</span>
        <span class="overview-item">📦 {{ formatSize(response.content_size) }}</span>
      </div>

      <!-- Tab 切换 -->
      <div class="response-tabs">
        <button
          v-for="tab in tabs"
          :key="tab.key"
          :class="{ active: activeTab === tab.key }"
          @click="activeTab = tab.key"
        >
          {{ tab.label }}
        </button>
      </div>

      <!-- 响应体 Tab -->
      <div v-show="activeTab === 'body'" class="tab-content">
        <div class="section-header" @click="bodyExpanded = !bodyExpanded">
          <span>响应体</span>
          <span>{{ bodyExpanded ? '▲' : '▼' }}</span>
        </div>
        <div v-show="bodyExpanded" class="response-body">
          <div class="body-toolbar">
            <button @click="toggleFormat" :class="{ active: formatted }">
              {{ formatted ? '原始' : '格式化' }}
            </button>
          </div>
          <pre class="body-content" :class="{ 'body-formatted': formatted }">{{ displayContent }}</pre>
        </div>

        <div class="section-header" @click="headersExpanded = !headersExpanded">
          <span>响应头 ({{ responseHeadersCount }})</span>
          <span>{{ headersExpanded ? '▲' : '▼' }}</span>
        </div>
        <div v-show="headersExpanded" class="response-headers">
          <div v-for="(value, key) in response.headers" :key="key" class="header-row">
            <span class="header-key">{{ key }}</span>
            <span class="header-value">{{ value }}</span>
          </div>
        </div>
      </div>

      <!-- 请求参数 Tab -->
      <div v-show="activeTab === 'request'" class="tab-content">
        <!-- 请求 URL -->
        <div class="section-header" @click="reqUrlExpanded = !reqUrlExpanded">
          <span>请求地址</span>
          <span>{{ reqUrlExpanded ? '▲' : '▼' }}</span>
        </div>
        <div v-show="reqUrlExpanded" class="request-url">
          <div class="url-row">
            <span class="method-badge" :class="'method-' + method.toLowerCase()">{{ method }}</span>
            <span class="url-text">{{ fullUrl || requestStore.url }}</span>
          </div>
        </div>

        <!-- 请求头 -->
        <div class="section-header" @click="reqHeadersExpanded = !reqHeadersExpanded">
          <span>请求头 ({{ requestHeadersCount }})</span>
          <span>{{ reqHeadersExpanded ? '▲' : '▼' }}</span>
        </div>
        <div v-show="reqHeadersExpanded" class="request-headers">
          <div v-for="(item, index) in enabledHeaders" :key="index" class="header-row">
            <span class="header-key">{{ item.key }}</span>
            <span class="header-value">{{ item.value }}</span>
          </div>
          <div v-if="enabledHeaders.length === 0" class="empty-hint">无</div>
        </div>

        <!-- Query 参数 -->
        <div class="section-header" @click="reqParamsExpanded = !reqParamsExpanded">
          <span>Query 参数 ({{ queryParamsCount }})</span>
          <span>{{ reqParamsExpanded ? '▲' : '▼' }}</span>
        </div>
        <div v-show="reqParamsExpanded" class="request-headers">
          <div v-for="(item, index) in enabledParams" :key="index" class="header-row">
            <span class="header-key">{{ item.key }}</span>
            <span class="header-value">{{ item.value }}</span>
          </div>
          <div v-if="enabledParams.length === 0" class="empty-hint">无</div>
        </div>

        <!-- 请求体 -->
        <div class="section-header" @click="reqBodyExpanded = !reqBodyExpanded">
          <span>请求体</span>
          <span>{{ reqBodyExpanded ? '▲' : '▼' }}</span>
        </div>
        <div v-show="reqBodyExpanded" class="request-body">
          <pre v-if="requestStore.body" class="body-content">{{ requestStore.body }}</pre>
          <div v-else class="empty-hint">无</div>
        </div>
      </div>
    </div>

    <!-- 空状态 -->
    <div v-else class="response-empty">
      <div class="empty-icon">📭</div>
      <div class="empty-text">暂无响应</div>
      <div class="empty-hint">发送请求后查看响应结果</div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRequestStore } from '../../stores/request'

const requestStore = useRequestStore()

const loading = computed(() => requestStore.loading)
const error = computed(() => requestStore.error)
const response = computed(() => requestStore.response)
const method = computed(() => requestStore.method)
const fullUrl = computed(() => requestStore.fullUrl)

const tabs = [
  { key: 'body', label: '响应体' },
  { key: 'request', label: '请求参数' }
]
const activeTab = ref('body')

const bodyExpanded = ref(true)
const headersExpanded = ref(false)
const formatted = ref(true)

// 请求参数展开状态
const reqUrlExpanded = ref(true)
const reqHeadersExpanded = ref(true)
const reqParamsExpanded = ref(true)
const reqBodyExpanded = ref(true)

const enabledHeaders = computed(() => {
  return requestStore.headers.filter(h => h.key.trim() && h.enabled !== false)
})

const enabledParams = computed(() => {
  return requestStore.params.filter(p => p.key.trim() && p.enabled !== false)
})

const requestHeadersCount = computed(() => enabledHeaders.value.length)
const queryParamsCount = computed(() => enabledParams.value.length)

const displayContent = computed(() => {
  if (!response.value?.content) return ''
  if (formatted.value) {
    try {
      const parsed = JSON.parse(response.value.content)
      return JSON.stringify(parsed, null, 2)
    } catch (e) {
      return response.value.content
    }
  }
  return response.value.content
})

const responseHeadersCount = computed(() => {
  if (!response.value?.headers) return 0
  return Object.keys(response.value.headers).length
})

function getStatusClass(code) {
  if (code >= 200 && code < 300) return 'status-2xx'
  if (code >= 300 && code < 400) return 'status-3xx'
  if (code >= 400 && code < 500) return 'status-4xx'
  if (code >= 500) return 'status-5xx'
  return ''
}

function formatSize(bytes) {
  if (!bytes) return '0 B'
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / 1024 / 1024).toFixed(1) + ' MB'
}

function toggleFormat() {
  formatted.value = !formatted.value
}

function copyResponse() {
  if (response.value?.content) {
    navigator.clipboard.writeText(displayContent.value)
  }
}

function downloadResponse() {
  if (response.value?.content) {
    const blob = new Blob([response.value.content], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `response-${Date.now()}.json`
    a.click()
    URL.revokeObjectURL(url)
  }
}
</script>

<style scoped>
.response-panel {
  min-height: 200px;
  display: flex;
  flex-direction: column;
}
.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 16px;
  border-bottom: 1px solid var(--border-color);
}
.panel-title {
  font-size: 13px;
  font-weight: 500;
}
.response-actions {
  display: flex;
  gap: 6px;
}
.action-btn {
  padding: 4px 10px;
  background: var(--bg-tertiary);
  border: 1px solid var(--border-color);
  color: var(--text-secondary);
  border-radius: var(--radius-sm);
  font-size: 11px;
  cursor: pointer;
}
.action-btn:hover {
  border-color: var(--accent-blue);
  color: var(--accent-blue);
}
.response-loading {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  color: var(--text-muted);
}
.loading-spinner {
  font-size: 24px;
  animation: spin 1s linear infinite;
}
@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
.response-error {
  padding: 16px;
}
.error-title {
  color: var(--danger);
  font-size: 14px;
  margin-bottom: 8px;
}
.error-detail {
  color: var(--text-secondary);
  font-size: 12px;
  font-family: monospace;
  background: var(--bg-tertiary);
  padding: 8px;
  border-radius: var(--radius-sm);
}
.response-overview {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 10px 16px;
  border-bottom: 1px solid var(--border-color);
}
.status-badge {
  padding: 3px 10px;
  border-radius: var(--radius-sm);
  font-size: 13px;
  font-weight: 600;
  background: var(--bg-tertiary);
}
.overview-item {
  font-size: 12px;
  color: var(--text-secondary);
}
.response-tabs {
  display: flex;
  gap: 4px;
  padding: 8px 16px;
  border-bottom: 1px solid var(--border-color);
}
.response-tabs button {
  padding: 4px 12px;
  background: var(--bg-tertiary);
  border: 1px solid var(--border-color);
  color: var(--text-secondary);
  border-radius: var(--radius-md);
  font-size: 12px;
  cursor: pointer;
}
.response-tabs button.active {
  background: var(--accent-blue);
  border-color: var(--accent-blue);
  color: white;
}
.tab-content {
  padding: 0;
}
.section-header {
  display: flex;
  justify-content: space-between;
  padding: 8px 16px;
  cursor: pointer;
  font-size: 12px;
  color: var(--text-secondary);
  user-select: none;
}
.section-header:hover {
  background: var(--bg-tertiary);
}
.response-body,
.response-headers {
  padding: 0 16px 12px;
}
.body-toolbar {
  margin-bottom: 8px;
}
.body-toolbar button {
  padding: 3px 10px;
  background: var(--bg-tertiary);
  border: 1px solid var(--border-color);
  color: var(--text-secondary);
  border-radius: var(--radius-sm);
  font-size: 11px;
  cursor: pointer;
}
.body-toolbar button.active {
  background: var(--accent-blue);
  border-color: var(--accent-blue);
  color: white;
}
.body-content {
  background: var(--bg-tertiary);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  padding: 10px;
  font-family: 'JetBrains Mono', monospace;
  font-size: 12px;
  line-height: 1.5;
  max-height: 300px;
  overflow: auto;
  white-space: pre-wrap;
  word-break: break-all;
}
.response-headers {
  display: grid;
  grid-template-columns: 1fr 2fr;
  gap: 4px 12px;
}
.header-key {
  color: var(--accent-blue);
  font-size: 12px;
}
.header-value {
  color: var(--text-secondary);
  font-size: 12px;
  word-break: break-all;
}
.request-url {
  padding: 8px 16px 12px;
}
.url-row {
  display: flex;
  align-items: center;
  gap: 8px;
  background: var(--bg-tertiary);
  padding: 8px 12px;
  border-radius: var(--radius-md);
  overflow-x: auto;
}
.method-badge {
  padding: 2px 8px;
  border-radius: var(--radius-sm);
  font-size: 11px;
  font-weight: 600;
  flex-shrink: 0;
}
.method-badge.method-get { background: var(--method-get); color: white; }
.method-badge.method-post { background: var(--method-post); color: white; }
.method-badge.method-put { background: var(--method-put); color: white; }
.method-badge.method-delete { background: var(--method-delete); color: white; }
.method-badge.method-patch { background: var(--method-patch); color: white; }
.url-text {
  font-size: 12px;
  font-family: 'JetBrains Mono', monospace;
  color: var(--text-primary);
  word-break: break-all;
}
.request-headers {
  padding: 0 16px 12px;
  display: grid;
  grid-template-columns: 1fr 2fr;
  gap: 4px 12px;
}
.request-body {
  padding: 0 16px 12px;
}
.empty-hint {
  color: var(--text-muted);
  font-size: 12px;
  padding: 4px 0;
}
.response-empty {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px;
}
.empty-icon {
  font-size: 32px;
  margin-bottom: 12px;
}
.empty-text {
  color: var(--text-secondary);
  font-size: 14px;
  margin-bottom: 4px;
}
.empty-hint {
  color: var(--text-muted);
  font-size: 12px;
}
</style>
