<template>
  <header class="app-header">
    <div class="header-left">
      <span class="logo">
        <span class="logo-icon">⚡</span>
        <span class="logo-text">CYBER<span class="highlight">API</span></span>
      </span>

      <!-- 导航滚动区域 -->
      <div class="nav-scroll-container">
        <!-- 左滚动按钮 -->
        <button
          v-if="showLeftArrow"
          class="nav-scroll-btn left"
          @click="scrollNav(-1)"
          title="向左滚动"
        >◀</button>

        <nav ref="navRef" class="main-nav">
          <!-- 动态渲染菜单 -->
          <template v-for="item in visibleMenuItems" :key="item.name">
            <!-- 有子菜单的 -->
            <div
              v-if="item.children && item.children.length"
              class="nav-item nav-dropdown"
              :class="{ active: isActiveGroup(item) }"
              @mouseenter="onDropdownEnter(item.name)"
              @mouseleave="onDropdownLeave(item.name)"
            >
              <span class="nav-icon">{{ item.icon }}</span>
              <span>{{ item.name }}</span>
              <span class="dropdown-arrow">▼</span>
              <div
                class="nav-dropdown-menu"
                :class="{ 'is-open': showDropdown }"
                @mouseenter="onMenuEnter"
                @mouseleave="onMenuLeave"
              >
                <router-link
                  v-for="child in item.children"
                  :key="child.path"
                  :to="child.path"
                  class="dropdown-item"
                  :class="{ active: $route.path === child.path }"
                >
                  <span>{{ child.icon }}</span>
                  <span>{{ child.name }}</span>
                </router-link>
              </div>
            </div>
            <!-- 无子菜单的 -->
            <router-link
              v-else
              :to="item.path"
              class="nav-item"
              :class="{ active: $route.path === item.path }"
            >
              <span class="nav-icon">{{ item.icon }}</span>
              <span>{{ item.name }}</span>
            </router-link>
          </template>

          <!-- 系统管理（固定在最后） -->
          <div
            class="nav-item nav-dropdown"
            :class="{ active: isSysActive }"
            @mouseenter="onDropdownEnter('sys')"
            @mouseleave="onDropdownLeave('sys')"
          >
            <span class="nav-icon">⚙</span>
            <span>系统管理</span>
            <span class="dropdown-arrow">▼</span>
            <div
              class="nav-dropdown-menu"
              :class="{ 'is-open': showDropdown }"
              @mouseenter="onMenuEnter"
              @mouseleave="onMenuLeave"
            >
              <router-link to="/menu-manage" class="dropdown-item" :class="{ active: $route.path === '/menu-manage' }">
                <span>📋</span><span>菜单管理</span>
              </router-link>
              <router-link to="/ai-model-config" class="dropdown-item" :class="{ active: $route.path === '/ai-model-config' }">
                <span>🤖</span><span>AI模型配置</span>
              </router-link>
              <router-link to="/users" class="dropdown-item" :class="{ active: $route.path === '/users' }">
                <span>👥</span><span>用户管理</span>
              </router-link>
              <router-link to="/projects" class="dropdown-item" :class="{ active: $route.path === '/projects' }">
                <span>📁</span><span>项目管理</span>
              </router-link>
              <router-link to="/assets" class="dropdown-item" :class="{ active: $route.path === '/assets' }">
                <span>📦</span><span>资产管理</span>
              </router-link>
              <div class="dropdown-divider"></div>
              <router-link to="/audit" class="dropdown-item" :class="{ active: $route.path === '/audit' }">
                <span>📋</span><span>审计日志</span>
              </router-link>
            </div>
          </div>
        </nav>

        <!-- 右滚动按钮 -->
        <button
          v-if="showRightArrow"
          class="nav-scroll-btn right"
          @click="scrollNav(1)"
          title="向右滚动"
        >▶</button>
      </div>
    </div>

    <div class="header-right">
      <div class="env-switch">
        <span class="env-label">环境:</span>
        <select v-model="currentEnv" class="cyber-select">
          <option value="dev">DEV</option>
          <option value="test">TEST</option>
          <option value="prod">PROD</option>
        </select>
        <span class="env-dot" :class="currentEnv"></span>
      </div>

      <div class="theme-toggle" @click="emit('toggle-theme')">
        <span class="theme-icon" :class="{ dark: isDark }">
          {{ isDark ? '☾' : '☀' }}
        </span>
        <span class="theme-label">{{ isDark ? '深色' : '浅色' }}</span>
      </div>

      <router-link to="/settings" class="icon-btn" title="Settings">⚙</router-link>

      <div class="header-user">
        <span class="user-name">{{ authStore.currentUsername || '用户' }}</span>
        <button class="logout-btn" @click="logout" title="退出登录">🚪</button>
      </div>
    </div>

    <div class="scan-line"></div>
  </header>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const props = defineProps({
  isDark: {
    type: Boolean,
    default: true
  }
})

