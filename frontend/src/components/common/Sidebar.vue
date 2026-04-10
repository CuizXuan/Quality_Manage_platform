<template>
  <aside class="sidebar">
    <div class="sidebar-tabs">
      <button
        :class="{ active: activeTab === 'collections' }"
        @click="activeTab = 'collections'"
      >
        📁 集合
      </button>
      <button
        :class="{ active: activeTab === 'history' }"
        @click="activeTab = 'history'"
      >
        🕐 历史
      </button>
    </div>

    <!-- 集合视图 -->
    <div v-show="activeTab === 'collections'" class="sidebar-content">
      <div class="sidebar-toolbar">
        <input
          v-model="searchKeyword"
          placeholder="搜索集合..."
          class="search-input"
        />
        <button class="btn-add" @click="showAddCollection = true" title="新建集合">+</button>
      </div>

      <!-- 添加集合弹窗 -->
      <div v-if="showAddCollection" class="inline-input">
        <input
          v-model="newCollectionName"
          placeholder="集合名称"
          @keyup.enter="createCollection"
          ref="newColInput"
        />
        <button @click="createCollection">✓</button>
        <button @click="showAddCollection = false">✕</button>
      </div>

      <!-- 集合树 -->
      <div class="collection-tree">
        <div
          v-for="col in filteredCollections"
          :key="col.id"
          class="collection-item"
        >
          <div class="collection-header" @click="toggleCollection(col.id)">
            <span class="expand-icon">{{ expandedCollections.includes(col.id) ? '📂' : '📁' }}</span>
            <span class="col-name">{{ col.name }}</span>
            <span class="col-count">{{ col.requests.length }}</span>
          </div>
          <div v-show="expandedCollections.includes(col.id)" class="request-list">
            <div
              v-for="req in col.requests"
              :key="req.id"
              class="request-item"
              @click="loadRequest(req)"
            >
              <span class="method-badge" :class="'method-' + req.method.toLowerCase()">
                {{ req.method }}
              </span>
              <span class="request-name">{{ req.name || req.url }}</span>
            </div>
            <div v-if="col.requests.length === 0" class="empty-tip">
              空集合
            </div>
          </div>
        </div>
        <div v-if="filteredCollections.length === 0" class="empty-tip">
          暂无集合，点击 + 新建
        </div>
      </div>
    </div>

    <!-- 历史视图 -->
    <div v-show="activeTab === 'history'" class="sidebar-content">
      <div class="sidebar-toolbar">
        <input
          v-model="historyKeyword"
          placeholder="搜索历史..."
          class="search-input"
        />
        <button class="btn-add" @click="clearHistory" title="清空历史">🗑</button>
      </div>
      <div class="history-list">
        <div
          v-for="item in filteredHistory"
          :key="item.id"
          class="history-item"
          @click="loadHistoryItem(item)"
        >
          <div class="history-meta">
            <span class="method-badge" :class="'method-' + item.method.toLowerCase()">
              {{ item.method }}
            </span>
            <span class="history-time">{{ formatTime(item.createdAt) }}</span>
          </div>
          <div class="history-url">{{ item.url }}</div>
          <div class="history-status" :class="getStatusClass(item.statusCode)">
            {{ item.statusCode || '错误' }}
          </div>
        </div>
        <div v-if="filteredHistory.length === 0" class="empty-tip">
          暂无历史记录
        </div>
      </div>
    </div>
  </aside>
</template>

<script setup>
import { ref, computed, nextTick } from 'vue'
import { useCollectionStore } from '../../stores/collection'
import { useHistoryStore } from '../../stores/history'
import { useRequestStore } from '../../stores/request'

const emit = defineEmits(['load-request'])

const collectionStore = useCollectionStore()
const historyStore = useHistoryStore()
const requestStore = useRequestStore()

const activeTab = ref('collections')
const searchKeyword = ref('')
const historyKeyword = ref('')
const showAddCollection = ref(false)
const newCollectionName = ref('')
const newColInput = ref(null)
const expandedCollections = ref([])

const filteredCollections = computed(() => {
  if (!searchKeyword.value) return collectionStore.collections
  const kw = searchKeyword.value.toLowerCase()
  return collectionStore.collections.filter(col =>
    col.name.toLowerCase().includes(kw) ||
    col.requests.some(r => r.name?.toLowerCase().includes(kw) || r.url?.toLowerCase().includes(kw))
  )
})

const filteredHistory = computed(() => {
  return historyStore.getFiltered({ keyword: historyKeyword.value })
})

function toggleCollection(id) {
  const idx = expandedCollections.value.indexOf(id)
  if (idx >= 0) {
    expandedCollections.value.splice(idx, 1)
  } else {
    expandedCollections.value.push(id)
  }
}

