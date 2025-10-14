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
  }

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
    
    // 初始化方法
    initSettings
  }
})