const emit = defineEmits(['toggle-theme'])
const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

function logout() {
  authStore.logout()
  router.push('/login')
}

const currentEnv = ref('dev')
const navRef = ref(null)
const showLeftArrow = ref(false)
const showRightArrow = ref(false)

// ==================== 菜单配置 ====================
// 默认菜单配置（系统管理固定在最后）
const DEFAULT_MENU = [
  { name: '终端', icon: '⌘', path: '/' },
  { name: '用例', icon: '☰', path: '/cases' },
  { name: '场景', icon: '⚙', path: '/scenarios' },
  { name: '环境', icon: '◈', path: '/environments' },
  { name: '日志', icon: '▤', path: '/history' },
  { name: '数据集', icon: '◫', path: '/datasets' },
  { name: '定时', icon: '◷', path: '/schedules' },
  { name: 'Mock', icon: '◇', path: '/mock-rules' },
  { name: '报告', icon: '▦', path: '/reports' },
  { name: '代码质量', icon: '⚡', path: '/repositories' },
  { name: '缺陷管理', icon: '🐛', path: '/defects' },
  { name: '质量门禁', icon: '⚖', path: '/quality-gates' },
  { name: 'AI分析', icon: '🤖', path: '/ai-analysis' },
  { name: '大盘', icon: '📊', path: '/quality-dashboard' },
  { name: 'AI实验室', icon: '✨', path: '/ai-lab' },
  { name: '压测', icon: '⚡', path: '/load-test' },
  { name: '混沌', icon: '🧪', path: '/chaos' },
  { name: '数据', icon: '🗄', path: '/test-data' },
  { name: '插件市场', icon: '🛒', path: '/marketplace' },
]

// 带分组的菜单配置（示例）
const GROUPED_MENU = [
  {
    name: '测试工具',
    icon: '🧰',
    children: [
      { name: '用例', icon: '☰', path: '/cases' },
      { name: '场景', icon: '⚙', path: '/scenarios' },
      { name: 'Mock', icon: '◇', path: '/mock-rules' },
      { name: '报告', icon: '▦', path: '/reports' },
    ]
  },
  {
    name: '质量保障',
    icon: '🔍',
    children: [
      { name: '代码质量', icon: '⚡', path: '/repositories' },
      { name: '缺陷管理', icon: '🐛', path: '/defects' },
      { name: '质量门禁', icon: '⚖', path: '/quality-gates' },
      { name: 'AI分析', icon: '🤖', path: '/ai-analysis' },
    ]
  },
  {
    name: '高级测试',
    icon: '🚀',
    children: [
      { name: 'AI实验室', icon: '✨', path: '/ai-lab' },
      { name: '压测', icon: '⚡', path: '/load-test' },
      { name: '混沌', icon: '🧪', path: '/chaos' },
      { name: '数据', icon: '🗄', path: '/test-data' },
    ]
  },
  {
    name: '基础功能',
    icon: '⌘',
    children: [
      { name: '终端', icon: '⌘', path: '/' },
      { name: '环境', icon: '◈', path: '/environments' },
      { name: '日志', icon: '▤', path: '/history' },
      { name: '数据集', icon: '◫', path: '/datasets' },
      { name: '定时', icon: '◷', path: '/schedules' },
    ]
  },
]

