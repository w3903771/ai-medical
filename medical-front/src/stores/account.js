import { defineStore } from 'pinia'
import { ref } from 'vue'
import { useUserStore } from './user'

export const useAccountStore = defineStore('account', () => {
  const userStore = useUserStore()
  // 账号信息
  const accountForm = ref({
    username: '',
    email: '',
    phone: '13800138000',
    birthDate: '1990-01-01'
  })

  // 密码表单
  const passwordForm = ref({
    oldPassword: '',
    newPassword: '',
    confirmPassword: ''
  })

  // 保存账号信息（与后端对齐：username/email）
  const saveAccountInfo = async () => {
    await userStore.updateProfile({
      email: accountForm.value.email,
      username: accountForm.value.username,
      birthDate: accountForm.value.birthDate
    })
    // 仅本地保存扩展字段（phone）
    const localOnly = {
      phone: accountForm.value.phone
    }
    localStorage.setItem('accountInfo.extra', JSON.stringify(localOnly))
    return true
  }

  // 加载账号信息（优先使用后端资料）
  const loadAccountInfo = async () => {
    try {
      if (!userStore.userInfo.username) {
        await userStore.fetchProfile()
      }
      accountForm.value.username = userStore.userInfo.username || accountForm.value.username
      accountForm.value.email = userStore.userInfo.email || accountForm.value.email
      accountForm.value.birthDate = userStore.userInfo.birthDate || accountForm.value.birthDate
    } catch {}

    const storedExtra = localStorage.getItem('accountInfo.extra')
    if (storedExtra) {
      try {
        const extra = JSON.parse(storedExtra)
        accountForm.value.phone = extra.phone ?? accountForm.value.phone
      } catch {}
    }
  }

  // 修改密码（与后端交互）
  const changePassword = async () => {
    const ok = await userStore.changePassword({
      oldPassword: passwordForm.value.oldPassword,
      newPassword: passwordForm.value.newPassword
    })
    if (ok) {
      passwordForm.value = {
        oldPassword: '',
        newPassword: '',
        confirmPassword: ''
      }
    }
    return ok
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