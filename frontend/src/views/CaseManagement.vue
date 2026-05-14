<template>
  <div class="case-management">
    <!-- 顶部工具栏 -->
    <div class="toolbar">
      <div class="toolbar-left">
        <h2 class="page-title">
          <span class="prompt">&gt;</span> 用例管理
        </h2>
      </div>
      <div class="toolbar-right">
        <input v-model="keyword" placeholder="搜索用例..." class="search-input" @input="debounceSearch" />
        <div style="display: flex; gap: 8px; align-items: center;">
          <el-select v-model="sortBy" style="width: 130px" @change="debounceSearch">
            <el-option label="按名称" value="name" />
            <el-option label="按创建时间" value="created_at" />
            <el-option label="按ID" value="id" />
          </el-select>
          <el-select v-model="sortOrder" style="width: 100px" @change="debounceSearch">
            <el-option label="↓ 降序" value="desc" />
            <el-option label="↑ 升序" value="asc" />
          </el-select>
        </div>
        <button class="btn primary" @click="editingCase = null; form = defaultForm(); showCreateModal = true">
          <span>+</span> 新建用例
        </button>
      </div>
    </div>

    <!-- Tab 切换：用例列表 / 分类管理 -->
    <el-tabs v-model="activeTab" class="content-tabs cyber-tabs">
      <el-tab-pane label="用例列表" name="cases">
        <!-- 文件夹树 + 用例列表 -->
        <div class="content">
          <!-- 左侧文件夹树 -->
          <div class="folder-tree panel">
        <div class="panel-header">
          <span class="panel-title">// 分类</span>
        </div>
        <div
          class="tree-item root"
          :class="{ active: selectedFolder === '/' }"
          @click="selectFolder('/')"
        >
          <span class="folder-icon">◈</span>
          全部用例 ({{ cases.length }})
        </div>
        <div v-for="folder in folderList" :key="folder.path"
          class="tree-item"
          :class="{ active: selectedFolder === folder.path }"
          @click="selectFolder(folder.path)"
        >
          <span class="folder-icon">▤</span>
          {{ folder.name }} ({{ folder.count }})
        </div>
      </div>

      <!-- 用例列表 -->
      <div class="case-list panel">
        <div class="panel-header">
          <span class="panel-title">// 用例列表</span>
        </div>
        <div v-if="loading" class="loading">
          <span class="loading-spinner">⟳</span>
          <span>加载中...</span>
        </div>
        <div v-else-if="fetchError" class="empty" style="color:#F43F5E;">
          <span>⚠ {{ fetchError }}</span>
        </div>
        <div v-else-if="filteredCases.length === 0" class="empty">
          <span class="glitch">// 暂无数据</span>
        </div>
        <div v-else class="case-table">
          <div class="table-header">
            <span class="col-method">方法</span>
            <span class="col-name">名称</span>
            <span class="col-path">路径</span>
            <span class="col-time">创建时间</span>
            <span class="col-actions">操作</span>
          </div>
          <div v-for="c in filteredCases" :key="c.id" class="table-row" @click="openCase(c)">
            <span class="col-method">
              <span class="method-badge" :class="'method-' + c.method.toLowerCase()">{{ c.method }}</span>
            </span>
            <span class="col-name">{{ c.name }}</span>
            <span class="col-path">{{ c.folder_path }}</span>
            <span class="col-time">{{ formatDate(c.created_at) }}</span>
            <span class="col-actions" @click.stop>
              <button class="icon-btn" :class="{ loading: runningCaseId === c.id }" :disabled="runningCaseId === c.id" title="执行" @click="runCase(c)">
                <span v-if="runningCaseId === c.id" class="loading-spinner">⟳</span>
                <span v-else>▶</span>
              </button>
              <button class="icon-btn" :class="{ loading: duplicatingCaseId === c.id }" :disabled="duplicatingCaseId === c.id" title="复制" @click="duplicateCase(c.id)">
                <span v-if="duplicatingCaseId === c.id" class="loading-spinner">⟳</span>
                <span v-else>📋</span>
              </button>
              <CyberConfirm
                :ref="el => { if (el) cyberConfirmRefs[c.id] = el }"
                title="确认删除这个用例？"
                ok-text="删除"
                cancel-text="取消"
                danger
                :loading="deletingCaseId === c.id"
                @confirm="handleDelete(c.id)"
              >
                <template #trigger>
                  <button class="icon-btn danger" title="删除">🗑</button>
                </template>
              </CyberConfirm>
            </span>
          </div>
        </div>
        </div>
        </div>
      </el-tab-pane>
      <el-tab-pane label="分类管理" name="folders">
        <CaseFolderManager />
      </el-tab-pane>
    </el-tabs>

    <!-- 新建/编辑弹窗 -->
    <div v-if="showCreateModal" class="case-modal-overlay" @click.self="showCreateModal = false">
      <div class="case-modal" role="dialog" aria-modal="true" :aria-labelledby="'case-modal-title'">
        <div class="case-modal-header">
          <h3 :id="'case-modal-title'">{{ editingCase ? '编辑用例' : '新建用例' }}</h3>
          <button class="case-modal-close" aria-label="关闭弹窗" @click="showCreateModal = false">×</button>
        </div>
        <div class="case-modal-body">
          <div class="form-group">
            <label>名称*</label>
            <input v-model="form.name" placeholder="用例名称" :style="formErrors.name ? 'border-color:#ff4d4f' : ''" />
          </div>
          <div class="form-row">
            <div class="form-group">
              <label>请求方法*</label>
              <select v-model="form.method" :style="formErrors.method ? 'border-color:#ff4d4f' : ''">
                <option v-for="m in ['GET','POST','PUT','DELETE','PATCH']" :key="m" :value="m">{{ m }}</option>
              </select>
            </div>
            <div class="form-group flex-1">
              <label>请求地址*</label>
              <input v-model="form.url" placeholder="https://api.example.com/path" :style="formErrors.url ? 'border-color:#ff4d4f' : ''" />
            </div>
          </div>
          <div class="form-group">
            <label>所属分类</label>
            <input v-model="form.folder_path" placeholder="/用户模块/登录" />
          </div>
          <div class="form-group">
            <label>描述</label>
            <textarea v-model="form.description" rows="2" placeholder="用例描述..."></textarea>
          </div>
          <div class="form-group">
            <label>请求头 (JSON)</label>
            <textarea v-model="form.headers" rows="3" placeholder='{"Content-Type": "application/json"}'></textarea>
          </div>
          <div class="form-group">
            <label>请求体</label>
            <textarea v-model="form.request_body" rows="4" placeholder="请求体内容..."></textarea>
          </div>
        </div>
        <div class="case-modal-footer">
          <button class="btn" @click="showCreateModal = false">取消</button>
          <button class="btn primary" @click="saveCase">{{ editingCase ? '保存' : '创建' }}</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onActivated, nextTick, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessageBox, ElMessage } from 'element-plus'
