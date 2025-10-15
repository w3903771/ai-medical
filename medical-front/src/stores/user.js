import { defineStore } from 'pinia'
import { ref } from 'vue'
import request from '@/utils/request'
import router from '@/router'

export const useUserStore = defineStore('user', () => {
  // 用户信息
  const userInfo = ref({
    id: null,
    username: '',
    name: '',
    email: '',
    role: '',
    createdAt: '',
    lastLogin: '',
    birthDate: ''
  })
  
  // 登录状态
  const isLoggedIn = ref(false)
  
  // 设置用户信息
  const setUserInfo = (info) => {
    userInfo.value = {
      ...userInfo.value,
      ...info
    }
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
  const initUserInfo = async () => {
    const token = localStorage.getItem('token')
    if (!token) {
      isLoggedIn.value = false
      return
    }
    try {
      // 拉取用户资料以初始化（兼容包裹/非包裹响应）
      const profile = await request.get('/account/profile')
      if (profile && typeof profile === 'object') {
        setUserInfo({
          id: profile.id ?? userInfo.value.id,
          username: profile.username ?? userInfo.value.username,
          name: profile.name ?? userInfo.value.name,
          email: profile.email ?? userInfo.value.email,
          role: profile.role ?? userInfo.value.role,
          createdAt: profile.createdAt ?? userInfo.value.createdAt,
          lastLogin: profile.lastLogin ?? userInfo.value.lastLogin,
          birthDate: profile.birthDate ?? userInfo.value.birthDate,
        })
      } else {
        isLoggedIn.value = true
      }
    } catch (e) {
      // token 失效时清理并回到登录
      clearUserInfo()
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
    // 按 api.md：{ token, expiresIn, user }
    const { token, user } = res || {}
    if (!token) throw new Error('登录响应缺少 token')
    localStorage.setItem('token', token)
    setUserInfo(user || { username })
    return true
  }

  // 注册
  const register = async ({ username, email, password }) => {
    const res = await request.post('/auth/register', { username, email, password })
    // 返回 { id, username } 或包裹数据
    return !!res
  }

  // 拉取用户资料（手动触发）
  const fetchProfile = async () => {
    const profile = await request.get('/account/profile')
    if (profile && typeof profile === 'object') {
      setUserInfo({
        id: profile.id,
        username: profile.username,
        name: profile.name ?? '',
        email: profile.email ?? '',
        role: profile.role ?? '',
        createdAt: profile.createdAt ?? '',
        lastLogin: profile.lastLogin ?? '',
        birthDate: profile.birthDate ?? ''
      })
    }
    return profile
  }

  // 更新用户资料（仅允许 email/username）
  const updateProfile = async ({ email, username, birthDate }) => {
    const payload = {}
    if (typeof email === 'string') payload.email = email
    if (typeof username === 'string') payload.username = username
    if (typeof birthDate === 'string') payload.birthDate = birthDate
    const res = await request.put('/account/profile', payload)
    // 成功后刷新本地资料
    await fetchProfile()
    return !!res
  }

  // 修改密码
  const changePassword = async ({ oldPassword, newPassword }) => {
    const res = await request.put('/account/password', { oldPassword, newPassword })
    return !!res
  }

  // 登出：调用后端并清理本地状态
  const logout = async () => {
    try {
      await request.post('/auth/logout')
    } catch (e) {
      // 后端无状态登出，失败也不影响前端清理
    }
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
    fetchProfile,
    updateProfile,
    changePassword,
    logout
  }
})