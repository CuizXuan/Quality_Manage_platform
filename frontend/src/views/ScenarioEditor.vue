<template>
  <div class="scenario-editor">
    <div class="toolbar">
      <h2>场景编排</h2>
      <button class="btn primary" @click="showModal = true; editing = null; form = defaultForm()">+ 新建场景</button>
    </div>

    <div v-if="scenarioStore.loading" class="loading">加载中...</div>
    <div v-else-if="scenarioStore.scenarios.length === 0" class="empty">
      暂无场景，点击"新建场景"开始
    </div>
    <div v-else class="scenario-list">
      <div v-for="s in scenarioStore.scenarios" :key="s.id" class="scenario-card">
        <div class="scenario-header">
          <div class="scenario-name">{{ s.name }}</div>
          <div class="scenario-actions">
            <button class="icon-btn" title="执行" @click="runScenario(s)">▶</button>
            <button class="icon-btn" @click="openScenario(s)">✏️</button>
            <button class="icon-btn danger" @click="removeScenario(s.id)">🗑</button>
          </div>
        </div>
        <div v-if="s.description" class="scenario-desc">{{ s.description }}</div>
        <div class="step-count">步骤: {{ s.steps?.length || 0 }}</div>
      </div>
    </div>

    <!-- 场景详情弹窗 -->
    <div v-if="showDetailModal" class="modal-overlay" @click.self="showDetailModal = false">
      <div class="modal wide">
        <h3>{{ editingScenario?.name || '场景详情' }}</h3>
        <div v-if="editingScenario?.description" class="desc">{{ editingScenario.description }}</div>

        <!-- 步骤列表 -->
        <div class="steps">
          <div v-for="(step, i) in editingScenario?.steps" :key="step.id" class="step-item">
            <span class="step-num">{{ i + 1 }}</span>
            <span class="step-info">
              <span class="method-badge">{{ cases.find(c => c.id === step.case_id)?.method || '?' }}</span>
              {{ cases.find(c => c.id === step.case_id)?.name || `用例 #${step.case_id}` }}
            </span>
            <button class="icon-btn danger" @click="deleteStep(editingScenario.id, step.id)">×</button>
          </div>
          <div v-if="!editingScenario?.steps?.length" class="empty-steps">暂无步骤</div>
        </div>

        <div class="form-actions">
          <button class="btn" @click="showDetailModal = false">关闭</button>
        </div>
      </div>
    </div>

    <!-- 新建场景弹窗 -->
    <div v-if="showModal" class="modal-overlay" @click.self="showModal = false">
      <div class="modal">
        <h3>{{ editing ? '编辑场景' : '新建场景' }}</h3>
        <div class="form-group">
          <label>名称</label>
          <input v-model="form.name" placeholder="场景名称" />
        </div>
        <div class="form-group">
          <label>描述</label>
          <textarea v-model="form.description" rows="2"></textarea>
        </div>
        <div class="form-actions">
          <button class="btn" @click="showModal = false">取消</button>
          <button class="btn primary" @click="saveScenario">{{ editing ? '保存' : '创建' }}</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useScenarioStore } from '../stores/scenarioStore'
import { useCaseStore } from '../stores/caseStore'

const scenarioStore = useScenarioStore()
const caseStore = useCaseStore()

const showModal = ref(false)
const showDetailModal = ref(false)
const editing = ref(null)
const editingScenario = ref(null)
const form = ref(defaultForm())

const { cases } = caseStore

function defaultForm() {
  return { name: '', description: '', folder_path: '/', variables: {} }
}

async function saveScenario() {
  if (!form.value.name) return
  if (editing.value) {
    await scenarioStore.updateScenario(editing.value.id, form.value)
  } else {
    await scenarioStore.createScenario(form.value)
  }
  showModal.value = false
}

function openScenario(s) {
  editingScenario.value = s
  showDetailModal.value = true
}

async function runScenario(s) {
  const result = await scenarioStore.runScenario(s.id)
  console.log('场景执行结果', result)
}

async function removeScenario(id) {
  if (!confirm('确认删除？')) return
  await scenarioStore.deleteScenario(id)
}

async function deleteStep(scenarioId, stepId) {
  await scenarioStore.deleteStep(scenarioId, stepId)
  await scenarioStore.fetchScenarios()
  // refresh current scenario
  if (editingScenario.value?.id === scenarioId) {
    editingScenario.value = scenarioStore.scenarios.find(s => s.id === scenarioId)
  }
}

onMounted(() => {
  scenarioStore.fetchScenarios()
  caseStore.fetchCases()
})
</script>

<style scoped>
.scenario-editor { padding: 16px; }
.toolbar { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
.toolbar h2 { margin: 0; }
.btn { padding: 8px 16px; border-radius: 6px; border: 1px solid var(--border); background: var(--bg-secondary); color: var(--text); cursor: pointer; }
.btn.primary { background: var(--primary); color: #fff; border-color: var(--primary); }
.loading, .empty { padding: 40px; text-align: center; }
.scenario-list { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 16px; }
.scenario-card { border: 1px solid var(--border); border-radius: 12px; padding: 16px; background: var(--bg-secondary); }
.scenario-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
.scenario-name { font-weight: 600; font-size: 15px; }
.scenario-desc { font-size: 12px; color: var(--text-secondary); margin-bottom: 8px; }
.step-count { font-size: 12px; color: var(--text-secondary); }
.scenario-actions { display: flex; gap: 4px; }
.icon-btn { background: none; border: none; cursor: pointer; padding: 4px; font-size: 14px; }
.icon-btn.danger:hover { color: #f93e3e; }
.modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.5); display: flex; align-items: center; justify-content: center; z-index: 100; }
.modal { background: var(--bg); border-radius: 12px; padding: 24px; width: 480px; max-height: 80vh; overflow-y: auto; }
.modal.wide { width: 640px; }
.modal h3 { margin: 0 0 16px; }
.desc { font-size: 13px; color: var(--text-secondary); margin-bottom: 16px; }
.steps { margin-bottom: 16px; }
.step-item { display: flex; align-items: center; gap: 12px; padding: 8px; border-bottom: 1px solid var(--border); }
.step-num { width: 24px; height: 24px; border-radius: 50%; background: var(--primary); color: #fff; display: flex; align-items: center; justify-content: center; font-size: 12px; flex-shrink: 0; }
.step-info { flex: 1; font-size: 13px; }
.method-badge { display: inline-block; padding: 1px 6px; border-radius: 3px; font-size: 11px; background: #61affe22; color: #61affe; margin-right: 6px; }
.empty-steps { padding: 20px; text-align: center; color: var(--text-secondary); font-size: 13px; }
.form-group { margin-bottom: 12px; }
.form-group label { display: block; font-size: 12px; color: var(--text-secondary); margin-bottom: 4px; }
.form-group input, .form-group textarea { width: 100%; padding: 8px; border: 1px solid var(--border); border-radius: 6px; background: var(--bg-secondary); color: var(--text); box-sizing: border-box; }
.form-actions { display: flex; gap: 8px; justify-content: flex-end; margin-top: 16px; }
</style>