import { useCaseStore } from '../stores/caseStore'
import { useRequestStore } from '../stores/request'
import { storeToRefs } from 'pinia'
import CaseFolderManager from '@/components/CaseFolderManager.vue'
import CyberConfirm from '@/components/common/CyberConfirm.vue'

const router = useRouter()

const caseStore = useCaseStore()
const requestStore = useRequestStore()

// ✅ 用 storeToRefs 保持响应式连接
const { cases, folders, loading, fetchError } = storeToRefs(caseStore)

const keyword = ref('')
const activeTab = ref('cases')
const selectedFolder = ref('/')
const sortBy = ref('created_at')
const sortOrder = ref('desc')
const showCreateModal = ref(false)
const editingCase = ref(null)
const form = ref(defaultForm())
const formErrors = ref({ name: false, method: false, url: false })

watch(showCreateModal, (val) => {
  if (val) formErrors.value = { name: false, method: false, url: false }
})

// ✅ 操作按钮 loading 状态追踪
const runningCaseId = ref(null)    // 正在执行的用例
const duplicatingCaseId = ref(null) // 正在复制的用例
const deletingCaseId = ref(null)   // 正在删除的用例

// CyberConfirm 实例引用，用于手动控制关闭
const cyberConfirmRefs = ref({})

const folderList = computed(() => {
  // 使用 store 中的 folders（来自 case-folders API）
  return folders.value.map(f => ({
    name: f.name,
    path: '/' + f.name,
    count: cases.value.filter(c => c.folder_path === '/' + f.name).length
  }))
})

