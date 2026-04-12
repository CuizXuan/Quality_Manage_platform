<template>
  <div class="auth-container">
    <div class="auth-card">
      <!-- Logo -->
      <div class="logo-section">
        <h1 class="logo-title">质量保障平台</h1>
        <p class="logo-subtitle">API Debug Tool - Phase 4</p>
      </div>

      <!-- 登录表单 -->
      <div v-if="mode === 'login'" class="form-section">
        <h2 class="form-title">登录</h2>
        <form @submit.prevent="handleLogin" class="auth-form">
          <div class="form-group">
            <label for="login-username">用户名</label>
            <input
              id="login-username"
              v-model="loginForm.username"
              type="text"
              placeholder="请输入用户名"
              required
              :disabled="loading"
            />
          </div>
          <div class="form-group">
            <label for="login-password">密码</label>
            <input
              id="login-password"
              v-model="loginForm.password"
              type="password"
              placeholder="请输入密码"
              required
              :disabled="loading"
            />
          </div>
          <div class="form-group checkbox-group">
            <label>
              <input v-model="loginForm.remember" type="checkbox" />
              记住我
            </label>
          </div>
          <div v-if="error" class="error-message">{{ error }}</div>
          <button type="submit" class="btn-primary" :disabled="loading">
            <span v-if="loading" class="loading-spinner"></span>
            {{ loading ? '登录中...' : '登录' }}
          </button>
        </form>
        <div class="form-footer">
          <span>还没有账号？</span>
          <a @click="mode = 'register'" href="javascript:void(0)">立即注册</a>
        </div>
      </div>

      <!-- 注册表单 -->
      <div v-else class="form-section">
        <h2 class="form-title">注册</h2>
        <form @submit.prevent="handleRegister" class="auth-form">
          <div class="form-group">
            <label for="reg-username">用户名</label>
            <input
              id="reg-username"
              v-model="registerForm.username"
              type="text"
              placeholder="请输入用户名"
              required
              :disabled="loading"
              minlength="3"
              maxlength="50"
            />
          </div>
          <div class="form-group">
            <label for="reg-email">邮箱</label>
            <input
              id="reg-email"
              v-model="registerForm.email"
              type="email"
              placeholder="请输入邮箱"
              required
              :disabled="loading"
            />
          </div>
          <div class="form-group">
            <label for="reg-password">密码</label>
            <input
              id="reg-password"
              v-model="registerForm.password"
              type="password"
              placeholder="请输入密码（至少6位）"
              required
              :disabled="loading"
              minlength="6"
            />
            <div class="password-strength" v-if="registerForm.password">
              <div class="strength-bar" :class="passwordStrength.class">
                <div class="strength-fill" :style="{ width: passwordStrength.width }"></div>
              </div>
              <span class="strength-text">{{ passwordStrength.text }}</span>
            </div>
          </div>
          <div class="form-group">
            <label for="reg-confirm">确认密码</label>
            <input
              id="reg-confirm"
              v-model="registerForm.confirmPassword"
              type="password"
              placeholder="请再次输入密码"
              required
              :disabled="loading"
            />
            <span v-if="registerForm.confirmPassword && registerForm.password !== registerForm.confirmPassword" class="field-error">
              两次输入的密码不一致
            </span>
          </div>
          <div v-if="error" class="error-message">{{ error }}</div>
          <button 
            type="submit" 
            class="btn-primary" 
            :disabled="loading || (registerForm.password !== registerForm.confirmPassword)"
          >
            <span v-if="loading" class="loading-spinner"></span>
            {{ loading ? '注册中...' : '注册' }}
          </button>
        </form>
        <div class="form-footer">
          <span>已有账号？</span>
          <a @click="mode = 'login'" href="javascript:void(0)">立即登录</a>
        </div>
      </div>

      <!-- 演示账号提示 -->
      <div class="demo-hint">
        <p>演示账号：admin / admin123</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const mode = ref('login')
const loading = ref(false)
const error = ref('')

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

