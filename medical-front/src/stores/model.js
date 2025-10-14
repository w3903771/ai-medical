import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useModelStore = defineStore('model', () => {
  // 模型服务提供商
  const modelProviders = ref([
    {
      id: 'github-copilot',
      name: 'GitHub Copilot',
      enabled: false,
      apiKey: '',
      hasCustomEndpoint: false,
      selectedModels: ['copilot'], // 根据默认enabled状态初始化
      models: [
        { id: 'copilot', name: 'Copilot', description: '代码智能补全和生成', enabled: true }
      ]
    },
    {
      id: 'silicon-flow',
      name: '硅基流动',
      enabled: false,
      apiKey: '',
      hasCustomEndpoint: true,
      apiUrl: 'https://api.silicon-flow.com/v1',
      selectedModels: ['silicon-1'], // 根据默认enabled状态初始化
      models: [
        { id: 'silicon-1', name: 'Silicon-1', description: '通用大语言模型', enabled: true },
        { id: 'silicon-pro', name: 'Silicon-Pro', description: '高级专业模型', enabled: false }
      ]
    },
    {
      id: 'ollama',
      name: 'Ollama',
      enabled: false,
      apiKey: '',
      hasCustomEndpoint: true,
      apiUrl: 'http://localhost:11434/api',
      selectedModels: ['llama3'], // 根据默认enabled状态初始化
      models: [
        { id: 'llama3', name: 'Llama 3', description: '开源大语言模型', enabled: true },
        { id: 'mistral', name: 'Mistral', description: '高性能开源模型', enabled: false },
        { id: 'vicuna', name: 'Vicuna', description: '对话型AI助手', enabled: false }
      ]
    },
    {
      id: 'gemini',
      name: 'Gemini',
      enabled: false,
      apiKey: '',
      hasCustomEndpoint: false,
      selectedModels: ['gemini-pro'], // 根据默认enabled状态初始化
      models: [
        { id: 'gemini-pro', name: 'Gemini Pro', description: '通用大语言模型', enabled: true },
        { id: 'gemini-ultra', name: 'Gemini Ultra', description: '高级多模态模型', enabled: false }
      ]
    },
    {
      id: 'alibaba',
      name: '阿里云百炼',
      enabled: false,
      apiKey: '',
      hasCustomEndpoint: true,
      apiUrl: 'https://dashscope.aliyuncs.com/api/v1',
      selectedModels: ['qwen'], // 根据默认enabled状态初始化
      models: [
        { id: 'qwen', name: '通义千问', description: '阿里云大语言模型', enabled: true }
      ]
    },
    {
      id: 'volcengine',
      name: '火山引擎',
      enabled: false,
      apiKey: '',
      hasCustomEndpoint: true,
      apiUrl: 'https://api.volcengine.com/v1',
      selectedModels: ['skylark'], // 根据默认enabled状态初始化
      models: [
        { id: 'skylark', name: '云雀大模型', description: '火山引擎大语言模型', enabled: true }
      ]
    }
  ])

  // 保存模型提供商配置到本地存储
  const saveModelProvidersToStorage = () => {
    localStorage.setItem('modelProviders', JSON.stringify(modelProviders.value))
  }

  // 从本地存储加载模型提供商配置
  const loadModelProvidersFromStorage = () => {
    const stored = localStorage.getItem('modelProviders')
    if (stored) {
      const loadedProviders = JSON.parse(stored)
      // 确保每个provider都有selectedModels字段
      loadedProviders.forEach(provider => {
        if (!provider.selectedModels) {
          // 如果没有selectedModels字段，根据models的enabled状态初始化
          provider.selectedModels = provider.models
            .filter(model => model.enabled)
            .map(model => model.id)
        }
      })
      modelProviders.value = loadedProviders
    }
  }

  // 处理模型状态变更
  const handleModelStatusChange = (provider) => {
    saveModelProvidersToStorage()
  }

  // 测试API连接
  const handleTestApi = async (provider) => {
    if (!provider.apiKey) {
      return false
    }
    
    // 模拟API测试
    await new Promise(resolve => setTimeout(resolve, 1500))
    return true
  }

  // 重置模型配置
  const handleResetModelConfig = (provider) => {
    // 根据不同提供商设置默认值
    switch (provider.id) {
      case 'ollama':
        provider.apiUrl = 'http://localhost:11434/api'
        break
      case 'silicon-flow':
        provider.apiUrl = 'https://api.silicon-flow.com/v1'
        break
      case 'alibaba':
        provider.apiUrl = 'https://dashscope.aliyuncs.com/api/v1'
        break
      case 'volcengine':
        provider.apiUrl = 'https://api.volcengine.com/v1'
        break
    }
    
    provider.apiKey = ''
    provider.models.forEach(model => {
      // 重置为默认启用状态
      if (['copilot', 'silicon-1', 'llama3', 'gemini-pro', 'qwen', 'skylark'].includes(model.id)) {
        model.enabled = true
      } else {
        model.enabled = false
      }
    })
  }

  // 保存模型配置
  const handleSaveModelConfig = (provider) => {
    saveModelProvidersToStorage()
  }

  // 初始化
  const initModelSettings = () => {
    loadModelProvidersFromStorage()
  }

  return {
    // 状态
    modelProviders,
    
    // 方法
    saveModelProvidersToStorage,
    loadModelProvidersFromStorage,
    handleModelStatusChange,
    handleTestApi,
    handleResetModelConfig,
    handleSaveModelConfig,
    initModelSettings
  }
})