const filteredCases = computed(() => {
  let list = cases.value
  if (selectedFolder.value !== '/') {
    list = list.filter(c => c.folder_path === selectedFolder.value)
  }
  if (keyword.value) {
    const kw = keyword.value.toLowerCase()
    list = list.filter(c => c.name.toLowerCase().includes(kw) || c.url.toLowerCase().includes(kw))
  }
  return list
})

function defaultForm() {
  return {
    name: '',
    method: 'GET',
    url: '',
    folder_path: '/',
    description: '',
    headers: {},
    params: {},
    body: '',
    body_type: 'json',
    request_body: '',
    response_body: '',
    auth_type: 'none',
    auth_config: {},
    assertions: [],
    pre_script: '',
    post_script: '',
    timeout: 30,
    follow_redirects: true,
    verify_ssl: true,
  }
}

function selectFolder(path) {
  selectedFolder.value = path
}

function formatDate(dateStr) {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString('zh-CN', {
    year: 'numeric', month: '2-digit', day: '2-digit',
    hour: '2-digit', minute: '2-digit'
  })
}

let searchTimer = null
function debounceSearch() {
  clearTimeout(searchTimer)
  searchTimer = setTimeout(() => {
    caseStore.fetchCases({ keyword: keyword.value, sort_by: sortBy.value, order: sortOrder.value })
  }, 300)
}

// 操作后按默认条件重新查询
function refreshWithDefaults() {
  clearTimeout(searchTimer)
  keyword.value = ''
  sortBy.value = 'created_at'
  sortOrder.value = 'desc'
  caseStore.fetchCases({ sort_by: 'created_at', order: 'desc' })
}

async function saveCase() {
  // 重置错误状态
  formErrors.value = { name: false, method: false, url: false }
  const missing = []
  if (!form.value.name?.trim()) {
    formErrors.value.name = true
    missing.push('名称')
  }
  if (!form.value.url?.trim()) {
    formErrors.value.url = true
    missing.push('URL')
  }
  if (missing.length > 0) {
    ElMessage.warning(`请填写必填项：${missing.join('、')}`)
    return
  }
  try {
    if (editingCase.value) {
      await caseStore.updateCase(editingCase.value.id, form.value)
      ElMessage.success('用例更新成功')
    } else {
      await caseStore.createCase(form.value)
      ElMessage.success('用例创建成功')
    }
    showCreateModal.value = false
    editingCase.value = null
    form.value = defaultForm()
    // 操作完成后按默认条件重新查询
    refreshWithDefaults()
  } catch (err) {
    ElMessage.error(editingCase.value ? '用例更新失败' : '用例创建失败')
    console.error('saveCase error:', err)
  }
}

function openCase(c) {
  editingCase.value = c
  form.value = { ...c }
  showCreateModal.value = true
}

