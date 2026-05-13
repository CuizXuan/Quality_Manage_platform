<template>
  <div class="ai-workspace">
    <!-- AI Canvas - Main Content Area -->
    <div class="ai-canvas">
      <!-- Layer 1: Request Composer (compact, floating) -->
      <RequestComposer class="floating-card" />

      <!-- Layer 2: AI Insight Grid (MAIN FOCUS) -->
      <AIInsightGrid class="floating-card" />

      <!-- Layer 3: Response Intelligence -->
      <div class="response-section floating-card">
        <div class="section-header">
          <span class="section-icon">📡</span>
          <span class="section-title">Response Intelligence</span>
          <div v-if="requestStore.response" class="response-meta">
            <span class="status-badge" :class="statusClass">{{ requestStore.response.status_code }}</span>
            <span class="duration-badge">{{ requestStore.response.duration_ms }}ms</span>
          </div>
        </div>
        <ResponsePanel />
      </div>

      <!-- Layer 4: AI Activity Stream -->
      <AIActivityStream />
    </div>

    <!-- Case Modal (reuse existing) -->
    <div v-if="showCaseModal" class="case-modal-overlay" @click.self="closeCaseModal">
      <div class="case-modal" role="dialog" aria-modal="true">
        <div class="case-modal-header">
          <h3>新建用例</h3>
          <button class="case-modal-close" aria-label="关闭弹窗" @click="closeCaseModal">×</button>
        </div>
        <div class="case-modal-body">
          <div class="form-group">
            <label>名称</label>
            <input v-model="caseModalForm.name" placeholder="用例名称" />
          </div>
          <div class="form-row">
            <div class="form-group">
              <label>请求方法</label>
              <select v-model="caseModalForm.method">
                <option v-for="m in ['GET','POST','PUT','DELETE','PATCH']" :key="m" :value="m">{{ m }}</option>
              </select>
            </div>
            <div class="form-group flex-1">
              <label>请求地址</label>
              <input v-model="caseModalForm.url" placeholder="https://api.example.com/path" />
            </div>
          </div>
          <div class="form-group">
            <label>所属分类</label>
            <input v-model="caseModalForm.folder_path" placeholder="/用户模块/登录" />
          </div>
          <div class="form-group">
            <label>描述</label>
            <textarea v-model="caseModalForm.description" rows="2" placeholder="用例描述..."></textarea>
          </div>
        </div>
        <div class="case-modal-footer">
          <button class="btn" @click="closeCaseModal">取消</button>
          <button class="btn primary" @click="saveCaseFromModal">创建</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { useRequestStore } from '@/stores/request'
import { useCaseStore } from '@/stores/caseStore'
import RequestComposer from '@/components/request/RequestComposer.vue'
import AIInsightGrid from '@/components/ai/AIInsightGrid.vue'
import ResponsePanel from '@/components/response/ResponsePanel.vue'
import AIActivityStream from '@/components/ai/AIActivityStream.vue'

const requestStore = useRequestStore()
const caseStore = useCaseStore()

const showCaseModal = ref(false)
const caseModalForm = ref(defaultCaseForm())

const statusClass = computed(() => {
  const code = requestStore.response?.status_code
  if (!code) return ''
  return code >= 200 && code < 300 ? 'success' : code >= 400 && code < 500 ? 'warning' : 'error'
})

function defaultCaseForm() {
  return {
    name: '',
    method: 'GET',
    url: '',
    folder_path: '/终端导入',
    description: '',
    headers: {},
    body: '',
    request_body: '',
  }
}

function openCaseModal() {
  const method = requestStore.method || 'GET'
  const url = requestStore.url || ''
  const headersObj = {}
  requestStore.headers.forEach(h => {
    if (h.key && h.enabled !== false) {
      headersObj[h.key] = h.value
    }
  })
  caseModalForm.value = {
    name: `${method} ${url}`,
    method,
    url,
    folder_path: '/终端导入',
    description: `从终端调试创建 - ${new Date().toLocaleString()}`,
    headers: headersObj,
    body: requestStore.body || '',
    request_body: requestStore.body || '',
  }
  showCaseModal.value = true
}

function closeCaseModal() {
  showCaseModal.value = false
}

