import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useAccountStore = defineStore('account', () => {
  // 账号信息
  const accountForm = ref({
    username: 'admin',
    email: 'admin@example.com',
    phone: '13800138000',
    gender: 'male',
    birthDate: '1990-01-01'
  })

  // 密码表单
  const passwordForm = ref({
    oldPassword: '',
    newPassword: '',
    confirmPassword: ''
  })

  // 保存账号信息
  const saveAccountInfo = () => {
    // 这里可以添加保存账号信息的逻辑
    localStorage.setItem('accountInfo', JSON.stringify(accountForm.value))
  }

  // 加载账号信息
  const loadAccountInfo = () => {
    const stored = localStorage.getItem('accountInfo')
    if (stored) {
      accountForm.value = JSON.parse(stored)
    }
  }

  // 修改密码
  const changePassword = () => {
    // 这里可以添加修改密码的逻辑
    // 实际应用中需要与后端API交互
    passwordForm.value = {
      oldPassword: '',
      newPassword: '',
      confirmPassword: ''
    }
    return true
  }

  return {
    // 状态
    accountForm,
    passwordForm,
    
    // 方法
    saveAccountInfo,
    loadAccountInfo,
    changePassword
  }
})