async function runCase(c) {
  // 校验用例信息完整性
  if (!c.url || !c.url.trim()) {
    ElMessage.warning('用例 URL 为空，无法执行')
    return
  }
  if (!c.method || !c.method.trim()) {
    ElMessage.warning('用例请求方法为空，无法执行')
    return
  }

  runningCaseId.value = c.id
  let result = {}
  let apiError = null
  try {
    result = await caseStore.runCase(c.id)
    console.log('[CaseManagement] 执行结果:', result)
  } catch (err) {
    apiError = err.message || '请求失败'
    console.error('[CaseManagement] 执行失败:', err)
    result = {}
  }

  // result 结构: execute_case 返回值 { execution_id, case_id, status, response, ... }
  // caseStore.runCase 返回 res.data，所以 result 已经是 execute_case 的返回值
  const execData = result || {}
  const resp = execData?.response || {}
  // execute_case 返回的 status 是 "success" 或 "failure"
  const isSuccess = execData?.status === 'success'
  const error = apiError || execData?.error || resp.error || ''
  const reqBody = c.body || c.request_body || ''
  const reqHeaders = typeof c.headers === 'object' ? JSON.stringify(c.headers) : (c.headers || '')

  console.log('[CaseManagement] isSuccess:', isSuccess, 'resp:', resp)

  await ElMessageBox.alert(
    `<div class="run-result">
      <p><strong>方法:</strong> ${c.method}</p>
      <p><strong>URL:</strong> ${c.url}</p>
      ${reqHeaders ? `<p><strong>请求头:</strong></p><pre style="max-height:150px;overflow:auto;">${formatJson(reqHeaders)}</pre>` : ''}
      ${reqBody ? `<p><strong>请求体:</strong></p><pre style="max-height:150px;overflow:auto;">${formatJson(reqBody)}</pre>` : ''}
      <hr style="border-color:var(--border-default);margin:12px 0;">
      <p><strong>用例:</strong> ${c.name}</p>
      <p><strong>状态:</strong> ${isSuccess ? '✅ 成功' : '❌ 失败'}</p>
      ${resp.time_ms ? `<p><strong>响应时间:</strong> ${resp.time_ms}ms</p>` : ''}
      ${resp.status_code ? `<p><strong>状态码:</strong> ${resp.status_code}</p>` : ''}
      ${resp.body ? `<p><strong>响应体:</strong></p><pre style="max-height:200px;overflow:auto;">${formatJson(resp.body)}</pre>` : ''}
      ${error ? `<p style="color:#F43F5E;"><strong>错误:</strong> ${error}</p>` : ''}
    </div>`,
    '执行结果',
    {
      confirmButtonText: '确定',
      dangerouslyUseHTMLString: true,
      customClass: 'cyber-msgbox',
    }
  )
  runningCaseId.value = null

  // 执行成功后跳转到执行历史页面
  if (isSuccess) {
    router.push('/history')
  }
}

function formatJson(val) {
  if (!val) return ''
  if (typeof val === 'object') return JSON.stringify(val, null, 2)
  try { return JSON.stringify(JSON.parse(val), null, 2) } catch { return val }
}

async function duplicateCase(id) {
  duplicatingCaseId.value = id
  try {
    const newCase = await caseStore.duplicateCase(id)
    ElMessage.success(`用例复制成功 【${newCase?.name}】`)
    // 操作完成后按默认条件重新查询
    refreshWithDefaults()
  } catch (err) {
    ElMessage.error('用例复制失败')
    console.error('duplicateCase error:', err)
  } finally {
    duplicatingCaseId.value = null
  }
}

async function handleDelete(id) {
  deletingCaseId.value = id
  // CyberConfirm 已在 confirm 时自动关闭弹窗，这里手动关闭实例引用
  try {
    await caseStore.deleteCase(id)
    ElMessage.success('删除成功')
    // 清理实例引用
    nextTick(() => { delete cyberConfirmRefs[id] })
    // 操作完成后按默认条件重新查询
    refreshWithDefaults()
  } catch (err) {
    ElMessage.error('删除失败')
    console.error('handleDelete error:', err)
    // 删除失败也要关闭弹窗
    nextTick(() => {
      if (cyberConfirmRefs[id]) {
        cyberConfirmRefs[id].close()
        delete cyberConfirmRefs[id]
      }
    })
  } finally {
    deletingCaseId.value = null
  }
}

