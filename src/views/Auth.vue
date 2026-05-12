<template>
  <div class="auth-page">
    <!-- Background Layer - 深层背景 -->
    <div class="bg-layer">
      <!-- 柔和的大光源 -->
      <div class="ambient-glow glow-1"></div>
      <div class="ambient-glow glow-2"></div>
      <div class="ambient-glow glow-3"></div>

      <!-- 细微的噪点纹理 -->
      <div class="noise-overlay"></div>

      <!-- 动态渐变背景 -->
      <div class="gradient-bg"></div>
    </div>

    <!-- Left AI Vision Section -->
    <div class="left-section">
      <!-- 次要浮层卡片 - 中景 -->
      <div class="floating-card card-1">
        <div class="card-header">
          <span class="card-dot"></span>
          <span class="card-title">Quality Metrics</span>
        </div>
        <div class="card-body">
          <div class="metric-row">
            <span class="metric-label">测试覆盖率</span>
            <span class="metric-value primary">92%</span>
          </div>
          <div class="metric-bar">
            <div class="metric-fill" style="width: 92%"></div>
          </div>
        </div>
      </div>

      <div class="floating-card card-2">
        <div class="card-header">
          <span class="card-dot warning"></span>
          <span class="card-title">Risk Analysis</span>
        </div>
        <div class="card-body">
          <div class="metric-row">
            <span class="metric-label">Bug 趋势</span>
            <span class="metric-value success">Low</span>
          </div>
          <div class="mini-chart">
            <svg viewBox="0 0 100 30" preserveAspectRatio="none">
              <polyline
                points="0,25 15,20 30,22 45,15 60,18 75,10 90,8 100,5"
                fill="none"
                stroke="url(#chartGrad)"
                stroke-width="2"
                stroke-linecap="round"
              />
              <defs>
                <linearGradient id="chartGrad" x1="0%" y1="0%" x2="100%" y2="0%">
                  <stop offset="0%" stop-color="#5B8CFF"/>
                  <stop offset="100%" stop-color="#00D4FF"/>
                </linearGradient>
              </defs>
            </svg>
          </div>
        </div>
      </div>

      <div class="floating-card card-3">
        <div class="card-header">
          <span class="card-dot success"></span>
          <span class="card-title">Automation</span>
        </div>
        <div class="card-body">
          <div class="metric-row">
            <span class="metric-label">自动化率</span>
            <span class="metric-value primary">78%</span>
          </div>
          <div class="metric-bar">
            <div class="metric-fill success" style="width: 78%"></div>
          </div>
        </div>
      </div>

      <!-- 主内容区 -->
      <div class="left-content">
        <div class="eyebrow">AI Quality Operating System</div>
        <h1 class="main-title">智能驱动的新一代<br/>质量保障平台</h1>
        <p class="description">
          融合智能测试、风险分析与自动化执行，<br/>
          构建企业级 AI Quality Engineering 中台。
        </p>
      </div>

      <!-- 实时日志流 -->
      <!-- 日志粒子画布 -->
      <canvas id="log-particles" class="log-particles-canvas"></canvas>

      <div class="log-stream">
        <div class="log-label">Activity</div>
        <div class="log-list">
          <div class="log-item" v-for="(log, i) in displayedLogs" :key="i" :style="{ animationDelay: i * 0.1 + 's' }">
            <span class="log-indicator" :style="{ background: log.color, boxShadow: `0 0 6px ${log.color}80` }"></span>
            <span class="log-text" :style="{ color: log.color }">{{ log.text }}</span>
          </div>
        </div>
      </div>

      <!-- AI Network Canvas -->
      <canvas id="ai-network" class="ai-canvas"></canvas>
    </div>

    <!-- Right Login Section -->
    <div class="right-section">
      <!-- 登录卡片环境光 -->
      <div class="card-ambient-glow"></div>

      <div class="login-card">
        <!-- Logo -->
        <div class="logo-section">
          <div class="logo-icon">
            <svg viewBox="0 0 48 48" fill="none">
              <circle cx="24" cy="24" r="20" stroke="url(#logoGrad)" stroke-width="1.5" opacity="0.3"/>
              <circle cx="24" cy="24" r="12" stroke="url(#logoGrad)" stroke-width="1.5" opacity="0.5"/>
              <path d="M24 8L12 16l12 6 12-6-12-8z" fill="url(#logoGrad)"/>
              <path d="M12 28l12 6 12-6" stroke="url(#logoGrad)" stroke-width="1.5" stroke-linecap="round"/>
              <path d="M12 22l12 6 12-6" stroke="url(#logoGrad)" stroke-width="1.5" stroke-linecap="round"/>
              <defs>
                <linearGradient id="logoGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop offset="0%" stop-color="#5B8CFF"/>
                  <stop offset="50%" stop-color="#7C4DFF"/>
                  <stop offset="100%" stop-color="#00D4FF"/>
                </linearGradient>
              </defs>
            </svg>
          </div>
          <h2 class="logo-title">灵测 AI</h2>
          <p class="logo-subtitle">AI-Driven Quality Assurance</p>
        </div>

        <!-- 登录表单 -->
        <div v-if="mode === 'login'" class="form-section">
          <h3 class="form-title">Sign in</h3>
          <form @submit.prevent="handleLogin" class="auth-form">
            <div class="input-group">
              <div class="input-icon">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                  <circle cx="12" cy="8" r="4"/>
                  <path d="M4 20c0-4 4-6 8-6s8 2 8 6"/>
                </svg>
              </div>
              <input
                v-model="loginForm.username"
                type="text"
                placeholder="Username"
                :disabled="loading"
              />
            </div>
            <div class="input-group">
              <div class="input-icon">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                  <rect x="3" y="11" width="18" height="11" rx="2"/>
                  <path d="M7 11V7a5 5 0 0 1 10 0v4"/>
                </svg>
              </div>
              <input
                v-model="loginForm.password"
                :type="showPassword ? 'text' : 'password'"
                placeholder="Password"
                :disabled="loading"
              />
              <button
                class="toggle-password"
                type="button"
                @click="showPassword = !showPassword"
              >
                <svg v-if="!showPassword" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                  <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
                  <circle cx="12" cy="12" r="3"/>
                </svg>
                <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                  <path d="M17.94 17.94A10.5 10.5 0 0 1 12 20c-7 0-11-8-11-8a21 21 0 0 1 4-6"/>
                  <path d="M9.88 9.88a3 3 0 1 0 4.24 4.24"/>
                  <line x1="1" y1="1" x2="23" y2="23"/>
                </svg>
              </button>
            </div>
            <div v-if="error" class="error-message">
              <span class="error-text">{{ error }}</span>
            </div>
            <button type="submit" class="btn-login" :disabled="loading">
              <span v-if="loading" class="loading-spinner"></span>
              {{ loading ? 'Signing in...' : 'Continue' }}
            </button>
          </form>
          <div class="form-footer">
            <span>没有账号？</span>
            <a @click="mode = 'register'" href="javascript:void(0)">创建账号</a>
          </div>
        </div>

        <!-- 注册表单 -->
        <div v-else class="form-section">
          <h3 class="form-title">Create account</h3>
          <form @submit.prevent="handleRegister" class="auth-form">
            <div class="input-group">
              <div class="input-icon">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                  <circle cx="12" cy="8" r="4"/>
                  <path d="M4 20c0-4 4-6 8-6s8 2 8 6"/>
                </svg>
              </div>
              <input
                v-model="registerForm.username"
                type="text"
                placeholder="Username"
                :disabled="loading"
              />
            </div>
            <div class="input-group">
              <div class="input-icon">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                  <rect x="2" y="4" width="20" height="16" rx="2"/>
                  <path d="M22 6l-10 7L2 6"/>
                </svg>
              </div>
              <input
                v-model="registerForm.email"
                type="text"
                placeholder="Email"
                :disabled="loading"
              />
            </div>
            <div class="input-group">
              <div class="input-icon">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                  <rect x="3" y="11" width="18" height="11" rx="2"/>
                  <path d="M7 11V7a5 5 0 0 1 10 0v4"/>
                </svg>
              </div>
              <input
                v-model="registerForm.password"
                type="password"
                placeholder="Password (min 6 chars)"
                :disabled="loading"
              />
            </div>
            <div v-if="error" class="error-message">
              <span class="error-text">{{ error }}</span>
            </div>
            <button type="submit" class="btn-login" :disabled="loading">
              <span v-if="loading" class="loading-spinner"></span>
              {{ loading ? 'Creating...' : 'Create account' }}
            </button>
          </form>
          <div class="form-footer">
            <span>已有账号？</span>
            <a @click="mode = 'login'" href="javascript:void(0)">登录</a>
          </div>
        </div>

        <!-- 演示账号 -->
        <div class="demo-hint">
          <span>Demo account:</span>
          <code>admin / admin123</code>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const mode = ref('login')
