import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useBackupStore = defineStore('backup', () => {
  // 备份设置
  const backupForm = ref({
    autoBackup: false,
    frequency: 'daily',
    time: new Date(2023, 0, 1, 3, 0),
    dayOfWeek: '1',
    dayOfMonth: 1,
    keepCount: 5,
    path: 'C:/Users/Default/AppData/Local/MedicalAssistant/Backups'
  })

  // 备份列表
  const backupList = ref([
    {
      id: 1,
      name: '自动备份_20240101',
      createTime: '2024-01-01 00:00:00',
      size: '125.6 MB',
      type: 'auto'
    },
    {
      id: 2,
      name: '手动备份_20240115',
      createTime: '2024-01-15 15:30:00',
      size: '130.2 MB',
      type: 'manual'
    }
  ])

  const autoBackupSettings = ref({
    enabled: true,
    frequency: 'daily',
    time: '03:00',
    keepDays: 30
  })

  // 保存备份设置
  const saveBackupSettings = () => {
    localStorage.setItem('backupSettings', JSON.stringify(backupForm.value))
    localStorage.setItem('autoBackupSettings', JSON.stringify(autoBackupSettings.value))
  }

  // 加载备份设置
  const loadBackupSettings = () => {
    const storedBackup = localStorage.getItem('backupSettings')
    if (storedBackup) {
      backupForm.value = JSON.parse(storedBackup)
    }

    const storedAutoBackup = localStorage.getItem('autoBackupSettings')
    if (storedAutoBackup) {
      autoBackupSettings.value = JSON.parse(storedAutoBackup)
    }
  }

  // 创建备份
  const createBackup = () => {
    // 这里可以添加创建备份的逻辑
    const newBackup = {
      id: backupList.value.length + 1,
      name: `手动备份_${new Date().toISOString().slice(0, 10).replace(/-/g, '')}`,
      createTime: new Date().toLocaleString(),
      size: `${(Math.random() * 50 + 100).toFixed(1)} MB`,
      type: 'manual'
    }
    
    backupList.value.push(newBackup)
    return true
  }

  // 恢复备份
  const restoreBackup = (backupId) => {
    // 这里可以添加恢复备份的逻辑
    return true
  }

  // 删除备份
  const deleteBackup = (backupId) => {
    // 这里可以添加删除备份的逻辑
    backupList.value = backupList.value.filter(backup => backup.id !== backupId)
    return true
  }

  return {
    // 状态
    backupForm,
    backupList,
    autoBackupSettings,
    
    // 方法
    saveBackupSettings,
    loadBackupSettings,
    createBackup,
    restoreBackup,
    deleteBackup
  }
})