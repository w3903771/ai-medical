import { defineStore } from 'pinia'
import { ref } from 'vue'
import request from '@/utils/request'
import router from '@/router'

export const useUserStore = defineStore('user', () => {
  // 用户信息
  const userInfo = ref({
    id: null,
    username: '',
    email: '',
    role: ''
  })
  
  // 登录状态
  const isLoggedIn = ref(false)
  
  // 设置用户信息
  const setUserInfo = (info) => {
    userInfo.value = info
    isLoggedIn.value = true
  }
  
  // 清除用户信息
  const clearUserInfo = () => {
    userInfo.value = {
      id: null,
      username: '',
      email: '',
      role: ''
    }
    isLoggedIn.value = false
    localStorage.removeItem('token')
  }
  
  // 初始化用户信息（从localStorage恢复）
  const initUserInfo = () => {
    const token = localStorage.getItem('token')
    if (token) {
      // 这里可以调用API验证token并获取用户信息
      isLoggedIn.value = true
    }
  }

  // 登录
  const login = async ({ username, password }) => {
    // 前端内置 Mock 管理员账号（无后端时使用）
    if (username === 'admin' && password === 'admin') {
      const mockToken = 'mock-admin-token'
      localStorage.setItem('token', mockToken)
      setUserInfo({ id: 1, username: 'admin', email: 'admin@example.com', role: 'admin' })
      return true
    }

    const res = await request.post('/auth/login', { username, password })
    // 约定返回：{ accessToken, refreshToken, user }
    const { accessToken, user } = res || {}
    if (!accessToken) throw new Error('登录响应缺少 accessToken')
    localStorage.setItem('token', accessToken)
    setUserInfo(user || { username })
    return true
  }

  // 注册
  const register = async ({ username, email, password }) => {
    const res = await request.post('/auth/register', { username, email, password })
    return !!res
  }

  // 登出
  const logout = () => {
    clearUserInfo()
    router.push('/login')
  }
  
  return {
    userInfo,
    isLoggedIn,
    setUserInfo,
    clearUserInfo,
    initUserInfo,
    login,
    register,
    logout
  }
})