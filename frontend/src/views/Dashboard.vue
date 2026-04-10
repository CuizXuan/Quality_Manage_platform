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
    <ResponsePanel />
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRequestStore } from '../stores/request'
import RequestParser from '../components/request/RequestParser.vue'
import RequestBar from '../components/request/RequestBar.vue'
import BodyEditor from '../components/request/BodyEditor.vue'
import KeyValueTable from '../components/request/KeyValueTable.vue'
import ResponsePanel from '../components/response/ResponsePanel.vue'
import AuthConfig from '../components/request/AuthConfig.vue'
import AssertionConfig from '../components/request/AssertionConfig.vue'

const requestStore = useRequestStore()

const activeTab = ref('params')
const assertions = ref([])
const authConfig = ref({ type: 'none', config: {} })

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
</style>