onMounted(() => {
  caseStore.fetchCases()
  caseStore.fetchFolders()
})

// keep-alive 场景下：每次激活都重新拉取数据
onActivated(() => {
  caseStore.fetchCases()
})
</script>

<style scoped>
.case-management {
  height: calc(100vh - var(--header-height) - 28px - 32px);
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
}

.toolbar-left, .toolbar-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.page-title {
  font-family: var(--font-title);
  font-size: 16px;
  font-weight: 700;
  letter-spacing: 3px;
  color: var(--neon-cyan);
  margin: 0;
  text-shadow: 0 0 10px var(--neon-cyan);
}

.prompt {
  color: var(--neon-magenta);
}

.search-input {
  padding: 8px 16px;
  width: 250px;
  font-family: var(--font-mono);
  font-size: 12px;
  letter-spacing: 1px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-default);
  color: var(--neon-cyan);
  outline: none;
}

.search-input:focus {
  border-color: var(--neon-cyan);
  box-shadow: 0 0 10px rgba(0, 255, 255, 0.3);
}

.content {
  flex: 1;
  display: flex;
  gap: 16px;
  overflow: hidden;
}

.content-tabs {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.content-tabs .el-tabs__content {
  flex: 1;
  overflow: hidden;
}

.content-tabs .el-tab-pane {
  height: 100%;
}

.folder-tree {
  width: 240px;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
}

.panel-header {
  padding: 10px 16px;
  border-bottom: 1px solid var(--border-default);
  background: rgba(0, 255, 255, 0.02);
}

.panel-title {
  font-family: var(--font-title);
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 2px;
  color: var(--text-secondary);
}

.tree-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  cursor: pointer;
  font-family: var(--font-title);
  font-size: 11px;
  letter-spacing: 1px;
  color: var(--text-secondary);
  border-left: 2px solid transparent;
  transition: all var(--transition-fast);
}

.tree-item:hover, .tree-item.active {
  background: rgba(0, 255, 255, 0.05);
  border-left-color: var(--neon-cyan);
  color: var(--neon-cyan);
}

.tree-item.active {
  background: rgba(0, 255, 255, 0.1);
}

.folder-icon {
  font-size: 12px;
}

.case-list {
  flex: 1;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.case-list .panel-header {
  flex-shrink: 0;
}

.case-table {
  flex: 1;
  overflow-y: auto;
}

.loading, .empty {
  padding: 40px;
  text-align: center;
  color: var(--text-secondary);
  font-family: var(--font-mono);
}

.loading-spinner {
  display: inline-block;
  animation: spin 1s linear infinite;
  margin-right: 10px;
  color: var(--neon-cyan);
}

.glitch {
  animation: glitch 0.5s infinite;
}

.table-header, .table-row {
  display: flex;
  align-items: center;
  padding: 10px 16px;
  border-bottom: 1px solid var(--border-default);
}

.table-header {
  font-family: var(--font-title);
  font-size: 10px;
  font-weight: 600;
  letter-spacing: 2px;
  color: var(--neon-cyan);
  background: rgba(0, 255, 255, 0.02);
  position: sticky;
  top: 0;
}

.table-row {
  cursor: pointer;
  font-size: 12px;
  transition: all var(--transition-fast);
}

.table-row:hover {
  background: rgba(0, 255, 255, 0.05);
}

.col-method { width: 90px; }
.col-name { flex: 1; }
.col-path { width: 160px; color: var(--text-secondary); font-size: 11px; }
.col-time { width: 160px; color: var(--text-secondary); font-size: 11px; }
.col-actions { width: 120px; display: flex; gap: 4px; }

.icon-btn {
  background: transparent;
  border: 1px solid var(--border-default);
  cursor: pointer;
  padding: 4px 8px;
  font-size: 12px;
  color: var(--text-secondary);
  transition: all var(--transition-fast);
}

.icon-btn:hover {
  border-color: var(--neon-cyan);
  color: var(--neon-cyan);
}

.icon-btn.danger:hover {
  border-color: var(--neon-pink);
  color: var(--neon-pink);
}

.icon-btn.loading {
  cursor: not-allowed;
  opacity: 0.6;
}

.icon-btn.loading .loading-spinner {
  animation: spin 1s linear infinite;
  color: var(--neon-cyan);
}

/* ========================================
   CASE MODAL - 组件化命名，隔离全局样式污染
   参照 Ant Design Modal 规范
   ======================================== */

/* 遮罩层 - Ant Design 规范 rgba(0,0,0,0.45) */
.case-modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.45);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 100;
}

