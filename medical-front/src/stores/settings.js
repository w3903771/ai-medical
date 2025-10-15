/**
 * 设置模块统一导出文件
 * 按功能领域拆分为多个独立的store
 */

// 导入各个功能领域的store
export { useAccountStore } from './account'
export { useModelStore } from './model'
export { useDataManagementStore } from './dataManagement'
export { useBackupStore } from './backup'
export { useSystemStore } from './system'
export { useExportStore } from './export'
export { useWebSearchStore } from './webSearch'
export { useDocProcessingStore } from './docProcessing'

// 为了保持向后兼容，提供原始的useSettingsStore
import { defineStore } from 'pinia'
import { useAccountStore } from './account'
import { useModelStore } from './model'
import { useDataManagementStore } from './dataManagement'
import { useBackupStore } from './backup'
import { useSystemStore } from './system'
import { useExportStore } from './export'
import { useWebSearchStore } from './webSearch'
import { useDocProcessingStore } from './docProcessing'

/**
 * 兼容原始的useSettingsStore
 * 聚合所有拆分后的store功能
 * 注意：建议在新代码中直接使用拆分后的专用store
 */
export const useSettingsStore = defineStore('settings', () => {
  const accountStore = useAccountStore()
  const modelStore = useModelStore()
  const dataStore = useDataManagementStore()
  const backupStore = useBackupStore()
  const systemStore = useSystemStore()
  const exportStore = useExportStore()
  const webSearchStore = useWebSearchStore()
  const docProcessingStore = useDocProcessingStore()

  // 初始化所有设置
  const initSettings = () => {
    modelStore.initModelSettings()
    systemStore.initSystemConfig()
    // 可选：加载各模块的持久化设置
    try { exportStore.loadExportSettings() } catch {}
    try { dataStore.loadDataSettings && dataStore.loadDataSettings() } catch {}
    try { backupStore.loadBackupSettings && backupStore.loadBackupSettings() } catch {}
    try { webSearchStore.loadSettings && webSearchStore.loadSettings() } catch {}
    try { docProcessingStore.loadSettings && docProcessingStore.loadSettings() } catch {}
  }

  // 模型：包装兼容方法
  const testApiConnection = async (provider) => {
    return modelStore.handleTestApi(provider)
  }

  const resetModelConfig = (providerOrId) => {
    const providers = modelStore.modelProviders
    const provider = typeof providerOrId === 'string'
      ? (Array.isArray(providers) ? providers.find(p => p.id === providerOrId) : providers.value?.find(p => p.id === providerOrId))
      : providerOrId
    if (provider) {
      modelStore.handleResetModelConfig(provider)
    }
  }

  // 系统：暴露保存与重置（重置为默认字段并应用主题）
  const saveSystemConfig = () => {
    systemStore.saveSystemConfig()
    // 立即应用主题以获得即时反馈
    systemStore.applyTheme()
  }

  const resetSystemConfig = () => {
    // 使用当前 store 的默认结构重置
    systemStore.systemConfig = {
      theme: 'light',
      language: 'zh-CN',
      fontSize: 'medium',
      notificationEnabled: true,
      autoLogout: 30,
      // 兼容视图中扩展字段（如存在则覆盖）
      autoUpdate: false,
      autoStart: false,
      minimizeToTray: false,
      proxyType: 'none',
      proxyHost: '',
      proxyPort: 0,
      proxyAuth: false,
      proxyUsername: '',
      proxyPassword: ''
    }
    systemStore.saveSystemConfig()
    systemStore.applyTheme()
  }

  // 数据管理：暴露方法
  const saveDataSettings = () => dataStore.saveDataSettings()
  const clearCache = () => dataStore.clearCache && dataStore.clearCache()
  const resetDataSettings = () => dataStore.resetDataSettings && dataStore.resetDataSettings()

  // 备份设置：暴露方法
  const saveBackupSettings = () => backupStore.saveBackupSettings && backupStore.saveBackupSettings()
  const loadBackupSettings = () => backupStore.loadBackupSettings && backupStore.loadBackupSettings()

  return {
    // 账号相关
    accountForm: accountStore.accountForm,
    passwordForm: accountStore.passwordForm,
    
    // 模型相关
    modelProviders: modelStore.modelProviders,
    saveModelProvidersToStorage: modelStore.saveModelProvidersToStorage,
    loadModelProvidersFromStorage: modelStore.loadModelProvidersFromStorage,
    handleModelStatusChange: modelStore.handleModelStatusChange,
    handleTestApi: modelStore.handleTestApi,
    handleResetModelConfig: modelStore.handleResetModelConfig,
    handleSaveModelConfig: modelStore.handleSaveModelConfig,
    saveModelConfigs: modelStore.saveModelProvidersToStorage, // 添加saveModelConfigs方法映射
    
    // 数据管理相关
    dataForm: dataStore.dataForm,
    storageInfo: dataStore.storageInfo,
    importForm: dataStore.importForm,
    exportForm: dataStore.exportForm,
    
    // 备份相关
    backupForm: backupStore.backupForm,
    backupList: backupStore.backupList,
    autoBackupSettings: backupStore.autoBackupSettings,

    // 系统配置相关
    systemConfig: systemStore.systemConfig,
    saveSystemConfig,
    resetSystemConfig,
    
    // 导出设置相关
    exportOptionsEnabled: exportStore.exportOptionsEnabled,
    markdownExportSettings: exportStore.markdownSettings,
    saveExportSettings: exportStore.saveExportSettings,
    loadExportSettings: exportStore.loadExportSettings,

    // 网络搜索相关
    webSearchProvider: webSearchStore.provider,
    webSearchApiKey: webSearchStore.apiKey,
    webSearchApiEndpoint: webSearchStore.apiEndpoint,
    webSearchIncludeDate: webSearchStore.includeDate,
    webSearchResultCount: webSearchStore.resultCount,
    saveWebSearchSettings: webSearchStore.saveSettings,
    loadWebSearchSettings: webSearchStore.loadSettings,
    testWebSearchApiKey: webSearchStore.testApiKey,

    // 文档处理相关
    ocrProvider: docProcessingStore.ocrProvider,
    ocrLanguages: docProcessingStore.ocrLanguages,
    ocrApiUrl: docProcessingStore.ocrApiUrl,
    ocrToken: docProcessingStore.ocrToken,
    docProvider: docProcessingStore.docProvider,
    docApiKey: docProcessingStore.docApiKey,
    docApiEndpoint: docProcessingStore.docApiEndpoint,
    saveDocProcessingSettings: docProcessingStore.saveSettings,
    loadDocProcessingSettings: docProcessingStore.loadSettings,

    // 数据管理方法
    saveDataSettings,
    clearCache,
    resetDataSettings,

    // 备份方法
    saveBackupSettings,
    loadBackupSettings,

    // 模型方法兼容映射
    testApiConnection,
    resetModelConfig,

    // 初始化方法
    initSettings
  }
})