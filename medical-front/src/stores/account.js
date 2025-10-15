import { defineStore } from 'pinia'
import { ref } from 'vue'
import { useUserStore } from './user'

// For account info management in settings
export const useAccountStore = defineStore('account', () => {
  const userStore = useUserStore()
  // 账号信息
  const accountForm = ref({
    username: '',
    name: '',
    email: '',
    role: '',
    gender: null,
    birthDate: ''
  })

  // 密码表单
  const passwordForm = ref({
    oldPassword: '',
    newPassword: '',
    confirmPassword: ''
  })

  // 保存账号信息（与后端对齐：email/name/gender/birthDate）
  const saveAccountInfo = async () => {
    try {
      const ok = await userStore.updateProfile({
        email: accountForm.value.email,
        name: accountForm.value.name,
        gender: accountForm.value.gender,
        birthDate: accountForm.value.birthDate
      })
      return ok
    } catch {
      return false
    }
  }

  // 加载账号信息（优先使用后端资料）
  const loadAccountInfo = async () => {
    try {
      if (!userStore.userInfo.username) {
        await userStore.fetchProfile()
      }
      accountForm.value.username = userStore.userInfo.username || accountForm.value.username
      accountForm.value.name = userStore.userInfo.name || accountForm.value.name
      accountForm.value.email = userStore.userInfo.email || accountForm.value.email
      accountForm.value.role = userStore.userInfo.role || accountForm.value.role
      accountForm.value.gender = (userStore.userInfo.gender ?? accountForm.value.gender)
      accountForm.value.birthDate = userStore.userInfo.birthDate || accountForm.value.birthDate
    } catch {}
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