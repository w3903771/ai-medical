import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useWebSearchStore = defineStore('webSearch', () => {
  const provider = ref('tavily') // tavily | google | bing | baidu
  const apiKey = ref('')
  const apiEndpoint = ref('https://api.tavily.com')

  const includeDate = ref(false)
  const resultCount = ref(5)

  const saveSettings = () => {
    const data = {
      provider: provider.value,
      apiKey: apiKey.value,
      apiEndpoint: apiEndpoint.value,
      includeDate: includeDate.value,
      resultCount: resultCount.value,
    }
    localStorage.setItem('websearch.settings', JSON.stringify(data))
  }

  const loadSettings = () => {
    const raw = localStorage.getItem('websearch.settings')
    if (!raw) return
    try {
      const data = JSON.parse(raw)
      provider.value = data.provider || provider.value
      apiKey.value = data.apiKey || ''
      apiEndpoint.value = data.apiEndpoint || apiEndpoint.value
      includeDate.value = !!data.includeDate
      resultCount.value = Number.isFinite(data.resultCount) ? data.resultCount : resultCount.value
    } catch {}
  }

  const testApiKey = async () => {
    // 这里先进行基本校验，后续可接入真实服务商检测
    return Boolean(apiKey.value && apiKey.value.trim().length >= 8 && apiEndpoint.value)
  }

  return {
    provider,
    apiKey,
    apiEndpoint,
    includeDate,
    resultCount,
    saveSettings,
    loadSettings,
    testApiKey,
  }
})