const loading = ref(false)
const error = ref('')
const showPassword = ref(false)

const loginForm = ref({
  username: '',
  password: '',
  remember: false
})

const registerForm = ref({
  username: '',
  email: '',
  password: '',
  confirmPassword: ''
})

const logs = [
  { text: '回归测试已完成', color: 'rgba(82, 196, 26, 0.85)' },
  { text: 'AI 检测到异常', color: 'rgba(255, 77, 79, 0.85)' },
  { text: '覆盖率: 92%', color: 'rgba(91, 140, 255, 0.85)' },
  { text: '风险等级: 低', color: 'rgba(82, 196, 26, 0.85)' },
  { text: 'AI 推荐已生成', color: 'rgba(0, 212, 255, 0.85)' },
  { text: '自动化流程运行中', color: 'rgba(91, 140, 255, 0.85)' },
  { text: '测试套件已优化', color: 'rgba(124, 77, 255, 0.85)' }
]

const currentLogIndex = ref(0)
const displayedLogs = computed(() => {
  return [0, 1, 2].map(i => logs[(currentLogIndex.value + i) % logs.length])
})

let logInterval

async function handleLogin() {
  error.value = ''

  if (!loginForm.value.username.trim()) {
    error.value = '请输入用户名'
    return
  }

  if (!loginForm.value.password) {
    error.value = '请输入密码'
    return
  }

  loading.value = true

  try {
    const success = await authStore.login(loginForm.value.username, loginForm.value.password)
    if (success) {
      router.push('/')
    } else {
      error.value = authStore.error || '登录失败'
    }
  } catch (err) {
    error.value = err.message || '登录失败'
  } finally {
    loading.value = false
  }
}
async function handleRegister() {
  error.value = ''

  if (!registerForm.value.username.trim()) {
    error.value = '请输入用户名'
    return
  }

  if (!registerForm.value.email.trim()) {
    error.value = '请输入邮箱'
    return
  }

  // Email format validation
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  if (!emailRegex.test(registerForm.value.email)) {
    error.value = '请输入有效的邮箱地址'
    return
  }

  if (registerForm.value.password.length < 6) {
    error.value = '密码长度至少6位'
    return
  }

  loading.value = true

  try {
    const success = await authStore.register(
      registerForm.value.username,
      registerForm.value.email,
      registerForm.value.password
    )
    if (success) {
      router.push('/')
    } else {
      error.value = authStore.error || '注册失败'
    }
  } catch (err) {
    error.value = err.message || '注册失败'
  } finally {
    loading.value = false
  }
}
// AI Network Canvas - 更精致的节点网络
let canvas, ctx, nodes, animationId
let logCanvas, logCtx, logParticles

