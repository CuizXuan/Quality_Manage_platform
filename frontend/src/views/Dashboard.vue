<template>
  <div class="dashboard">
    <!-- 请求解析器 -->
    <RequestParser @parsed="onParsed" />

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
      </div>
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

const requestStore = useRequestStore()

const activeTab = ref('params')

const tabs = computed(() => [
  {
    label: 'Headers',
    value: 'headers',
    count: requestStore.headers.filter(h => h.key.trim()).length,
  },
  {
    label: 'Params',
    value: 'params',
    count: requestStore.params.filter(p => p.key.trim()).length,
  },
  {
    label: 'Body',
    value: 'body',
    count: requestStore.body ? 1 : 0,
  },
])

function onParsed(result) {
  console.log('[Dashboard] 收到解析结果:', result)
  // 解析成功后，根据情况切换到对应 tab
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
  height: calc(100vh - var(--header-height) - var(--status-bar-height));
  overflow-y: auto;
  padding: 16px;
}
.request-config {
  margin-bottom: 12px;
  padding: 16px;
}
.config-tabs {
  display: flex;
  gap: 4px;
  margin-bottom: 12px;
  border-bottom: 1px solid var(--border);
  padding-bottom: 0;
}
.config-tabs button {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  background: transparent;
  border: none;
  color: var(--text);
  font-size: 13px;
  cursor: pointer;
  border-bottom: 2px solid transparent;
  margin-bottom: -1px;
  transition: all var(--transition-fast);
}
.config-tabs button.active {
  color: var(--primary);
  border-bottom-color: var(--primary);
}
.config-tabs button:hover {
  color: var(--text-h);
}
.tab-count {
  background: var(--bg-secondary);
  padding: 1px 6px;
  border-radius: 10px;
  font-size: 11px;
}
.config-tabs button.active .tab-count {
  background: var(--bg-secondary);
  color: var(--primary);
}
.tab-pane {
  padding: 4px 0;
}
</style>
