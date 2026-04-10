<template>
  <aside class="sidebar">
    <div class="sidebar-tabs">
      <button
        :class="{ active: activeTab === 'collections' }"
        @click="activeTab = 'collections'"
      >
        <span class="tab-icon">☰</span>
        <span>集合</span>
      </button>
      <button
        :class="{ active: activeTab === 'history' }"
        @click="activeTab = 'history'"
      >
        <span class="tab-icon">◷</span>
        <span>历史</span>
      </button>
    </div>

    <!-- 集合视图 -->
    <div v-show="activeTab === 'collections'" class="sidebar-content">
      <div class="sidebar-toolbar">
        <input
          v-model="searchKeyword"
          placeholder="SEARCH..."
          class="cyber-input"
        />
        <button class="cyber-btn-small" @click="showAddCollection = true" title="新建集合">+</button>
      </div>

      <!-- 添加集合弹窗 -->
      <div v-if="showAddCollection" class="inline-input">
        <input
          v-model="newCollectionName"
          placeholder="集合名称"
          class="cyber-input"
          @keyup.enter="createCollection"
          ref="newColInput"
        />
        <button class="cyber-btn-small success" @click="createCollection">✓</button>
        <button class="cyber-btn-small danger" @click="showAddCollection = false">✕</button>
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
            <span class="col-count">[{{ col.requests.length }}]</span>
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
              -- EMPTY --
            </div>
          </div>
        </div>
        <div v-if="filteredCollections.length === 0" class="empty-tip">
          <span class="glitch">// NO DATA</span>
        </div>
      </div>
    </div>

    <!-- 历史视图 -->
    <div v-show="activeTab === 'history'" class="sidebar-content">
      <div class="sidebar-toolbar">
        <input
          v-model="historyKeyword"
          placeholder="SEARCH..."
          class="cyber-input"
        />
        <button class="cyber-btn-small danger" @click="clearHistory" title="清空历史">🗑</button>
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
            {{ item.statusCode || 'ERR' }}
          </div>
        </div>
        <div v-if="filteredHistory.length === 0" class="empty-tip">
          <span class="glitch">// NO HISTORY</span>
        </div>
      </div>
    </div>

    <!-- Scanline overlay -->
    <div class="sidebar-scanlines"></div>
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
  if (!isoString) return ''
  const date = new Date(isoString)
  const now = new Date()
  const diff = now - date
  const minutes = Math.floor(diff / 60000)
  if (minutes < 1) return 'NOW'
  if (minutes < 60) return `${minutes}m`
  const hours = Math.floor(minutes / 60)
  if (hours < 24) return `${hours}h`
  return `${Math.floor(hours / 24)}d`
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
  height: calc(100vh - var(--header-height) - 28px);
  background: var(--bg-panel);
  border-right: 1px solid var(--border-default);
  display: flex;
  flex-direction: column;
  position: fixed;
  top: var(--header-height);
  left: 0;
  overflow: hidden;
  font-size: 13px;
  z-index: 50;
}

.sidebar-tabs {
  display: flex;
  border-bottom: 1px solid var(--border-default);
}

.sidebar-tabs button {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 12px 8px;
  background: transparent;
  border: none;
  border-bottom: 2px solid transparent;
  color: var(--text-secondary);
  font-family: var(--font-title);
  font-size: 10px;
  font-weight: 600;
  letter-spacing: 2px;
  text-transform: uppercase;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.sidebar-tabs button.active {
  color: var(--neon-cyan);
  background: rgba(0, 255, 255, 0.1);
  border-bottom-color: var(--neon-cyan);
  text-shadow: 0 0 10px var(--neon-cyan);
}

.sidebar-tabs button:hover:not(.active) {
  color: var(--neon-cyan);
  background: rgba(0, 255, 255, 0.05);
}

.tab-icon {
  font-size: 14px;
}

.sidebar-content {
  flex: 1;
  overflow-y: auto;
  padding: 8px;
  position: relative;
}

.sidebar-toolbar {
  display: flex;
  gap: 6px;
  margin-bottom: 8px;
}

.cyber-input {
  flex: 1;
  padding: 6px 10px;
  font-family: var(--font-mono);
  font-size: 11px;
  letter-spacing: 1px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-default);
  color: var(--neon-cyan);
  outline: none;
}