async function saveCaseFromModal() {
  if (!caseModalForm.value.name?.trim()) {
    ElMessage.warning('请填写用例名称')
    return
  }
  if (!caseModalForm.value.url?.trim()) {
    ElMessage.warning('请填写请求地址')
    return
  }
  try {
    const caseData = {
      name: caseModalForm.value.name.trim(),
      method: caseModalForm.value.method || 'GET',
      url: caseModalForm.value.url.trim(),
      folder_path: caseModalForm.value.folder_path || '/终端导入',
      description: caseModalForm.value.description || '',
      headers: caseModalForm.value.headers || {},
      body: caseModalForm.value.request_body || '',
      request_body: caseModalForm.value.request_body || '',
      body_type: 'json',
    }
    await caseStore.createCase(caseData)
    ElMessage.success('用例创建成功')
    closeCaseModal()
  } catch (err) {
    ElMessage.error('用例创建失败: ' + (err.message || err))
  }
}
</script>

<style scoped>
.ai-workspace {
  height: calc(100vh - var(--header-height) - 28px - 32px);
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding: 16px;
}

.ai-canvas {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

/* Floating Card Base */
.floating-card {
  background: var(--glass-bg);
  backdrop-filter: blur(20px);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-xl);
  transition: all var(--transition-normal);
}

.floating-card:hover {
  box-shadow: var(--shadow-card-hover);
}

/* Response Section */
.response-section {
  padding: 16px 20px;
}

.section-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 16px;
}

.section-icon {
  font-size: 18px;
}

.section-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
  flex: 1;
}

.response-meta {
  display: flex;
  align-items: center;
  gap: 8px;
}

.status-badge {
  font-size: 11px;
  font-weight: 600;
  padding: 2px 8px;
  border-radius: 4px;
  background: var(--bg-card-hover);
}

.status-badge.success {
  background: var(--success-muted);
  color: var(--success);
}

.status-badge.warning {
  background: var(--warning-muted);
  color: var(--warning);
}

.status-badge.error {
  background: var(--error-muted);
  color: var(--error);
}

.duration-badge {
  font-size: 11px;
  font-family: var(--font-mono);
  color: var(--text-tertiary);
}

/* Case Modal */
.case-modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(15, 18, 28, 0.88);
  backdrop-filter: blur(32px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 99999;
}

.case-modal {
  background: rgba(15, 18, 28, 0.95);
  border: 1px solid var(--border-default);
  border-radius: 24px;
  width: 560px;
  max-height: 80vh;
  display: flex;
  flex-direction: column;
  box-shadow: var(--shadow-xl);
  overflow: hidden;
}

.case-modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 24px;
  border-bottom: 1px solid var(--border-default);
}

.case-modal-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
}

.case-modal-close {
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-card);
  border: none;
  border-radius: 8px;
  color: var(--text-secondary);
  font-size: 18px;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.case-modal-close:hover {
  background: var(--bg-card-hover);
  color: var(--text-primary);
}

.case-modal-body {
  padding: 24px;
  overflow-y: auto;
  flex: 1;
}

.case-modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 16px 24px;
  border-top: 1px solid var(--border-default);
}

.form-group {
  margin-bottom: 16px;
}

.form-group label {
  display: block;
  margin-bottom: 6px;
  font-size: 12px;
  font-weight: 500;
  color: var(--text-secondary);
}

.form-group input,
.form-group select,
.form-group textarea {
  width: 100%;
  padding: 10px 12px;
  background: var(--bg-card);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-md);
  color: var(--text-primary);
  font-size: 13px;
  font-family: var(--font-body);
  transition: all var(--transition-fast);
  box-sizing: border-box;
}

.form-group input:focus,
.form-group select:focus,
.form-group textarea:focus {
  outline: none;
  border-color: var(--primary);
  box-shadow: 0 0 0 3px var(--primary-muted);
}

.form-row {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
}

.form-row .form-group {
  margin-bottom: 0;
}

.form-row .flex-1 {
  flex: 1;
}

.btn {
  padding: 10px 20px;
  background: var(--bg-card);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-md);
  color: var(--text-secondary);
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.btn:hover {
  background: var(--bg-card-hover);
  color: var(--text-primary);
}

.btn.primary {
  background: var(--primary);
  border-color: var(--primary);
  color: white;
}

.btn.primary:hover {
  background: var(--primary-hover);
}
</style>