// 加载菜单配置（优先从 localStorage 读取）
function loadMenuConfig() {
  try {
    const saved = localStorage.getItem('nav_menu_config')
    if (saved) {
      return JSON.parse(saved)
    }
  } catch (e) {
    console.warn('Failed to load menu config:', e)
  }
  return null
}

// 当前菜单（默认或配置的）
const menuConfig = loadMenuConfig()
const navMenu = computed(() => {
  if (menuConfig) {
    // 配置模式：把系统管理的 children 动态加入
    return menuConfig
  }
  return DEFAULT_MENU
})

// 用于渲染的菜单项（系统管理之外的）
const visibleMenuItems = computed(() => navMenu.value)

// ==================== 滚动逻辑 ====================
const NAV_ITEM_APPROX_WIDTH = 80 // 每个菜单项预估宽度

function updateScrollButtons() {
  if (!navRef.value) return
  const el = navRef.value
  const hasOverflow = el.scrollWidth > el.clientWidth + 2
  showRightArrow.value = hasOverflow && el.scrollLeft + el.clientWidth < el.scrollWidth - 2
  showLeftArrow.value = el.scrollLeft > 2
}

function scrollNav(direction) {
  if (!navRef.value) return
  const scrollAmount = NAV_ITEM_APPROX_WIDTH * 3
  navRef.value.scrollBy({ left: direction * scrollAmount, behavior: 'smooth' })
  setTimeout(updateScrollButtons, 300)
}

// ==================== 下拉菜单逻辑 ====================
const showDropdown = ref(false)
let showTimer = null
let hideTimer = null
const SHOW_DELAY = 100     // 鼠标进入后延迟显示
const HIDE_DELAY = 200     // 鼠标离开后延迟隐藏（防止间隙闪烁）

function onDropdownEnter(name) {
  clearTimeout(hideTimer)
  clearTimeout(showTimer)
  showTimer = setTimeout(() => {
    showDropdown.value = true
  }, SHOW_DELAY)
}

function onDropdownLeave(name) {
  clearTimeout(showTimer)
  clearTimeout(hideTimer)
  hideTimer = setTimeout(() => {
    showDropdown.value = false
  }, HIDE_DELAY)
}

function onMenuEnter() {
  clearTimeout(hideTimer)
  clearTimeout(showTimer)
  showDropdown.value = true
}

function onMenuLeave() {
  clearTimeout(showTimer)
  hideTimer = setTimeout(() => {
    showDropdown.value = false
  }, HIDE_DELAY)
}

function isActiveGroup(item) {
  return (item.children || []).some(c => c.path === route.path)
}

const isSysActive = computed(() => {
  const sysPaths = ['/menu-manage', '/users', '/projects', '/assets', '/audit']
  return sysPaths.includes(route.path)
})

// ==================== 生命周期 ====================
let resizeObserver = null

onMounted(() => {
  nextTick(() => {
    updateScrollButtons()
    resizeObserver = new ResizeObserver(() => {
      updateScrollButtons()
    })
    if (navRef.value) {
      resizeObserver.observe(navRef.value)
    }
  })
})

onUnmounted(() => {
  if (resizeObserver) {
    resizeObserver.disconnect()
  }
})
</script>

<style scoped>
.app-header {
  height: var(--header-height);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  background: var(--bg-panel);
  border-bottom: 1px solid var(--border-default);
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 100;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 0;
  flex: 1;
  min-width: 0;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-shrink: 0;
}

.logo {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-right: 24px;
}

.logo-icon {
  font-size: 24px;
  filter: drop-shadow(0 0 10px var(--neon-cyan));
  animation: pulse-glow 2s infinite;
}

.logo-text {
  font-family: var(--font-title);
  font-size: 18px;
  font-weight: 800;
  letter-spacing: 3px;
  color: #fff;
  text-shadow: 0 0 10px var(--neon-cyan);
}