function initCanvas() {
  canvas = document.getElementById('ai-network')
  if (!canvas) return

  ctx = canvas.getContext('2d')
  resizeCanvas()

  nodes = []
  const nodeCount = 25
  for (let i = 0; i < nodeCount; i++) {
    nodes.push({
      x: Math.random() * canvas.width,
      y: Math.random() * canvas.height,
      vx: (Math.random() - 0.5) * 0.3,
      vy: (Math.random() - 0.5) * 0.3,
      radius: Math.random() * 2 + 1,
      pulsePhase: Math.random() * Math.PI * 2
    })
  }

  animate()
}

// 初始化日志粒子系统
function initLogParticles() {
  logCanvas = document.getElementById('log-particles')
  if (!logCanvas) return

  logCtx = logCanvas.getContext('2d')
  logCanvas.width = 300
  logCanvas.height = 150

  logParticles = []
  animateLogParticles()
}

function createLogParticle() {
  const colors = ['rgba(82, 196, 26, 0.6)', 'rgba(255, 77, 79, 0.6)', 'rgba(91, 140, 255, 0.6)', 'rgba(0, 212, 255, 0.6)', 'rgba(124, 77, 255, 0.6)']
  return {
    x: Math.random() * logCanvas.width,
    y: logCanvas.height + 10,
    vx: (Math.random() - 0.5) * 0.5,
    vy: -Math.random() * 1.5 - 0.5,
    radius: Math.random() * 2 + 0.5,
    color: colors[Math.floor(Math.random() * colors.length)],
    alpha: Math.random() * 0.5 + 0.3,
    life: 0
  }
}

