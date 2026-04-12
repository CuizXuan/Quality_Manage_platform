<template>

  <div class="env-manage">

    <div class="toolbar">

      <h2 class="page-title">

        <span class="prompt">&gt;</span> 环境管理

      </h2>

      <button class="btn primary" @click="showModal = true; editing = null; form = defaultForm()">

        <span>+</span> 新建环境

      </button>

    </div>



    <div v-if="envStore.loading" class="loading">

      <span class="loading-spinner">⟳</span>

      加载中...

    </div>

    <div v-else class="env-list">

      <div v-for="env in envStore.environments" :key="env.id" class="env-card panel" :class="{ default: env.is_default }">

        <div class="env-header">

          <div class="env-name">

            <span class="env-icon">◈</span>

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

          <div class="var-header">

            <span>变量</span>

          </div>

          <div v-for="(value, key) in env.variables" :key="key" class="var-row">

            <span class="var-key">{{ key }}</span>

            <span class="var-equals">=</span>

            <span class="var-val">{{ value }}</span>

          </div>

          <div v-if="!env.variables || Object.keys(env.variables).length === 0" class="empty-vars">

            -- 暂无变量 --

          </div>

        </div>

      </div>

    </div>



    <!-- 弹窗 -->

    <div v-if="showModal" class="modal-overlay" @click.self="showModal = false">

      <div class="modal">

        <div class="modal-header">

          <h3>{{ editing ? '// 编辑环境' : '// 新建环境' }}</h3>

          <button class="btn-close" @click="showModal = false">×</button>

        </div>

        <div class="form-body">

          <div class="form-group">

            <label>名称</label>

            <input v-model="form.name" placeholder="测试环境" />

          </div>

          <div class="form-group">

            <label>描述</label>

            <input v-model="form.description" placeholder="环境描述" />

          </div>

          <div class="form-group checkbox-group">

            <label>

              <input type="checkbox" v-model="form.is_default" />

              设为默认环境

            </label>

          </div>

          <div class="form-group">

            <label>变量</label>

            <div v-for="(v, k, i) in form.variables" :key="i" class="var-input-row">

              <input v-model="form.variables[i].key" placeholder="键" />

              <span class="equals">=</span>

              <input v-model="form.variables[i].value" placeholder="值" />

              <button class="icon-btn danger" @click="form.variables.splice(i, 1)">×</button>

            </div>

            <button class="btn" @click="form.variables.push({ key: '', value: '' })">+ 添加变量</button>

          </div>

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

.env-manage {

  padding: 16px;

}



.toolbar {

  display: flex;

  justify-content: space-between;

  align-items: center;

  margin-bottom: 24px;

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



.loading {

  padding: 40px;

  text-align: center;

  color: var(--neon-cyan);

  font-family: var(--font-mono);

}



.loading-spinner {

  display: inline-block;

  animation: spin 1s linear infinite;

  margin-right: 10px;

}



.env-list {

  display: grid;

  grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));

  gap: 16px;

}



.env-card {

  padding: 16px;

}



.env-card.default {

  border-color: var(--neon-cyan);

  box-shadow: 0 0 20px rgba(0, 255, 255, 0.2);

}



.env-header {

  display: flex;

  justify-content: space-between;

  align-items: center;

  margin-bottom: 8px;

}



.env-name {

  font-family: var(--font-title);

  font-size: 14px;

  font-weight: 600;

  letter-spacing: 1px;

  color: var(--neon-cyan);

  display: flex;

  align-items: center;

  gap: 8px;

}



.env-icon {

  color: var(--neon-magenta);

}



.badge {

  font-size: 9px;

  background: var(--neon-cyan);

  color: var(--bg-primary);

  padding: 2px 6px;

  border-radius: 2px;

  letter-spacing: 1px;

}



.env-desc {

  font-size: 12px;

  color: var(--text-secondary);

  margin-bottom: 12px;

}



.env-vars {

  background: var(--bg-secondary);

  border-radius: 4px;

  overflow: hidden;

}



.var-header {

  padding: 8px 12px;

  font-family: var(--font-title);

  font-size: 10px;

  letter-spacing: 2px;

  color: var(--text-secondary);

  background: rgba(0, 255, 255, 0.05);

  border-bottom: 1px solid var(--border-default);

}



.var-row {

  display: flex;

  padding: 6px 12px;

  font-family: var(--font-mono);

  font-size: 12px;

  border-bottom: 1px solid var(--border-default);

}



.var-row:last-child {

  border-bottom: none;

}



.var-key {

  color: var(--neon-cyan);

}



.var-equals {

  color: var(--text-secondary);

  margin: 0 8px;

}



.var-val {

  color: var(--neon-magenta);

  word-break: break-all;

}



.empty-vars {

  padding: 12px;

  text-align: center;

  color: var(--text-secondary);

  font-family: var(--font-mono);

  font-size: 11px;

}



.env-actions {

  display: flex;

  gap: 4px;

}



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

  box-shadow: 0 0 30px rgba(0, 255, 255, 0.3);

  width: 480px;

  max-height: 80vh;

  overflow-y: auto;

}

/* 禁用 panel 角落装饰 */
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



.form-group input[type="text"] {

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



.form-group input[type="text"]:focus {

  border-color: var(--neon-cyan);

  box-shadow: 0 0 10px rgba(0, 255, 255, 0.3);

}



.checkbox-group label {

  display: flex;

  align-items: center;

  gap: 8px;

  cursor: pointer;

  color: var(--neon-cyan);

  font-family: var(--font-title);

  font-size: 11px;

  letter-spacing: 1px;

}



.var-input-row {

  display: flex;

  align-items: center;

  gap: 8px;

  margin-bottom: 8px;

}



.var-input-row input {

  flex: 1;

  padding: 8px;

}



.equals {

  color: var(--text-secondary);

}



.form-actions {

  display: flex;

  gap: 12px;

  justify-content: flex-end;

  padding: 16px 20px;

  border-top: 1px solid var(--border-default);

}



@keyframes spin {

  from { transform: rotate(0deg); }

  to { transform: rotate(360deg); }

}

</style>