.logo-text .highlight {
  color: var(--neon-cyan);
}

/* ==================== 导航滚动容器 ==================== */
.nav-scroll-container {
  display: flex;
  align-items: center;
  position: relative;
}

.main-nav {
  display: flex;
  gap: 2px;
  overflow-x: visible;
  scroll-behavior: smooth;
  /* 隐藏滚动条但保持功能 */
  scrollbar-width: none;  /* Firefox */
  -ms-overflow-style: none;  /* IE/Edge */
  max-width: calc(100vw - 400px); /* 留出右侧空间 */
}

.main-nav::-webkit-scrollbar {
  display: none; /* Chrome/Safari */
}

/* 确保下拉菜单不被任何祖先裁剪 */
.main-nav,
.nav-scroll-container {
  overflow: visible !important;
}

/* ==================== 滚动按钮 ==================== */
.nav-scroll-btn {
  flex-shrink: 0;
  width: 24px;
  height: 32px;
  background: var(--bg-secondary);
  border: 1px solid var(--neon-cyan);
  color: var(--neon-cyan);
  cursor: pointer;
  font-size: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0.7;
  transition: all 0.2s;
  z-index: 10;
}

.nav-scroll-btn:hover {
  opacity: 1;
  background: rgba(0, 255, 255, 0.15);
  box-shadow: 0 0 10px rgba(0, 255, 255, 0.4);
}

.nav-scroll-btn.left {
  border-radius: 4px 0 0 4px;
  margin-right: 1px;
}

.nav-scroll-btn.right {
  border-radius: 0 4px 4px 0;
  margin-left: 1px;
}

/* ==================== 导航项 ==================== */
.nav-item {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 14px;
  border: 1px solid transparent;
  border-radius: 4px;
  font-family: var(--font-title);
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 1px;
  text-transform: uppercase;
  color: var(--text-secondary);
  text-decoration: none;
  position: relative;
  overflow: visible;
  transition: all var(--transition-fast);
  white-space: nowrap;
  cursor: pointer;
  flex-shrink: 0;
}

.nav-item::before {
  content: '';
  position: absolute;
  left: 0;
  top: 50%;
  width: 0;
  height: 2px;
  background: var(--neon-cyan);
  box-shadow: 0 0 10px var(--neon-cyan);
  transform: translateY(-50%);
  transition: width var(--transition-fast);
}

.nav-item:hover {
  color: var(--neon-cyan);
  background: rgba(0, 255, 255, 0.05);
  border-color: rgba(0, 255, 255, 0.3);
}

.nav-item.active {
  color: var(--neon-cyan);
  background: rgba(0, 255, 255, 0.1);
  border-color: var(--neon-cyan);
  box-shadow: 0 0 15px rgba(0, 255, 255, 0.3), inset 0 0 15px rgba(0, 255, 255, 0.1);
}

.nav-item.active::before {
  width: 100%;
}

.nav-icon {
  font-size: 13px;
}

.dropdown-arrow {
  font-size: 8px;
  opacity: 0.7;
}

/* ==================== 下拉菜单 ==================== */
.nav-dropdown {
  position: relative;
}

.nav-dropdown-menu {
  display: none;
  position: absolute;
  top: calc(100% + 4px);
  left: 0;
  min-width: 180px;
  background: var(--bg-panel);
  border: 1px solid var(--neon-cyan);
  border-radius: 6px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5), 0 0 15px rgba(0, 255, 255, 0.2);
  z-index: 9999;
  padding: 4px 0;
  overflow: hidden;
}

/* JS 控制显示（延迟 1 秒后显示，移开立即隐藏） */
.nav-dropdown-menu.is-open {
  display: block;
}

.dropdown-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 14px;
  font-family: var(--font-title);
  font-size: 11px;
  letter-spacing: 1px;
  color: var(--text-secondary);
  text-decoration: none;
  transition: all 0.15s;
  cursor: pointer;
}

