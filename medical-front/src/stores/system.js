import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useSystemStore = defineStore('system', () => {
  // 系统配置
  const systemConfig = ref({
    theme: 'light',
    language: 'zh-CN',
    fontSize: 'medium',
    notificationEnabled: true,
    autoLogout: 30
  })

  // 保存系统配置
  const saveSystemConfig = () => {
    localStorage.setItem('systemConfig', JSON.stringify(systemConfig.value))
  }

  // 加载系统配置
  const loadSystemConfig = () => {
    const stored = localStorage.getItem('systemConfig')
    if (stored) {
      systemConfig.value = JSON.parse(stored)
    }
  }

  // 切换主题
  const toggleTheme = () => {
    systemConfig.value.theme = systemConfig.value.theme === 'light' ? 'dark' : 'light'
    saveSystemConfig()
    applyTheme()
  }

  // 应用主题
  const applyTheme = () => {
    document.documentElement.setAttribute('data-theme', systemConfig.value.theme)
  }

  // 设置语言
  const setLanguage = (lang) => {
    systemConfig.value.language = lang
    saveSystemConfig()
  }

  // 初始化系统配置
  const initSystemConfig = () => {
    loadSystemConfig()
    applyTheme()
  }

  return {
    // 状态
    systemConfig,
    
    // 方法
    saveSystemConfig,
    loadSystemConfig,
    toggleTheme,
    applyTheme,
    setLanguage,
    initSystemConfig
  }
})