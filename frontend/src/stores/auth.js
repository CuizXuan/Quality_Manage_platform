// Phase 4 - 认证状态管理
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

const API_BASE = '/api/auth'

export const useAuthStore = defineStore('auth', () => {
  // State
  const accessToken = ref(localStorage.getItem('access_token') || null)
  const refreshToken = ref(localStorage.getItem('refresh_token') || null)
  const user = ref(null)
  const loading = ref(false)
  const error = ref(null)

  // Getters
  const isAuthenticated = computed(() => !!accessToken.value)
  const isAdmin = computed(() => {
    if (!user.value) return false
    return user.value.roles?.includes('SuperAdmin') || 
           user.value.roles?.includes('TenantAdmin')
  })
  const currentUsername = computed(() => user.value?.username || '')

  // Actions
  async function login(username, password) {
    loading.value = true
    error.value = null
    try {
      const response = await fetch(`${API_BASE}/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ username, password })
      })
      
      if (!response.ok) {
        const data = await response.json()
        throw new Error(data.detail || '登录失败')
      }
      
      const data = await response.json()
      accessToken.value = data.access_token
      refreshToken.value = data.refresh_token
      
      // 存储到 localStorage
      localStorage.setItem('access_token', data.access_token)
      localStorage.setItem('refresh_token', data.refresh_token)
      
      // 获取用户信息
      await fetchUserInfo()
      
      return true
    } catch (err) {
      error.value = err.message
      return false
    } finally {
      loading.value = false
    }
  }

  async function register(username, email, password) {
    loading.value = true
    error.value = null
    try {
      const response = await fetch(`${API_BASE}/register`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ username, email, password })
      })
      
      if (!response.ok) {
        const data = await response.json()
        throw new Error(data.detail || '注册失败')
      }
      
      const data = await response.json()
      accessToken.value = data.access_token
      refreshToken.value = data.refresh_token
      
      // 存储到 localStorage
      localStorage.setItem('access_token', data.access_token)
      localStorage.setItem('refresh_token', data.refresh_token)
      
      // 获取用户信息
      await fetchUserInfo()
      
      return true
    } catch (err) {
      error.value = err.message
      return false
    } finally {
      loading.value = false
    }
  }

  async function fetchUserInfo() {
    if (!accessToken.value) return null
    
    try {
      const response = await fetch(`${API_BASE}/me`, {
        headers: {
          'Authorization': `Bearer ${accessToken.value}`
        }
      })
      
      if (!response.ok) {
        if (response.status === 401) {
          // Token 过期，尝试刷新
          await refreshAccessToken()
          if (accessToken.value) {
            return fetchUserInfo()
          }
        }
        throw new Error('获取用户信息失败')
      }
      
      user.value = await response.json()
      return user.value
    } catch (err) {
      error.value = err.message
      return null
    }
  }

  async function refreshAccessToken() {
    if (!refreshToken.value) return false
    
    try {
      const response = await fetch(`${API_BASE}/refresh`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ refresh_token: refreshToken.value })
      })
      
      if (!response.ok) {
        throw new Error('刷新令牌失败')
      }
      
      const data = await response.json()
      accessToken.value = data.access_token
      localStorage.setItem('access_token', data.access_token)
      return true
    } catch (err) {
      error.value = err.message
      logout()
      return false
    }
  }

  function logout() {
    accessToken.value = null
    refreshToken.value = null
    user.value = null
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
  }

  // 初始化时获取用户信息
  if (accessToken.value) {
    fetchUserInfo()
  }

  return {
    // State
    accessToken,
    refreshToken,
    user,
    loading,
    error,
    // Getters
    isAuthenticated,
    isAdmin,
    currentUsername,
    // Actions
    login,
    register,
    logout,
    fetchUserInfo,
    refreshAccessToken
  }
})