/* 弹窗主体 - 12px 圆角符合 Ant Design 大弹窗规范 */
.case-modal {
  background: var(--bg-panel);
  border: 1px solid var(--neon-cyan);
  box-shadow:
    0 0 30px rgba(0, 255, 255, 0.3),
    inset 0 0 60px rgba(0, 255, 255, 0.05);
  width: 560px;
  max-height: 80vh;
  overflow-y: auto;
  border-radius: 12px;  /* Ant Design 大弹窗圆角 */
}

/* 禁用 panel 角落装饰（装饰在模态框中不需要） */
.case-modal::before,
.case-modal::after {
  display: none;
}

/* 标题区 */
.case-modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid var(--border-default);
}

.case-modal-header h3 {
  font-family: var(--font-title);
  font-size: 18px;  /* Ant Design 标题 18px */
  font-weight: 600;
  letter-spacing: 2px;
  color: var(--neon-cyan);
  margin: 0;
}

/* 关闭按钮 */
.case-modal-close {
  background: none;
  border: none;
  font-size: 20px;
  color: var(--text-secondary);
  cursor: pointer;
  transition: color var(--transition-fast);
}

.case-modal-close:hover {
  color: var(--neon-pink);
}

/* 内容区 */
.case-modal-body {
  padding: 20px;
}

/* 底部按钮区 */
.case-modal-footer {
  display: flex;
  gap: 12px;
  justify-content: flex-end;  /* 主按钮在右 */
  padding: 16px 20px;
  border-top: 1px solid var(--border-default);
}

