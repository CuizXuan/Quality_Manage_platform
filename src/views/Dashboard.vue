<template>
  <div class="dashboard">
    <!-- 请求解析器 -->
    <div class="panel parser-panel">
      <div class="panel-header">
        <span class="panel-title">
          <span class="prompt">&gt;</span> URL PARSER
        </span>
      </div>
      <RequestParser @parsed="onParsed" />
    </div>

    <!-- 请求配置区 -->
    <div class="request-config panel">
      <!-- 请求行 -->
      <RequestBar @response-received="onResponseReceived" />

      <!-- 参数 Tab -->
      <div class="config-tabs">
        <button
          v-for="tab in tabs"
          :key="tab.value"
          :class="{ active: activeTab === tab.value }"
          @click="activeTab = tab.value"
        >
          {{ tab.label }}
          <span v-if="tab.count > 0" class="tab-count">{{ tab.count }}</span>
        </button>
      </div>

      <!-- Tab 内容 -->
      <div class="config-content">
        <div v-show="activeTab === 'headers'" class="tab-pane">
          <KeyValueTable
            :modelValue="requestStore.headers"
            @update:modelValue="val => requestStore.headers = val"
          />
        </div>
        <div v-show="activeTab === 'params'" class="tab-pane">
          <KeyValueTable
            :modelValue="requestStore.params"
            @update:modelValue="val => requestStore.params = val"
          />
        </div>
        <div v-show="activeTab === 'body'" class="tab-pane">
          <BodyEditor
            :modelValue="requestStore.body"
            @update:modelValue="val => requestStore.body = val"
            @update:type="t => requestStore.bodyType = t"
          />
        </div>
        <div v-show="activeTab === 'auth'" class="tab-pane">
          <AuthConfig
            :modelValue="authConfig"
            @update:modelValue="val => authConfig = val"
          />
        </div>
      </div>

      <!-- 断言配置 -->
      <AssertionConfig
        :modelValue="assertions"
        @update:modelValue="val => assertions = val"
      />
    </div>

    <!-- 响应展示区 -->
    <div class="response-wrapper">
      <ResponsePanel @convert-to-case="convertToCase" />
    </div>

    <!-- 用例创建/编辑弹窗 -->
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
          <div class="form-group">
            <label>请求头 (JSON)</label>
            <textarea v-model="caseModalForm.headersJson" rows="3" placeholder='{"Content-Type": "application/json"}'></textarea>
          </div>
          <div class="form-group">
            <label>请求体</label>
            <textarea v-model="caseModalForm.request_body" rows="4" placeholder="请求体内容..."></textarea>
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
import { useRequestStore } from '../stores/request'
import { useCaseStore } from '../stores/caseStore'
import RequestParser from '../components/request/RequestParser.vue'
import RequestBar from '../components/request/RequestBar.vue'
import BodyEditor from '../components/request/BodyEditor.vue'
import KeyValueTable from '../components/request/KeyValueTable.vue'
import ResponsePanel from '../components/response/ResponsePanel.vue'
import AuthConfig from '../components/request/AuthConfig.vue'
import AssertionConfig from '../components/request/AssertionConfig.vue'

const requestStore = useRequestStore()
const caseStore = useCaseStore()

const activeTab = ref('params')
const assertions = ref([])
const authConfig = ref({ type: 'none', config: {} })

// 用例创建弹窗
const showCaseModal = ref(false)
const caseModalForm = ref(defaultCaseForm())

function defaultCaseForm() {
  return {
    name: '',
    method: 'GET',
    url: '',
    folder_path: '/终端导入',
    description: '',
    headers: {},
    headersJson: '{}',
    body: '',
    request_body: '',
  }
}

function buildHeadersObj() {
  const obj = {}
  requestStore.headers.forEach(h => {
    if (h.key && h.enabled !== false) {
      obj[h.key] = h.value
    }
  })
  return obj
}

function openCaseModal() {
  const method = requestStore.method || 'GET'
  const url = requestStore.url || ''
  const headersObj = buildHeadersObj()
  caseModalForm.value = {
    name: `${method} ${url}`,
    method,
    url,
    folder_path: '/终端导入',
    description: `从终端调试创建 - ${new Date().toLocaleString()}`,
    headers: headersObj,
    headersJson: JSON.stringify(headersObj, null, 2),
    body: requestStore.body || '',
    request_body: requestStore.body || '',
  }
  showCaseModal.value = true
}

function closeCaseModal() {
  showCaseModal.value = false
}

