<template>
  <div class="case-management">
    <!-- 顶部工具栏 -->
    <div class="toolbar">
      <input v-model="keyword" placeholder="搜索用例..." class="search-input" @input="debounceSearch" />
      <button class="btn primary" @click="showCreateModal = true">+ 新建用例</button>
    </div>

    <!-- 文件夹树 + 用例列表 -->
    <div class="content">
      <!-- 左侧文件夹树 -->
      <div class="folder-tree">
        <div class="tree-item root" :class="{ active: selectedFolder === '/' }" @click="selectFolder('/')">
          全部用例 ({{ cases.length }})
        </div>
        <div v-for="folder in folderList" :key="folder.path"
          class="tree-item" :class="{ active: selectedFolder === folder.path }"
          @click="selectFolder(folder.path)">
          📁 {{ folder.name }} ({{ folder.count }})
        </div>
      </div>

      <!-- 用例列表 -->
      <div class="case-list">
        <div v-if="loading" class="loading">加载中...</div>
        <div v-else-if="filteredCases.length === 0" class="empty">
          {{ keyword ? '没有找到匹配的用例' : '暂无用例，点击"新建用例"开始' }}
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
              <span :class="`method-badge method-${c.method.toLowerCase()}`">{{ c.method }}</span>
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
        <h3>{{ editingCase ? '编辑用例' : '新建用例' }}</h3>
        <div class="form-group">
          <label>名称</label>
          <input v-model="form.name" placeholder="用例名称" />
        </div>
        <div class="form-row">
          <div class="form-group">
            <label>方法</label>
            <select v-model="form.method">
              <option v-for="m in ['GET','POST','PUT','DELETE','PATCH']" :key="m" :value="m">{{ m }}</option>
            </select>
          </div>
          <div class="form-group flex-1">
            <label>URL</label>
            <input v-model="form.url" placeholder="https://api.example.com/path" />
          </div>
        </div>
        <div class="form-group">
          <label>文件夹路径</label>
          <input v-model="form.folder_path" placeholder="/用户模块/登录" />
        </div>
        <div class="form-group">
          <label>描述</label>
          <textarea v-model="form.description" rows="2" placeholder="用例描述..."></textarea>
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

const { cases, folders, loading } = caseStore

const folderList = computed(() => {
  const map = {}
  cases.value.forEach(c => {
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
.case-management { height: 100%; display: flex; flex-direction: column; padding: 16px; gap: 12px; }
.toolbar { display: flex; gap: 12px; align-items: center; }
.search-input { flex: 1; padding: 8px 12px; border: 1px solid var(--border); border-radius: 6px; background: var(--bg-secondary); color: var(--text); }
.btn { padding: 8px 16px; border-radius: 6px; border: 1px solid var(--border); background: var(--bg-secondary); color: var(--text); cursor: pointer; }
.btn.primary { background: var(--primary); color: #fff; border-color: var(--primary); }
.content { flex: 1; display: flex; gap: 16px; overflow: hidden; }
.folder-tree { width: 200px; flex-shrink: 0; overflow-y: auto; }
.tree-item { padding: 8px 12px; cursor: pointer; border-radius: 6px; font-size: 13px; }
.tree-item:hover, .tree-item.active { background: var(--bg-secondary); }
.case-list { flex: 1; overflow-y: auto; }
.loading, .empty { padding: 40px; text-align: center; color: var(--text-secondary); }
.case-table { display: table; width: 100%; }
.table-header, .table-row { display: flex; align-items: center; padding: 8px 12px; border-bottom: 1px solid var(--border); }
.table-header { font-weight: 600; font-size: 12px; color: var(--text-secondary); }
.table-row { cursor: pointer; font-size: 13px; }
.table-row:hover { background: var(--bg-secondary); }
.col-method { width: 80px; }
.col-name { flex: 1; }
.col-path { width: 160px; color: var(--text-secondary); font-size: 12px; }
.col-actions { width: 120px; display: flex; gap: 4px; }
.method-badge { padding: 2px 6px; border-radius: 4px; font-size: 11px; font-weight: 600; }
.method-get { background: #61affe22; color: #61affe; }
.method-post { background: #49cc9022; color: #49cc90; }
.method-put { background: #fca13022; color: #fca130; }
.method-delete { background: #f93e3e22; color: #f93e3e; }
.method-patch { background: #50e3c222; color: #50e3c2; }
.icon-btn { background: none; border: none; cursor: pointer; padding: 4px; font-size: 14px; }
.icon-btn.danger:hover { color: #f93e3e; }
.modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.5); display: flex; align-items: center; justify-content: center; z-index: 100; }
.modal { background: var(--bg); border-radius: 12px; padding: 24px; width: 560px; max-height: 80vh; overflow-y: auto; }
.modal h3 { margin: 0 0 20px; }
.form-group { margin-bottom: 12px; }
.form-group label { display: block; font-size: 12px; color: var(--text-secondary); margin-bottom: 4px; }
.form-group input, .form-group select, .form-group textarea { width: 100%; padding: 8px; border: 1px solid var(--border); border-radius: 6px; background: var(--bg-secondary); color: var(--text); box-sizing: border-box; }
.form-row { display: flex; gap: 12px; }
.flex-1 { flex: 1; }
.form-actions { display: flex; gap: 8px; justify-content: flex-end; margin-top: 16px; }
</style>
