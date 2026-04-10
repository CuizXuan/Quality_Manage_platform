<template>
  <div class="execution-history">
    <div class="toolbar">
      <h2>执行历史</h2>
      <div class="filters">
        <select v-model="filterStatus" @change="fetchLogs">
          <option value="">全部状态</option>
          <option value="success">成功</option>
          <option value="failure">失败</option>
          <option value="error">错误</option>
        </select>
      </div>
    </div>

    <div v-if="loading" class="loading">加载中...</div>
    <div v-else-if="logs.length === 0" class="empty">暂无执行记录</div>
    <div v-else class="log-list">
      <div v-for="log in logs" :key="log.id" class="log-card" @click="openLog(log)">
        <div class="log-header">
          <span :class="`status-badge ${log.status}`">{{ statusLabel(log.status) }}</span>
          <span class="log-time">{{ formatTime(log.created_at) }}</span>
        </div>
        <div class="log-url">
          <span class="method-badge method-{{ log.request_method?.toLowerCase() }}">{{ log.request_method }}</span>
          {{ log.request_url }}
        </div>
        <div class="log-meta">
          <span v-if="log.response_status">状态码: {{ log.response_status }}</span>
          <span v-if="log.response_time_ms">耗时: {{ log.response_time_ms }}ms</span>
          <span v-if="log.case_id">用例 #{{ log.case_id }}</span>
        </div>
      </div>
    </div>

    <!-- 详情弹窗 -->
    <div v-if="showDetail" class="modal-overlay" @click.self="showDetail = false">
      <div class="modal wide">
        <h3>执行详情</h3>
        <div class="detail-grid">
          <div class="detail-section">
            <h4>请求</h4>
            <pre>{{ JSON.stringify(selectedLog?.request_headers, null, 2) }}</pre>
            <div><strong>URL:</strong> {{ selectedLog?.request_url }}</div>
            <div><strong>Method:</strong> {{ selectedLog?.request_method }}</div>
            <div><strong>Body:</strong> <pre>{{ selectedLog?.request_body }}</pre></div>
          </div>
          <div class="detail-section">
            <h4>响应</h4>
            <div><strong>Status:</strong> {{ selectedLog?.response_status }}</div>
            <div><strong>Time:</strong> {{ selectedLog?.response_time_ms }}ms</div>
            <div><strong>Size:</strong> {{ selectedLog?.response_size }} bytes</div>
            <div><strong>Body:</strong> <pre>{{ formatBody(selectedLog?.response_body) }}</pre></div>
          </div>
        </div>
        <div v-if="selectedLog?.assertion_results?.length" class="assertions">
          <h4>断言结果</h4>
          <div v-for="a in selectedLog.assertion_results" :key="a.id" class="assertion-item">
            <span :class="a.passed ? 'pass' : 'fail'">{{ a.passed ? '✅' : '❌' }}</span>
            {{ a.type }}: {{ a.message }}
          </div>
        </div>
        <div v-if="selectedLog?.error_message" class="error-msg">
          <strong>错误:</strong> {{ selectedLog.error_message }}
        </div>
        <div class="form-actions">
          <button class="btn" @click="showDetail = false">关闭</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { logsApi } from '../api/log'

const logs = ref([])
const loading = ref(false)
const filterStatus = ref('')
const showDetail = ref(false)
const selectedLog = ref(null)

async function fetchLogs() {
  loading.value = true
  try {
    const params = filterStatus.value ? { status: filterStatus.value } : {}
    const res = await logsApi.list(params)
    logs.value = res.data
  } finally {
    loading.value = false
  }
}

async function openLog(log) {
  const res = await logsApi.get(log.id)
  selectedLog.value = res.data
  showDetail.value = true
}

function statusLabel(s) {
  return { success: '成功', failure: '失败', error: '错误', pending: '等待', running: '运行中', skipped: '跳过' }[s] || s
}

function formatTime(ts) {
  if (!ts) return ''
  return new Date(ts).toLocaleString('zh-CN')
}

function formatBody(body) {
  if (!body) return ''
  try { return JSON.stringify(JSON.parse(body), null, 2) } catch { return body }
}

onMounted(fetchLogs)
</script>

<style scoped>
.execution-history { padding: 16px; }
.toolbar { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
.toolbar h2 { margin: 0; }
.filters select { padding: 8px 12px; border: 1px solid var(--border); border-radius: 6px; background: var(--bg-secondary); color: var(--text); }
.loading, .empty { padding: 40px; text-align: center; }
.log-list { display: flex; flex-direction: column; gap: 8px; }
.log-card { border: 1px solid var(--border); border-radius: 8px; padding: 12px; cursor: pointer; background: var(--bg-secondary); }
.log-card:hover { background: var(--bg-tertiary, var(--bg)); }
.log-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px; }
.status-badge { padding: 2px 8px; border-radius: 10px; font-size: 11px; font-weight: 600; }
.status-badge.success { background: #49cc9022; color: #49cc90; }
.status-badge.failure { background: #f93e3e22; color: #f93e3e; }
.status-badge.error { background: #f93e3e22; color: #f93e3e; }
.status-badge.pending { background: #fca13022; color: #fca130; }
.status-badge.running { background: #61affe22; color: #61affe; }
.log-time { font-size: 12px; color: var(--text-secondary); }
.log-url { font-size: 13px; margin-bottom: 4px; word-break: break-all; }
.method-badge { display: inline-block; padding: 1px 6px; border-radius: 3px; font-size: 11px; font-weight: 600; background: #61affe22; color: #61affe; margin-right: 6px; }
.log-meta { display: flex; gap: 16px; font-size: 12px; color: var(--text-secondary); }
.modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.5); display: flex; align-items: center; justify-content: center; z-index: 100; }
.modal { background: var(--bg); border-radius: 12px; padding: 24px; width: 700px; max-height: 80vh; overflow-y: auto; }
.modal.wide { width: 800px; }
.modal h3 { margin: 0 0 16px; }
.detail-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-bottom: 16px; }
.detail-section { border: 1px solid var(--border); border-radius: 8px; padding: 12px; }
.detail-section h4 { margin: 0 0 8px; font-size: 13px; }
.detail-section pre { background: var(--bg-secondary); padding: 8px; border-radius: 4px; font-size: 12px; overflow-x: auto; max-height: 200px; }
.assertions { margin-bottom: 16px; }
.assertions h4 { margin: 0 0 8px; }
.assertion-item { padding: 4px 0; font-size: 13px; }
.pass { margin-right: 6px; }
.fail { margin-right: 6px; }
.error-msg { padding: 12px; background: #f93e3e11; border-radius: 6px; color: #f93e3e; margin-bottom: 16px; font-size: 13px; }
.form-actions { display: flex; gap: 8px; justify-content: flex-end; }
.btn { padding: 8px 16px; border-radius: 6px; border: 1px solid var(--border); background: var(--bg-secondary); color: var(--text); cursor: pointer; }
</style>