@keyframes glitch {
  0% { transform: translate(0); opacity: 0.7; }
  20% { transform: translate(-2px, 2px); opacity: 0.8; }
  40% { transform: translate(-2px, -2px); opacity: 0.7; }
  60% { transform: translate(2px, 2px); opacity: 0.8; }
  80% { transform: translate(2px, -2px); opacity: 0.7; }
  100% { transform: translate(0); opacity: 0.7; }
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* ========================================
   深色主题适配 - Element Plus 组件
   ======================================== */

/* el-select 下拉框适配 */
:deep(.el-select) {
  --el-fill-color-blank: var(--bg-secondary, #1a1a2e);
  --el-text-color-regular: var(--neon-cyan, #00ffd5);
  --el-border-color: var(--border-default, #2a2a4a);
}

:deep(.el-select .el-input__wrapper) {
  background-color: var(--bg-secondary, #1a1a2e) !important;
  box-shadow: 0 0 0 1px var(--border-default, #2a2a4a) !important;
}

:deep(.el-select .el-input__wrapper:hover) {
  box-shadow: 0 0 0 1px var(--neon-cyan, #00ffd5) !important;
}

:deep(.el-select .el-input__inner) {
  color: var(--neon-cyan, #00ffd5) !important;
}

:deep(.el-select-dropdown) {
  background-color: var(--bg-panel, #16162a) !important;
  border-color: var(--neon-cyan, #00ffd5) !important;
}

:deep(.el-select-dropdown__item) {
  color: var(--text-primary, #e0e0e0) !important;
}

:deep(.el-select-dropdown__item.hover),
:deep(.el-select-dropdown__item:hover) {
  background-color: rgba(0, 255, 255, 0.1) !important;
}

:deep(.el-select-dropdown__item.selected) {
  color: var(--neon-cyan, #00ffd5) !important;
  font-weight: 600;
}

/* el-tabs 标签页适配 */
:deep(.el-tabs) {
  --el-tabs-header-height: 40px;
}

:deep(.el-tabs__header) {
  background-color: transparent !important;
  border-bottom: 1px solid var(--border-default, #2a2a4a) !important;
  margin-bottom: 0;
}

:deep(.el-tabs__nav-wrap::after) {
  display: none !important;
}

:deep(.el-tabs__item) {
  color: var(--text-secondary, #8a8a9a) !important;
  font-family: var(--font-title, 'Orbitron', sans-serif);
  font-size: 12px;
  letter-spacing: 1px;
  padding: 0 20px;
  height: 40px;
  line-height: 40px;
}

:deep(.el-tabs__item:hover) {
  color: var(--neon-cyan, #00ffd5) !important;
}

:deep(.el-tabs__item.is-active) {
  color: var(--neon-cyan, #00ffd5) !important;
}

:deep(.el-tabs__active-bar) {
  background-color: var(--neon-cyan, #00ffd5) !important;
  height: 2px;
}

:deep(.el-tabs__content) {
  padding: 0;
  overflow: hidden;
}

/* el-table 表格适配 */
:deep(.el-table) {
  --el-table-bg-color: var(--bg-panel, #16162a);
  --el-table-tr-bg-color: var(--bg-panel, #16162a);
  --el-table-header-bg-color: rgba(0, 255, 255, 0.05);
  --el-table-header-text-color: var(--neon-cyan, #00ffd5);
  --el-table-text-color: var(--text-primary, #e0e0e0);
  --el-table-border-color: var(--border-default, #2a2a4a);
  --el-table-row-hover-bg-color: rgba(0, 255, 255, 0.05);
  font-family: var(--font-mono, monospace);
}

:deep(.el-table th.el-table__cell) {
  background-color: rgba(0, 255, 255, 0.05) !important;
  color: var(--neon-cyan, #00ffd5) !important;
  font-family: var(--font-title, sans-serif);
  font-size: 11px;
  letter-spacing: 1px;
  font-weight: 600;
  border-bottom: 1px solid var(--border-default, #2a2a4a) !important;
}

:deep(.el-table td.el-table__cell) {
  border-bottom: 1px solid var(--border-default, #2a2a4a) !important;
}

:deep(.el-table__body tr) {
  background-color: var(--bg-panel, #16162a) !important;
}

:deep(.el-table__body tr:hover > td.el-table__cell) {
  background-color: rgba(0, 255, 255, 0.05) !important;
}

:deep(.el-table--striped .el-table__body tr.el-table__row--striped td.el-table__cell) {
  background: rgba(0, 255, 255, 0.02);
}

:deep(.el-table .cell) {
  color: var(--text-primary, #e0e0e0);
}

/* el-button 按钮适配 */
:deep(.el-button--primary) {
  --el-button-bg-color: var(--neon-cyan, #00ffd5);
  --el-button-border-color: var(--neon-cyan, #00ffd5);
  --el-button-text-color: #0a0a1a;
  --el-button-hover-bg-color: rgba(0, 255, 255, 0.8);
  --el-button-hover-border-color: rgba(0, 255, 253, 0.8);
  --el-button-hover-text-color: #0a0a1a;
}

:deep(.el-button--small) {
  font-family: var(--font-title, sans-serif);
  letter-spacing: 1px;
  font-size: 11px;
}

:deep(.el-button + .el-button) {
  margin-left: 8px;
}
</style>
