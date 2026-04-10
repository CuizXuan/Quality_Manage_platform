<template>
  <div class="env-manage">
    <div class="toolbar">
      <h2>环境管理</h2>
      <button class="btn primary" @click="showModal = true; editing = null; form = defaultForm()">+ 新建环境</button>
    </div>

    <div v-if="envStore.loading" class="loading">加载中...</div>
    <div v-else class="env-list">
      <div v-for="env in envStore.environments" :key="env.id" class="env-card" :class="{ default: env.is_default }">
        <div class="env-header">
          <div class="env-name">
            {{ env.name }}
            <span v-if="env.is_default" class="badge">默认</span>
          </div>
          <div class="env-actions">
            <button class="icon-btn" @click="editEnv(env)">✏️</button>
            <button v-if="!env.is_default" class="icon-btn" @click="envStore.setDefault(env.id)">⭐</button>
            <button class="icon-btn danger" @click="removeEnv(env.id)">🗑</button>
          </div>
        </div>
        <div v-if="env.description" class="env-desc">{{ env.description }}</div>
        <div class="env-vars">
          <div class="var-row header">
            <span>变量名</span><span>值</span>
          </div>
          <div v-for="(value, key) in env.variables" :key="key" class="var-row">
            <span class="var-key">{{ key }}</span>
            <span class="var-val">{{ value }}</span>
          </div>
          <div v-if="!env.variables || Object.keys(env.variables).length === 0" class="empty-vars">暂无变量</div>
        </div>
      </div>
    </div>

    <!-- 弹窗 -->
    <div v-if="showModal" class="modal-overlay" @click.self="showModal = false">
      <div class="modal">
        <h3>{{ editing ? '编辑环境' : '新建环境' }}</h3>
        <div class="form-group">
          <label>名称</label>
          <input v-model="form.name" placeholder="测试环境" />
        </div>
        <div class="form-group">
          <label>描述</label>
          <input v-model="form.description" placeholder="环境描述" />
        </div>
        <div class="form-group">
          <label>设为默认</label>
          <input type="checkbox" v-model="form.is_default" />
        </div>
        <div class="form-group">
          <label>变量</label>
          <div v-for="(v, k, i) in form.variables" :key="i" class="var-input-row">
            <input v-model="form.variables[i].key" placeholder="变量名" />
            <input v-model="form.variables[i].value" placeholder="值" />
            <button class="icon-btn danger" @click="form.variables.splice(i, 1)">×</button>
          </div>
          <button class="btn" @click="form.variables.push({ key: '', value: '' })">+ 添加变量</button>
        </div>
        <div class="form-actions">
          <button class="btn" @click="showModal = false">取消</button>
          <button class="btn primary" @click="saveEnv">保存</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useEnvironmentStore } from '../stores/environmentStore'

const envStore = useEnvironmentStore()

const showModal = ref(false)
const editing = ref(null)
const form = ref(defaultForm())

function defaultForm() {
  return { name: '', description: '', is_default: false, variables: [] }
}

function editEnv(env) {
  editing.value = env
  const vars = Object.entries(env.variables || {}).map(([key, value]) => ({ key, value }))
  form.value = { name: env.name, description: env.description, is_default: env.is_default, variables: vars }
  showModal.value = true
}

async function saveEnv() {
  const variables = {}
  form.value.variables.forEach(v => { if (v.key) variables[v.key] = v.value })
  const data = { ...form.value, variables }
  if (editing.value) {
    await envStore.updateEnvironment(editing.value.id, data)
  } else {
    await envStore.createEnvironment(data)
  }
  showModal.value = false
}

async function removeEnv(id) {
  if (!confirm('确认删除？')) return
  await envStore.deleteEnvironment(id)
}

onMounted(() => envStore.fetchEnvironments())
</script>

<style scoped>
.env-manage { padding: 16px; }
.toolbar { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
.toolbar h2 { margin: 0; }
.btn { padding: 8px 16px; border-radius: 6px; border: 1px solid var(--border); background: var(--bg-secondary); color: var(--text); cursor: pointer; }
.btn.primary { background: var(--primary); color: #fff; border-color: var(--primary); }
.loading { padding: 40px; text-align: center; }
.env-list { display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 16px; }
.env-card { border: 1px solid var(--border); border-radius: 12px; padding: 16px; background: var(--bg-secondary); }
.env-card.default { border-color: var(--primary); }
.env-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
.env-name { font-weight: 600; font-size: 16px; display: flex; align-items: center; gap: 8px; }
.badge { font-size: 11px; background: var(--primary); color: #fff; padding: 2px 8px; border-radius: 10px; }
.env-desc { font-size: 12px; color: var(--text-secondary); margin-bottom: 8px; }
.env-vars { margin-top: 8px; }
.var-row { display: flex; padding: 4px 0; font-size: 13px; border-bottom: 1px solid var(--border); }
.var-row.header { font-weight: 600; color: var(--text-secondary); font-size: 11px; }
.var-key { color: var(--primary); min-width: 120px; }
.var-val { color: var(--text); word-break: break-all; }
.empty-vars { font-size: 12px; color: var(--text-secondary); padding: 8px 0; }
.env-actions { display: flex; gap: 4px; }
.icon-btn { background: none; border: none; cursor: pointer; padding: 4px; font-size: 14px; }
.icon-btn.danger:hover { color: #f93e3e; }
.modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.5); display: flex; align-items: center; justify-content: center; z-index: 100; }
.modal { background: var(--bg); border-radius: 12px; padding: 24px; width: 480px; max-height: 80vh; overflow-y: auto; }
.modal h3 { margin: 0 0 20px; }
.form-group { margin-bottom: 12px; }
.form-group label { display: block; font-size: 12px; color: var(--text-secondary); margin-bottom: 4px; }
.form-group input[type="text"] { width: 100%; padding: 8px; border: 1px solid var(--border); border-radius: 6px; background: var(--bg-secondary); color: var(--text); box-sizing: border-box; }
.form-group input[type="checkbox"] { width: auto; }
.var-input-row { display: flex; gap: 8px; margin-bottom: 4px; }
.var-input-row input { flex: 1; padding: 6px; border: 1px solid var(--border); border-radius: 4px; background: var(--bg-secondary); color: var(--text); }
.form-actions { display: flex; gap: 8px; justify-content: flex-end; margin-top: 16px; }
</style>