function animateLogParticles() {
  if (!logCtx) return

  logCtx.clearRect(0, 0, logCanvas.width, logCanvas.height)

  // 添加新粒子
  if (Math.random() < 0.15) {
    logParticles.push(createLogParticle())
  }

  // 更新和绘制粒子
  logParticles = logParticles.filter(p => {
    p.x += p.vx
    p.y += p.vy
    p.life++

    // 渐隐
    const fadeAlpha = Math.max(0, p.alpha * (1 - p.life / 80))

    logCtx.beginPath()
    logCtx.fillStyle = p.color.replace('0.6', String(fadeAlpha))
    logCtx.arc(p.x, p.y, p.radius, 0, Math.PI * 2)
    logCtx.fill()

    // 发光效果
    logCtx.beginPath()
    const glow = logCtx.createRadialGradient(p.x, p.y, 0, p.x, p.y, p.radius * 3)
    glow.addColorStop(0, p.color.replace('0.6', String(fadeAlpha * 0.5)))
    glow.addColorStop(1, 'transparent')
    logCtx.fillStyle = glow
    logCtx.arc(p.x, p.y, p.radius * 3, 0, Math.PI * 2)
    logCtx.fill()

    return p.life < 80 && p.y > -10
  })

  requestAnimationFrame(animateLogParticles)
}

function resizeCanvas() {
  if (!canvas) return
  canvas.width = canvas.offsetWidth
  canvas.height = canvas.offsetHeight
}

function animate() {
  if (!ctx) return

  ctx.clearRect(0, 0, canvas.width, canvas.height)

  const time = Date.now() * 0.001

  // Draw connections - 更柔和的连线
  nodes.forEach((node, i) => {
    nodes.forEach((other, j) => {
      if (i >= j) return
      const dist = Math.hypot(node.x - other.x, node.y - other.y)
      if (dist < 180) {
        const alpha = 0.15 * (1 - dist / 180)
        ctx.beginPath()
        ctx.strokeStyle = `rgba(91, 140, 255, ${alpha})`
        ctx.lineWidth = 0.5
        ctx.moveTo(node.x, node.y)
        ctx.lineTo(other.x, other.y)
        ctx.stroke()
      }
    })
  })

  // Draw nodes
  nodes.forEach(node => {
    const pulse = Math.sin(time * 2 + node.pulsePhase) * 0.5 + 0.5

    // Outer glow
    ctx.beginPath()
    const gradient = ctx.createRadialGradient(
      node.x, node.y, 0,
      node.x, node.y, node.radius * 4
    )
    gradient.addColorStop(0, `rgba(91, 140, 255, ${0.15 * pulse})`)
    gradient.addColorStop(1, 'transparent')
    ctx.fillStyle = gradient
    ctx.arc(node.x, node.y, node.radius * 4, 0, Math.PI * 2)
    ctx.fill()

    // Core node
    ctx.beginPath()
    ctx.fillStyle = `rgba(255, 255, 255, ${0.6 + 0.4 * pulse})`
    ctx.arc(node.x, node.y, node.radius, 0, Math.PI * 2)
    ctx.fill()

    // Update position
    node.x += node.vx
    node.y += node.vy

    if (node.x < 0 || node.x > canvas.width) node.vx *= -1
    if (node.y < 0 || node.y > canvas.height) node.vy *= -1
  })

  animationId = requestAnimationFrame(animate)
}

onMounted(() => {
  if (authStore.isAuthenticated) {
    router.push('/')
  }

  initCanvas()
  initLogParticles()
  window.addEventListener('resize', resizeCanvas)

  logInterval = setInterval(() => {
    currentLogIndex.value = (currentLogIndex.value + 1) % logs.length
  }, 4000)
})

onUnmounted(() => {
  if (animationId) cancelAnimationFrame(animationId)
  window.removeEventListener('resize', resizeCanvas)
  if (logInterval) clearInterval(logInterval)
})
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

.auth-page {
  display: flex;
  min-height: 100vh;
  background: #09090B;
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
  position: relative;
  overflow: hidden;
}