// 密码强度计算
const passwordStrength = computed(() => {
  const pwd = registerForm.value.password
  if (!pwd) return { class: '', width: '0%', text: '' }
  
  let strength = 0
  if (pwd.length >= 6) strength++
  if (pwd.length >= 8) strength++
  if (/[a-z]/.test(pwd) && /[A-Z]/.test(pwd)) strength++
  if (/\d/.test(pwd)) strength++
  if (/[^a-zA-Z0-9]/.test(pwd)) strength++
  
  if (strength <= 2) return { class: 'weak', width: '33%', text: '弱' }
  if (strength <= 3) return { class: 'medium', width: '66%', text: '中等' }
  return { class: 'strong', width: '100%', text: '强' }
})

async function handleLogin() {
  error.value = ''
  loading.value = true
  
  const success = await authStore.login(loginForm.value.username, loginForm.value.password)
  
  if (success) {
    router.push('/')
  } else {
    error.value = authStore.error || '登录失败'
  }
  
  loading.value = false
}

async function handleRegister() {
  error.value = ''
  
  if (registerForm.value.password !== registerForm.value.confirmPassword) {
    error.value = '两次输入的密码不一致'
    return
  }
  
  if (registerForm.value.password.length < 6) {
    error.value = '密码长度至少6位'
    return
  }
  
  loading.value = true
  
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
  
  loading.value = false
}

onMounted(() => {
  // 如果已登录，直接跳转
  if (authStore.isAuthenticated) {
    router.push('/')
  }
})
</script>

<style scoped>
.auth-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

.auth-card {
  background: white;
  border-radius: 16px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  padding: 40px;
  width: 100%;
  max-width: 420px;
}

.logo-section {
  text-align: center;
  margin-bottom: 32px;
}

.logo-title {
  font-size: 28px;
  font-weight: 700;
  color: #333;
  margin: 0 0 8px 0;
}

.logo-subtitle {
  font-size: 14px;
  color: #666;
  margin: 0;
}

.form-section {
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.form-title {
  font-size: 24px;
  font-weight: 600;
  color: #333;
  margin: 0 0 24px 0;
  text-align: center;
}

.auth-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.form-group label {
  font-size: 14px;
  font-weight: 500;
  color: #555;
}

.form-group input[type="text"],
.form-group input[type="email"],
.form-group input[type="password"] {
  padding: 12px 16px;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 14px;
  transition: border-color 0.2s, box-shadow 0.2s;
}

.form-group input:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.form-group input:disabled {
  background: #f5f5f5;
  cursor: not-allowed;
}

.checkbox-group label {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  font-weight: 400;
}

.checkbox-group input[type="checkbox"] {
  width: 16px;
  height: 16px;
  cursor: pointer;
}

.password-strength {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 4px;
}

.strength-bar {
  flex: 1;
  height: 4px;
  background: #e0e0e0;
  border-radius: 2px;
  overflow: hidden;
}

.strength-fill {
  height: 100%;
  transition: width 0.3s, background-color 0.3s;
}

.strength-bar.weak .strength-fill {
  background: #ff4d4f;
}

.strength-bar.medium .strength-fill {
  background: #faad14;
}

.strength-bar.strong .strength-fill {
  background: #52c41a;
}

.strength-text {
  font-size: 12px;
  color: #888;
  min-width: 30px;
}

.field-error {
  font-size: 12px;
  color: #ff4d4f;
}

.error-message {
  padding: 10px 14px;
  background: #fff2f0;
  border: 1px solid #ffccc7;
  border-radius: 6px;
  color: #ff4d4f;
  font-size: 14px;
}

.btn-primary {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 8px;
  padding: 14px 24px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
}

.btn-primary:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(102, 126, 234, 0.4);
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.loading-spinner {
  width: 18px;
  height: 18px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.form-footer {
  margin-top: 20px;
  text-align: center;
  font-size: 14px;
  color: #666;
}

.form-footer a {
  color: #667eea;
  text-decoration: none;
  font-weight: 500;
  margin-left: 4px;
}

.form-footer a:hover {
  text-decoration: underline;
}

.demo-hint {
  margin-top: 24px;
  padding-top: 20px;
  border-top: 1px solid #eee;
  text-align: center;
}

.demo-hint p {
  margin: 0;
  font-size: 13px;
  color: #999;
}
</style>