async function saveCaseFromModal() {
  if (!caseModalForm.value.name || !caseModalForm.value.name.trim()) {
    ElMessage.warning('请填写用例名称')
    return
  }
  if (!caseModalForm.value.url || !caseModalForm.value.url.trim()) {
    ElMessage.warning('请填写请求地址')
    return
  }
  try {
    let headers = {}
    try {
      headers = JSON.parse(caseModalForm.value.headersJson || '{}')
    } catch {
      ElMessage.warning('请求头 JSON 格式错误，将使用空对象')
      headers = {}
    }
    const caseData = {
      name: caseModalForm.value.name.trim(),
      method: caseModalForm.value.method || 'GET',
      url: caseModalForm.value.url.trim(),
      folder_path: caseModalForm.value.folder_path || '/终端导入',
      description: caseModalForm.value.description || '',
      headers,
      body: caseModalForm.value.request_body || '',
      request_body: caseModalForm.value.request_body || '',
      body_type: 'json',
    }
    console.log('[Dashboard] 创建用例数据:', caseData)
    await caseStore.createCase(caseData)
    ElMessage.success('用例创建成功')
    closeCaseModal()
  } catch (err) {
    ElMessage.error('用例创建失败: ' + (err.message || err))
    console.error('saveCaseFromModal error:', err)
  }
}

const tabs = computed(() => [
  {
    label: 'HEADERS',
    value: 'headers',
    count: requestStore.headers.filter(h => h.key.trim()).length,
  },
  {
    label: 'PARAMS',
    value: 'params',
    count: requestStore.params.filter(p => p.key.trim()).length,
  },
  {
    label: 'BODY',
    value: 'body',
    count: requestStore.body ? 1 : 0,
  },
  {
    label: 'AUTH',
    value: 'auth',
    count: authConfig.value.type !== 'none' ? 1 : 0,
  },
])

function onParsed(result) {
  console.log('[Dashboard] 收到解析结果:', result)
  if (result.params && Object.keys(result.params).length > 0) {
    activeTab.value = 'params'
  } else if (result.headers && Object.keys(result.headers).length > 0) {
    activeTab.value = 'headers'
  } else if (result.body) {
    activeTab.value = 'body'
  } else {
    activeTab.value = 'params'
  }
}

function onResponseReceived() {
  // 响应回来后不做特殊处理
}

async function convertToCase() {
  openCaseModal()
}
</script>

<style scoped>
.dashboard {
  height: calc(100vh - var(--header-height) - 28px - 32px);
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.parser-panel {
  flex-shrink: 0;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 16px;
  border-bottom: 1px solid var(--border-default);
  background: rgba(0, 255, 255, 0.02);
}

.panel-title {
  font-family: var(--font-title);
  font-size: 12px;
  font-weight: 600;
  letter-spacing: 2px;
  color: var(--neon-cyan);
  text-transform: uppercase;
}

.prompt {
  color: var(--neon-magenta);
  margin-right: 8px;
  animation: blink 1s infinite;
}

@keyframes blink {
  0%, 50% { opacity: 1; }
  51%, 100% { opacity: 0; }
}

.request-config {
  padding: 16px;
}

.config-tabs {
  display: flex;
  gap: 4px;
  margin-bottom: 12px;
  border-bottom: 1px solid var(--border-default);
  padding-bottom: 0;
}

.config-tabs button {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  background: transparent;
  border: none;
  border-bottom: 2px solid transparent;
  margin-bottom: -1px;
  color: var(--text-secondary);
  font-family: var(--font-title);
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 2px;
  text-transform: uppercase;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.config-tabs button.active {
  color: var(--neon-cyan);
  border-bottom-color: var(--neon-cyan);
  text-shadow: 0 0 10px var(--neon-cyan);
}

.config-tabs button:hover:not(.active) {
  color: var(--neon-cyan);
}

.tab-count {
  background: rgba(0, 255, 255, 0.2);
  color: var(--neon-cyan);
  padding: 1px 6px;
  border-radius: 10px;
  font-size: 10px;
}

.config-tabs button.active .tab-count {
  background: var(--neon-cyan);
  color: var(--bg-primary);
}

.tab-pane {
  padding: 4px 0;
}

.response-wrapper {
  position: relative;
}

/* 用例创建弹窗 */
.case-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.case-modal {
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  width: 600px;
  max-height: 80vh;
  display: flex;
  flex-direction: column;
}

.case-modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  border-bottom: 1px solid var(--border-color);
}

.case-modal-header h3 {
  margin: 0;
  font-size: 16px;
  color: var(--text-primary);
}

.case-modal-close {
  background: none;
  border: none;
  color: var(--text-secondary);
  font-size: 24px;
  cursor: pointer;
  line-height: 1;
}

.case-modal-close:hover {
  color: var(--text-primary);
}

.case-modal-body {
  padding: 20px;
  overflow-y: auto;
  flex: 1;
}

.case-modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 16px 20px;
  border-top: 1px solid var(--border-color);
}

.form-group {
  margin-bottom: 14px;
}

.form-group label {
  display: block;
  margin-bottom: 6px;
  font-size: 12px;
  color: var(--text-secondary);
  font-weight: 500;
}

.form-group input,
.form-group select,
.form-group textarea {
  width: 100%;
  padding: 8px 12px;
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: 4px;
  color: var(--text-primary);
  font-size: 13px;
  box-sizing: border-box;
}

.form-group input:focus,
.form-group select:focus,
.form-group textarea:focus {
  outline: none;
  border-color: var(--neon-cyan);
}

.form-row {
  display: flex;
  gap: 12px;
  margin-bottom: 14px;
}

.form-row .form-group {
  margin-bottom: 0;
}

.form-row .flex-1 {
  flex: 1;
}
</style>