/* ========== Background Layer ========== */
.bg-layer {
  position: fixed;
  inset: 0;
  z-index: 0;
  pointer-events: none;
}

.ambient-glow {
  position: absolute;
  border-radius: 50%;
  filter: blur(100px);
  opacity: 0.4;
}

.glow-1 {
  width: 700px;
  height: 700px;
  top: -250px;
  left: 15%;
  background: radial-gradient(circle, rgba(91, 140, 255, 0.35) 0%, transparent 70%);
  animation: glowFloat1 20s ease-in-out infinite;
}

.glow-2 {
  width: 600px;
  height: 600px;
  bottom: -200px;
  right: 25%;
  background: radial-gradient(circle, rgba(124, 77, 255, 0.3) 0%, transparent 70%);
  animation: glowFloat2 18s ease-in-out infinite;
}

.glow-3 {
  width: 500px;
  height: 500px;
  top: 50%;
  left: 55%;
  transform: translate(-50%, -50%);
  background: radial-gradient(circle, rgba(0, 212, 255, 0.2) 0%, transparent 70%);
  animation: glowFloat3 25s ease-in-out infinite;
}

@keyframes glowFloat1 {
  0%, 100% { transform: translate(0, 0) scale(1); opacity: 0.4; }
  33% { transform: translate(50px, 30px) scale(1.1); opacity: 0.5; }
  66% { transform: translate(-30px, 50px) scale(0.95); opacity: 0.35; }
}

@keyframes glowFloat2 {
  0%, 100% { transform: translate(0, 0) scale(1); }
  50% { transform: translate(-40px, -30px) scale(1.05); }
}

@keyframes glowFloat3 {
  0%, 100% { transform: translate(-50%, -50%) scale(1); }
  50% { transform: translate(-50%, -50%) scale(1.2); }
}

.noise-overlay {
  position: absolute;
  inset: 0;
  opacity: 0.035;
  background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)'/%3E%3C/svg%3E");
}

.gradient-bg {
  position: absolute;
  inset: 0;
  background:
    radial-gradient(ellipse 100% 60% at 15% 50%, rgba(91, 140, 255, 0.12) 0%, transparent 50%),
    radial-gradient(ellipse 80% 100% at 85% 40%, rgba(124, 77, 255, 0.1) 0%, transparent 50%),
    radial-gradient(ellipse 60% 80% at 50% 80%, rgba(0, 212, 255, 0.06) 0%, transparent 50%);
  animation: gradientFlow 30s ease-in-out infinite;
}

@keyframes gradientFlow {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.85; }
}

/* ========== Left Section ========== */
.left-section {
  flex: 0 0 58%;
  position: relative;
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding: 80px;
  z-index: 1;
}

.ai-canvas {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  opacity: 0.6;
}

/* 浮层卡片 - 中景层次 */
.floating-card {
  position: absolute;
  padding: 16px 20px;
  background: rgba(255, 255, 255, 0.025);
  backdrop-filter: blur(24px);
  border: 1px solid rgba(255, 255, 255, 0.05);
  border-radius: 14px;
  z-index: 2;
}

.card-1 {
  top: 18%;
  right: 12%;
  min-width: 180px;
  animation: cardFloat1 12s ease-in-out infinite;
}

.card-2 {
  top: 42%;
  right: 5%;
  min-width: 160px;
  animation: cardFloat2 15s ease-in-out infinite;
}

.card-3 {
  bottom: 22%;
  right: 18%;
  min-width: 150px;
  animation: cardFloat3 10s ease-in-out infinite;
}

@keyframes cardFloat1 {
  0%, 100% { transform: translateY(0) rotate(0deg) translateX(0); }
  25% { transform: translateY(-6px) rotate(0.5deg) translateX(3px); }
  50% { transform: translateY(-10px) rotate(-0.3deg) translateX(-2px); }
  75% { transform: translateY(-4px) rotate(0.2deg) translateX(2px); }
}

@keyframes cardFloat2 {
  0%, 100% { transform: translateY(0) rotate(0deg) translateX(0); }
  33% { transform: translateY(-8px) rotate(-0.8deg) translateX(-4px); }
  66% { transform: translateY(-14px) rotate(0.5deg) translateX(3px); }
}

