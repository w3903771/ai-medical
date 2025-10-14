import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useDataManagementStore = defineStore('dataManagement', () => {
  // 数据管理
  const dataForm = ref({
    storagePath: 'C:/Users/Default/AppData/Local/MedicalAssistant/Data',
    // 以下为新增展示用路径
    logPath: 'C:/Users/Default/AppData/Local/MedicalAssistant/Logs',
    kbPath: 'C:/Users/Default/AppData/Local/MedicalAssistant/KnowledgeBase',
    // 旧的自动清理相关字段不再用于UI，但保留数据结构兼容
    autoCleanup: true,
    cleanupPeriod: 'monthly',
    retentionDays: 90
  })

  const storageInfo = ref({
    totalSpace: 100,
    usedSpace: 23.5,
    availableSpace: 76.5,
    usagePercentage: 23.5,
    // 新增：缓存大小展示（MB）
    cacheSizeMB: 128.4
  })

  const importForm = ref({
    fileList: []
  })

  const exportForm = ref({
    dataTypes: [],
    dateRange: null
  })

  // 保存数据管理设置
  const saveDataSettings = () => {
    localStorage.setItem('dataSettings', JSON.stringify(dataForm.value))
  }

  // 加载数据管理设置
  const loadDataSettings = () => {
    const stored = localStorage.getItem('dataSettings')
    if (stored) {
      dataForm.value = JSON.parse(stored)
    }
  }

  // 更新存储信息
  const updateStorageInfo = () => {
    // 这里可以添加获取实际存储信息的逻辑
    // 模拟更新存储信息
    storageInfo.value = {
      totalSpace: 100,
      usedSpace: Math.random() * 50,
      availableSpace: 0,
      usagePercentage: 0
    }
    
    storageInfo.value.availableSpace = storageInfo.value.totalSpace - storageInfo.value.usedSpace
    storageInfo.value.usagePercentage = (storageInfo.value.usedSpace / storageInfo.value.totalSpace) * 100
  }

  // 清除缓存（示例实现）
  const clearCache = () => {
    try {
      localStorage.removeItem('cacheData')
    } catch (e) {
      // 忽略本地不存在的缓存键
    }
    storageInfo.value.cacheSizeMB = 0
    return true
  }

  // 重置数据管理设置为默认
  const resetDataSettings = () => {
    dataForm.value = {
      storagePath: 'C:/Users/Default/AppData/Local/MedicalAssistant/Data',
      logPath: 'C:/Users/Default/AppData/Local/MedicalAssistant/Logs',
      kbPath: 'C:/Users/Default/AppData/Local/MedicalAssistant/KnowledgeBase',
      autoCleanup: true,
      cleanupPeriod: 'monthly',
      retentionDays: 90
    }
    saveDataSettings()
  }

  // 导入数据
  const importData = () => {
    // 这里可以添加导入数据的逻辑
    importForm.value.fileList = []
    return true
  }

  // 导出数据
  const exportData = () => {
    // 这里可以添加导出数据的逻辑
    return true
  }

  return {
    // 状态
    dataForm,
    storageInfo,
    importForm,
    exportForm,
    
    // 方法
    saveDataSettings,
    loadDataSettings,
    updateStorageInfo,
    importData,
    exportData,
    clearCache,
    resetDataSettings
  }
})