.cyber-input:focus {
  border-color: var(--neon-cyan);
  box-shadow: 0 0 10px rgba(0, 255, 255, 0.3), inset 0 0 10px rgba(0, 255, 255, 0.1);
}

.cyber-input::placeholder {
  color: rgba(0, 255, 255, 0.3);
}

.cyber-btn-small {
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  border: 1px solid var(--border-default);
  color: var(--text-secondary);
  font-size: 14px;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.cyber-btn-small:hover {
  border-color: var(--neon-cyan);
  color: var(--neon-cyan);
  box-shadow: 0 0 10px rgba(0, 255, 255, 0.3);
}

.cyber-btn-small.success {
  border-color: var(--neon-green);
  color: var(--neon-green);
}

.cyber-btn-small.danger {
  border-color: var(--neon-pink);
  color: var(--neon-pink);
}

.inline-input {
  display: flex;
  gap: 4px;
  margin-bottom: 8px;
}

.inline-input .cyber-input {
  flex: 1;
}

.collection-header {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 10px;
  cursor: pointer;
  border-radius: 4px;
  border: 1px solid transparent;
  color: var(--text-secondary);
  font-family: var(--font-title);
  font-size: 11px;
  letter-spacing: 1px;
  transition: all var(--transition-fast);
}

.collection-header:hover {
  background: rgba(0, 255, 255, 0.05);
  border-color: rgba(0, 255, 255, 0.2);
  color: var(--neon-cyan);
}

.col-name {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  text-transform: uppercase;
}

.col-count {
  font-size: 10px;
  color: var(--text-secondary);
}

.request-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 10px 6px 24px;
  cursor: pointer;
  border-radius: 4px;
  font-size: 11px;
  border-left: 2px solid transparent;
  transition: all var(--transition-fast);
}

.request-item:hover {
  background: rgba(0, 255, 255, 0.05);
  border-left-color: var(--neon-cyan);
}

.request-name {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  color: var(--text-primary);
}

.history-item {
  padding: 10px;
  cursor: pointer;
  border-radius: 4px;
  margin-bottom: 4px;
  position: relative;
  border: 1px solid transparent;
  transition: all var(--transition-fast);
}

.history-item:hover {
  background: rgba(0, 255, 255, 0.05);
  border-color: rgba(0, 255, 255, 0.2);
}

.history-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 4px;
}

.history-time {
  color: var(--text-secondary);
  font-size: 10px;
  letter-spacing: 1px;
}

.history-url {
  font-size: 11px;
  color: var(--text-primary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-family: var(--font-mono);
}

.history-status {
  position: absolute;
  right: 10px;
  top: 10px;
  font-family: var(--font-title);
  font-size: 10px;
  font-weight: 600;
  letter-spacing: 1px;
}

.status-success { color: var(--neon-green); }
.status-error { color: #f00; }

.empty-tip {
  text-align: center;
  color: var(--text-secondary);
  font-size: 11px;
  padding: 20px;
  font-family: var(--font-mono);
}

.glitch {
  animation: glitch 0.5s infinite;
}

.sidebar-scanlines {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: repeating-linear-gradient(
    0deg,
    rgba(0, 201, 167, 0.03) 0px,
    rgba(0, 201, 167, 0.03) 1px,
    transparent 1px,
    transparent 2px
  );
  pointer-events: none;
  opacity: 0.5;
}

@keyframes glitch {
  0% { transform: translate(0); opacity: 0.7; }
  20% { transform: translate(-1px, 1px); opacity: 0.8; }
  40% { transform: translate(-1px, -1px); opacity: 0.7; }
  60% { transform: translate(1px, 1px); opacity: 0.8; }
  80% { transform: translate(1px, -1px); opacity: 0.7; }
  100% { transform: translate(0); opacity: 0.7; }
}
</style>