@keyframes cardFloat3 {
  0%, 100% { transform: translateY(0) rotate(0deg) translateX(0); }
  50% { transform: translateY(-8px) rotate(0.6deg) translateX(-3px); }
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
}

.card-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #5B8CFF;
  box-shadow: 0 0 8px rgba(91, 140, 255, 0.6);
}

.card-dot.warning { background: #faad14; box-shadow: 0 0 8px rgba(250, 173, 20, 0.6); }
.card-dot.success { background: #52c41a; box-shadow: 0 0 8px rgba(82, 196, 26, 0.6); }

.card-title {
  font-size: 11px;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.5);
  text-transform: uppercase;
  letter-spacing: 0.08em;
}

.card-body {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.metric-row {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
}

.metric-label {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.6);
}

.metric-value {
  font-size: 18px;
  font-weight: 600;
  color: #5B8CFF;
}

.metric-value.primary { color: #5B8CFF; }
.metric-value.success { color: #52c41a; }

.metric-bar {
  height: 3px;
  background: rgba(255, 255, 255, 0.08);
  border-radius: 2px;
  overflow: hidden;
}

.metric-fill {
  height: 100%;
  background: linear-gradient(90deg, #5B8CFF, #7C4DFF);
  border-radius: 2px;
}

.metric-fill.success {
  background: linear-gradient(90deg, #52c41a, #73d13d);
}

.mini-chart {
  height: 30px;
}

.mini-chart svg {
  width: 100%;
  height: 100%;
}

/* 主内容区 */
.left-content {
  position: relative;
  z-index: 3;
  max-width: 540px;
}

.eyebrow {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 14px;
  margin-bottom: 28px;
  font-size: 11px;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.45);
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 20px;
  letter-spacing: 0.04em;
}

.eyebrow::before {
  content: '';
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: linear-gradient(135deg, #5B8CFF, #7C4DFF);
  box-shadow: 0 0 8px rgba(91, 140, 255, 0.5);
}

h1.main-title {
  font-size: 52px;
  font-weight: 500;
  margin: 0 0 28px 0;
  line-height: 1.08;
  letter-spacing: -0.035em;
  color: #FFFFFF;
  text-shadow: 0 0 40px rgba(184, 199, 255, 0.2);
  background: linear-gradient(180deg, #FFFFFF 0%, #B8C7FF 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.description {
  font-size: 17px;
  font-weight: 300;
  color: rgba(255, 255, 255, 0.45);
  margin: 0;
  line-height: 1.75;
}

/* 日志粒子效果 */
.log-particles-canvas {
  position: absolute;
  bottom: 60px;
  left: 60px;
  width: 300px;
  height: 150px;
  pointer-events: none;
  z-index: 2;
}

/* 日志流 */
.log-stream {
  position: absolute;
  bottom: 80px;
  left: 80px;
  z-index: 3;
}

.log-label {
  font-size: 10px;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.3);
  text-transform: uppercase;
  letter-spacing: 0.1em;
  margin-bottom: 12px;
}

.log-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.log-item {
  display: flex;
  align-items: center;
  gap: 10px;
  opacity: 0;
  animation: logFadeIn 0.5s ease forwards;
}

@keyframes logFadeIn {
  from { opacity: 0; transform: translateX(-8px); }
  to { opacity: 1; transform: translateX(0); }
}

.log-indicator {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: rgba(91, 140, 255, 0.6);
  box-shadow: 0 0 6px rgba(91, 140, 255, 0.4);
}

.log-text {
  color: rgba(255, 255, 255, 0.5);
  font-size: 12px;
  font-family: 'Inter', monospace;
}

/* Force override global input styles - highest priority */
.auth-page input,
.auth-page textarea,
.auth-form input,
.auth-form textarea {
  background: transparent !important;
  border: none !important;
  box-shadow: none !important;
  outline: none !important;
  -webkit-appearance: none !important;
  appearance: none !important;
}

* .input-group input,
* .input-group textarea {
  background: transparent !important;
  border: none !important;
  box-shadow: none !important;
  outline: none !important;
  -webkit-appearance: none !important;
  appearance: none !important;
}

/* ========== Right Section ========== */
.right-section {
  flex: 0 0 42%;
  display: flex;
  align-items: center;
  justify-content: flex-start;
  padding: 60px 80px 60px 60px;
  position: relative;
  z-index: 2;
}

.card-ambient-glow {
  position: absolute;
  width: 600px;
  height: 600px;
  left: -100px;
  top: 50%;
  transform: translateY(-50%);
  background: radial-gradient(circle, rgba(91, 140, 255, 0.15) 0%, rgba(124, 77, 255, 0.08) 40%, transparent 70%);
  filter: blur(80px);
  pointer-events: none;
  animation: ambientPulse 8s ease-in-out infinite;
}

@keyframes ambientPulse {
  0%, 100% { opacity: 0.8; transform: translateY(-50%) scale(1); }
  50% { opacity: 1; transform: translateY(-50%) scale(1.05); }
}

.login-card {
  width: 100%;
  max-width: 420px;
  padding: 48px;
  background: rgba(255, 255, 255, 0.025);
  backdrop-filter: blur(40px);
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 28px;
  box-shadow:
    0 0 0 1px rgba(255, 255, 255, 0.02),
    0 0 120px rgba(91, 140, 255, 0.08),
    0 4px 24px rgba(0, 0, 0, 0.4),
    0 16px 64px rgba(0, 0, 0, 0.25);
}

/* Logo */
.logo-section {
  text-align: center;
  margin-bottom: 44px;
}

.logo-icon {
  width: 48px;
  height: 48px;
  margin: 0 auto 14px;
  animation: logoPulse 5s ease-in-out infinite;
}

@keyframes logoPulse {
  0%, 100% {
    transform: scale(1);
    filter: drop-shadow(0 0 10px rgba(91, 140, 255, 0.35));
  }
  50% {
    transform: scale(1.03);
    filter: drop-shadow(0 0 20px rgba(91, 140, 255, 0.55));
  }
}

.logo-icon svg {
  width: 100%;
  height: 100%;
}

.logo-title {
  font-size: 20px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.95);
  margin: 0 0 6px 0;
  letter-spacing: -0.01em;
}

.logo-subtitle {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.35);
  margin: 0;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

/* Form */
.form-section {
  animation: formFadeIn 0.4s ease;
}

@keyframes formFadeIn {
  from { opacity: 0; transform: translateY(12px); }
  to { opacity: 1; transform: translateY(0); }
}

.form-title {
  font-size: 18px;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.9);
  margin: 0 0 28px 0;
  text-align: center;
}

.auth-form {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.input-group {
  position: relative;
  display: flex;
  align-items: center;
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
}

.input-group:focus-within {
  border-color: rgba(110, 168, 255, 0.6) !important;
  box-shadow:
    0 0 0 4px rgba(110, 168, 255, 0.12),
    0 0 30px rgba(110, 168, 255, 0.15),
    0 4px 20px rgba(0, 0, 0, 0.3);
  background: rgba(255, 255, 255, 0.08) !important;
}

.input-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 16px;
  color: rgba(255, 255, 255, 0.25);
  transition: color 0.25s;
}

.input-group:focus-within .input-icon {
  color: rgba(91, 140, 255, 0.8);
}

.input-icon svg {
  width: 18px;
  height: 18px;
}

.input-group input {
  flex: 1;
  height: 52px;
  padding: 14px 16px 14px 0;
  background: transparent;
  border: none !important;
  color: #fff;
  font-size: 15px;
  font-family: inherit;
  outline: none;
  transition: color 0.25s;
  -webkit-appearance: none;
  appearance: none;
}

.input-group input::placeholder {
  color: rgba(255, 255, 255, 0.2);
}

.input-group input:focus,
.input-group input:focus-visible,
.input-group input:focus-within {
  border-color: transparent !important;
  box-shadow: none !important;
  outline: none !important;
  -webkit-appearance: none !important;
  appearance: none !important;
}

/* 浏览器自动填充样式覆盖 */
.input-group input:-webkit-autofill,
.input-group input:-webkit-autofill:hover,
.input-group input:-webkit-autofill:focus,
.input-group input:-webkit-autofill:active {
  -webkit-box-shadow: 0 0 0 1000px #2b2c40 inset !important;
  -webkit-text-fill-color: #fff !important;
  background-color: #2b2c40 !important;
  transition: background-color 5000s ease-in-out 0s, box-shadow 5000s ease-in-out 0s;
}

.toggle-password {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 12px;
  background: none;
  border: none;
  color: rgba(255, 255, 255, 0.3);
  cursor: pointer;
  transition: color 0.25s;
}

.toggle-password:hover {
  color: rgba(91, 140, 255, 0.8);
}

.toggle-password svg {
  width: 18px;
  height: 18px;
}

.error-message {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 14px;
  background: rgba(15, 15, 20, 0.85);
  border: 1px solid rgba(255, 100, 100, 0.12);
  border-radius: 8px;
  color: rgba(255, 180, 180, 0.9);
  font-size: 13px;
  font-weight: 400;
  letter-spacing: 0.01em;
  backdrop-filter: blur(16px);
  box-shadow:
    0 0 0 1px rgba(255, 100, 100, 0.04),
    0 4px 16px rgba(0, 0, 0, 0.3),
    inset 0 0 20px rgba(255, 80, 80, 0.03);
  animation: errorFadeIn 0.25s cubic-bezier(0.4, 0, 0.2, 1);
}

@keyframes errorFadeIn {
  from {
    opacity: 0;
    transform: translateY(-4px) scale(0.98);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

.error-message .error-text {
  flex: 1;
  line-height: 1.4;
}

/* Button */
.btn-login {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 8px;
  height: 52px;
  padding: 0 28px;
  background: linear-gradient(135deg, #5B8CFF 0%, #6E5BFF 100%);
  color: white;
  border: none;
  border-radius: 12px;
  font-size: 15px;
  font-weight: 500;
  font-family: inherit;
  cursor: pointer;
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
  margin-top: 8px;
  box-shadow:
    inset 0 1px rgba(255, 255, 255, 0.15),
    inset 0 -1px rgba(0, 0, 0, 0.1),
    0 4px 12px rgba(91, 140, 255, 0.25);
}

.btn-login::before {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(180deg, rgba(255,255,255,0.12) 0%, transparent 50%);
  opacity: 0;
  transition: opacity 0.25s;
}

.btn-login::after {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,0.1), transparent);
  transition: left 0.6s;
}

.btn-login:hover {
  transform: translateY(-1px);
  box-shadow:
    inset 0 1px rgba(255, 255, 255, 0.2),
    inset 0 -1px rgba(0, 0, 0, 0.1),
    0 8px 24px rgba(91, 140, 255, 0.4);
}

.btn-login:hover::after {
  left: 100%;
}

.btn-login:hover::before {
  opacity: 1;
}

.btn-login:active {
  transform: translateY(0);
  box-shadow:
    inset 0 2px 4px rgba(0, 0, 0, 0.15),
    0 2px 8px rgba(91, 140, 255, 0.2);
}

.btn-login:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  pointer-events: none;
}

.loading-spinner {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.form-footer {
  margin-top: 24px;
  text-align: center;
  font-size: 13px;
  color: rgba(255, 255, 255, 0.4);
}

.form-footer a {
  color: rgba(91, 140, 255, 0.8);
  text-decoration: none;
  font-weight: 500;
  margin-left: 4px;
  transition: color 0.2s;
}

.form-footer a:hover {
  color: #7C4DFF;
}

.demo-hint {
  margin-top: 28px;
  padding-top: 24px;
  border-top: 1px solid rgba(255, 255, 255, 0.06);
  text-align: center;
  font-size: 12px;
  color: rgba(255, 255, 255, 0.3);
}

.demo-hint code {
  margin-left: 6px;
  padding: 2px 8px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 4px;
  font-family: 'SF Mono', 'Fira Code', monospace;
  color: rgba(255, 255, 255, 0.5);
}

/* ========== Responsive ========== */
@media (max-width: 1200px) {
  .floating-card {
    display: none;
  }
}

@media (max-width: 1024px) {
  .auth-page {
    flex-direction: column;
  }

  .left-section {
    flex: none;
    min-height: 45vh;
    padding: 60px 40px;
  }

  .main-title {
    font-size: 36px;
  }

  .eyebrow {
    font-size: 10px;
  }

  .log-stream {
    display: none;
  }

  .right-section {
    flex: none;
    padding: 40px;
  }

  .login-card {
    max-width: 100%;
    padding: 36px;
  }
}

@media (max-width: 640px) {
  .left-section {
    padding: 40px 24px;
  }

  .main-title {
    font-size: 28px;
  }

  .description {
    font-size: 14px;
  }

  .right-section {
    padding: 24px;
  }

  .login-card {
    padding: 28px 24px;
  }
}
</style>