.dropdown-item:hover {
  background: rgba(0, 255, 255, 0.1);
  color: var(--neon-cyan);
}

.dropdown-item.active {
  background: rgba(0, 255, 255, 0.15);
  color: var(--neon-cyan);
}

.dropdown-divider {
  height: 1px;
  background: rgba(0, 255, 255, 0.2);
  margin: 4px 0;
}

/* ==================== 右侧区域 ==================== */
.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.env-switch {
  display: flex;
  align-items: center;
  gap: 8px;
}

.env-label {
  font-family: var(--font-title);
  font-size: 10px;
  color: var(--text-secondary);
  letter-spacing: 2px;
}

.cyber-select {
  font-family: var(--font-title);
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 1px;
  padding: 4px 8px;
  background: var(--bg-secondary);
  border: 1px solid var(--neon-cyan);
  color: var(--neon-cyan);
  cursor: pointer;
  outline: none;
  border-radius: 3px;
}

.cyber-select:focus {
  box-shadow: 0 0 10px rgba(0, 255, 255, 0.5);
}

.env-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  animation: pulse-glow 1.5s infinite;
}

.env-dot.dev {
  background: var(--neon-green);
  box-shadow: 0 0 10px var(--neon-green);
}
.env-dot.test {
  background: var(--neon-yellow);
  box-shadow: 0 0 10px var(--neon-yellow);
}
.env-dot.prod {
  background: #f00;
  box-shadow: 0 0 10px #f00;
}

.theme-toggle {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  background: rgba(0, 255, 255, 0.1);
  border: 1px solid var(--neon-cyan);
  border-radius: 4px;
  cursor: pointer;
  transition: all var(--transition-fast);
  user-select: none;
}

.theme-toggle:hover {
  background: rgba(0, 255, 255, 0.2);
  box-shadow: 0 0 15px rgba(0, 255, 255, 0.4);
  transform: scale(1.05);
}

.theme-icon {
  font-size: 16px;
  transition: all 0.3s ease;
}

.theme-icon.dark {
  filter: drop-shadow(0 0 5px var(--neon-cyan));
}

.theme-icon:not(.dark) {
  filter: drop-shadow(0 0 5px var(--neon-yellow));
}

.theme-label {
  font-family: var(--font-title);
  font-size: 10px;
  font-weight: 600;
  letter-spacing: 1px;
  color: var(--neon-cyan);
}

.icon-btn {
  color: var(--text-secondary);
  font-size: 18px;
  text-decoration: none;
  padding: 6px 10px;
  border: 1px solid transparent;
  border-radius: 4px;
  transition: all var(--transition-fast);
  display: flex;
  align-items: center;
}

.icon-btn:hover {
  color: var(--neon-cyan);
  border-color: var(--neon-cyan);
  box-shadow: 0 0 10px rgba(0, 255, 255, 0.5);
}

.header-user {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 0 8px;
  border-left: 1px solid var(--border-default);
  margin-left: 4px;
}

.user-name {
  font-size: 12px;
  color: var(--text-secondary);
  max-width: 80px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.logout-btn {
  background: none;
  border: 1px solid transparent;
  border-radius: 4px;
  padding: 4px 6px;
  font-size: 14px;
  cursor: pointer;
  color: var(--text-secondary);
  transition: all var(--transition-fast);
}

.logout-btn:hover {
  color: var(--neon-pink);
  border-color: var(--neon-pink);
}

.scan-line {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, var(--neon-cyan), transparent);
  animation: scan-line 4s linear infinite;
  opacity: 0.3;
}

@keyframes scan-line {
  0% { top: -1px; opacity: 0; }
  10% { opacity: 0.3; }
  90% { opacity: 0.3; }
  100% { top: 100%; opacity: 0; }
}

@keyframes pulse-glow {
  0%, 100% {
    filter: drop-shadow(0 0 5px currentColor);
  }
  50% {
    filter: drop-shadow(0 0 15px currentColor) drop-shadow(0 0 25px currentColor);
  }
}
</style>