function createCollection() {
  if (newCollectionName.value.trim()) {
    collectionStore.createCollection(newCollectionName.value.trim())
    newCollectionName.value = ''
    showAddCollection.value = false
  }
}

function clearHistory() {
  if (confirm('确定清空所有历史记录？')) {
    historyStore.clearAll()
  }
}

function loadRequest(req) {
  requestStore.setRequest({
    method: req.method,
    url: req.url,
    fullUrl: req.fullUrl || req.url,
    headers: req.headers || {},
    params: req.params || {},
    body: req.body || '',
  })
  emit('load-request')
}

function loadHistoryItem(item) {
  requestStore.setRequest({
    method: item.method,
    url: item.url,
    fullUrl: item.fullUrl || item.url,
    headers: item.headers || {},
    params: item.params || {},
    body: item.body || '',
  })
  emit('load-request')
}

function formatTime(isoString) {
  const date = new Date(isoString)
  const now = new Date()
  const diff = now - date
  const minutes = Math.floor(diff / 60000)
  if (minutes < 1) return '刚刚'
  if (minutes < 60) return `${minutes}分钟前`
  const hours = Math.floor(minutes / 60)
  if (hours < 24) return `${hours}小时前`
  return `${Math.floor(hours / 24)}天前`
}

function getStatusClass(code) {
  if (!code) return 'status-error'
  if (code >= 200 && code < 300) return 'status-success'
  if (code >= 400) return 'status-error'
  return ''
}
</script>

<style scoped>
.sidebar {
  width: var(--sidebar-width);
  height: calc(100vh - var(--header-height) - var(--status-bar-height));
  background: var(--bg);
  border-right: 1px solid var(--border);
  display: flex;
  flex-direction: column;
  position: fixed;
  top: var(--header-height);
  left: 0;
  overflow: hidden;
  font-size: 14px;
}
.sidebar-tabs {
  display: flex;
  border-bottom: 1px solid var(--border);
}
.sidebar-tabs button {
  flex: 1;
  padding: 10px;
  background: transparent;
  border: none;
  color: var(--text);
  font-size: 12px;
  cursor: pointer;
  border-bottom: 2px solid transparent;
  transition: all var(--transition-fast);
}
.sidebar-tabs button.active {
  color: var(--primary);
  border-bottom-color: var(--primary);
}
.sidebar-tabs button:hover {
  color: var(--text-h);
}
.sidebar-content {
  flex: 1;
  overflow-y: auto;
  padding: 8px;
}
.sidebar-toolbar {
  display: flex;
  gap: 6px;
  margin-bottom: 8px;
}
.search-input {
  flex: 1;
  padding: 5px 8px;
  font-size: 12px;
}
.btn-add {
  width: 28px;
  height: 28px;
  background: var(--social-bg);
  border: 1px solid var(--border);
  color: var(--text-h);
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}
.btn-add:hover {
  background: var(--primary);
  color: #fff;
}
.inline-input {
  display: flex;
  gap: 4px;
  margin-bottom: 8px;
}
.inline-input input {
  flex: 1;
  padding: 5px 8px;
  font-size: 12px;
}
.inline-input button {
  padding: 5px 8px;
  background: var(--primary);
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}
.collection-header {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 8px;
  cursor: pointer;
  border-radius: 4px;
  color: var(--text-h);
  font-size: 13px;
}
.collection-header:hover {
  background: var(--bg-secondary);
}
.col-name {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.col-count {
  color: var(--text);
  font-size: 11px;
}
.request-item {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 5px 8px 5px 24px;
  cursor: pointer;
  border-radius: 4px;
  font-size: 12px;
}
.request-item:hover {
  background: var(--bg-secondary);
}
.request-name {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  color: var(--text);
}
.method-badge {
  font-size: 10px;
  font-weight: 600;
  padding: 1px 4px;
  border-radius: 3px;
  flex-shrink: 0;
}
.history-item {
  padding: 8px;
  cursor: pointer;
  border-radius: 4px;
  margin-bottom: 4px;
  position: relative;
}
.history-item:hover {
  background: var(--bg-secondary);
}
.history-meta {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 4px;
}
.history-time {
  color: var(--text);
  font-size: 11px;
}
.history-url {
  color: var(--text);
  font-size: 12px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.history-status {
  position: absolute;
  right: 8px;
  top: 8px;
  font-size: 11px;
  font-weight: 600;
}
.status-success { color: var(--success); }
.status-error { color: var(--danger); }
.empty-tip {
  text-align: center;
  color: var(--text);
  font-size: 12px;
  padding: 16px;
}
</style>
