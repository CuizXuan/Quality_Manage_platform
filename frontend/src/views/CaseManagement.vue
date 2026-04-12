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
        <button class="btn primary" @click="showCreateModal = true">
          <span>+</span> 新建用例
        </button>
      </div>
    </div>

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
        <div v-else-if="filteredCases.length === 0" class="empty">
          <span class="glitch">// 暂无数据</span>
        </div>
        <div v-else class="case-table">
          <div class="table-header">
            <span class="col-method">方法</span>
            <span class="col-name">名称</span>
            <span class="col-path">路径</span>
            <span class="col-actions">操作</span>
          </div>
          <div v-for="c in filteredCases" :key="c.id" class="table-row" @click="openCase(c)">
            <span class="col-method">
              <span class="method-badge" :class="'method-' + c.method.toLowerCase()">{{ c.method }}</span>
            </span>
            <span class="col-name">{{ c.name }}</span>
            <span class="col-path">{{ c.folder_path }}</span>
            <span class="col-actions" @click.stop>
              <button class="icon-btn" title="执行" @click="runCase(c)">▶</button>
              <button class="icon-btn" title="复制" @click="duplicateCase(c.id)">📋</button>
              <button class="icon-btn danger" title="删除" @click="removeCase(c.id)">🗑</button>
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- 新建/编辑弹窗 -->
    <div v-if="showCreateModal" class="modal-overlay" @click.self="showCreateModal = false">
      <div class="modal">
        <div class="modal-header">
          <h3>{{ editingCase ? '// 编辑用例' : '// 新建用例' }}</h3>
          <button class="btn-close" @click="showCreateModal = false">×</button>
        </div>
        <div class="form-body">
          <div class="form-group">
            <label>名称</label>
            <input v-model="form.name" placeholder="用例名称" />
          </div>
          <div class="form-row">
            <div class="form-group">
              <label>请求方法</label>
              <select v-model="form.method">
                <option v-for="m in ['GET','POST','PUT','DELETE','PATCH']" :key="m" :value="m">{{ m }}</option>
              </select>
            </div>
            <div class="form-group flex-1">
              <label>请求地址</label>
              <input v-model="form.url" placeholder="https://api.example.com/path" />
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
        </div>
        <div class="form-actions">
          <button class="btn" @click="showCreateModal = false">取消</button>
          <button class="btn primary" @click="saveCase">{{ editingCase ? '保存' : '创建' }}</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useCaseStore } from '../stores/caseStore'
import { useRequestStore } from '../stores/request'

const caseStore = useCaseStore()
const requestStore = useRequestStore()

const keyword = ref('')
const selectedFolder = ref('/')
const showCreateModal = ref(false)
const editingCase = ref(null)
const form = ref(defaultForm())

const cases = caseStore.cases
const loading = computed(() => caseStore.loading)

const folderList = computed(() => {
  const map = {}
  cases.forEach(c => {
    const path = c.folder_path || '/'
    if (path !== '/') {
      const name = path.split('/').filter(Boolean)[0] || ''
      if (name && !map[name]) {
        map[name] = { name, path: '/' + name, count: 0 }
      }
      if (map[name]) map[name].count++
    }
  })
  return Object.values(map)
})

const filteredCases = computed(() => {
  let list = cases
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

let searchTimer = null
function debounceSearch() {
  clearTimeout(searchTimer)
  searchTimer = setTimeout(() => {
    caseStore.fetchCases({ keyword: keyword.value })
  }, 300)
}

async function saveCase() {
  if (!form.value.name || !form.value.url) return
  if (editingCase.value) {
    await caseStore.updateCase(editingCase.value.id, form.value)
  } else {
    await caseStore.createCase(form.value)
  }
  showCreateModal.value = false
  editingCase.value = null
  form.value = defaultForm()
}

function openCase(c) {
  editingCase.value = c
  form.value = { ...c }
  showCreateModal.value = true
}

async function runCase(c) {
  const result = await caseStore.runCase(c.id)
  console.log('执行结果', result)
}

async function duplicateCase(id) {
  await caseStore.duplicateCase(id)
}

async function removeCase(id) {
  if (!confirm('确认删除？')) return
  await caseStore.deleteCase(id)
}

onMounted(() => {
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

.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.85);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 100;
}

.modal {
  background: var(--bg-panel);
  border: 1px solid var(--neon-cyan);
  box-shadow: 0 0 30px rgba(0, 255, 255, 0.3), inset 0 0 60px rgba(0, 255, 255, 0.05);
  width: 560px;
  max-height: 80vh;
  overflow-y: auto;
  clip-path: polygon(0 0, calc(100% - 20px) 0, 100% 20px, 100% 100%, 20px 100%, 0 calc(100% - 20px));
}

/* 禁用 panel 角落装饰（这些装饰在模态框中不需要） */
.modal::before,
.modal::after {
  display: none;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid var(--border-default);
}

.modal-header h3 {
  font-family: var(--font-title);
  font-size: 14px;
  font-weight: 600;
  letter-spacing: 2px;
  color: var(--neon-cyan);
  margin: 0;
}

.btn-close {
  background: none;
  border: none;
  font-size: 20px;
  color: var(--text-secondary);
  cursor: pointer;
}

.btn-close:hover {
  color: var(--neon-pink);
}

.form-body {
  padding: 20px;
}

.form-group {
  margin-bottom: 16px;
}

.form-group label {
  display: block;
  font-family: var(--font-title);
  font-size: 10px;
  letter-spacing: 1px;
  color: var(--text-secondary);
  margin-bottom: 6px;
}

.form-group input,
.form-group select,
.form-group textarea {
  width: 100%;
  padding: 10px 12px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-default);
  color: var(--neon-cyan);
  font-family: var(--font-mono);
  font-size: 12px;
  outline: none;
  box-sizing: border-box;
}

.form-group input:focus,
.form-group select:focus,
.form-group textarea:focus {
  border-color: var(--neon-cyan);
  box-shadow: 0 0 10px rgba(0, 255, 255, 0.3);
}

.form-row {
  display: flex;
  gap: 12px;
}

.flex-1 {
  flex: 1;
}

.form-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
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
</style>
