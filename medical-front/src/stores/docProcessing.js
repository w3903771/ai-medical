import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useDocProcessingStore = defineStore('docProcessing', () => {
  // OCR 服务
  const ocrProvider = ref('system') // system | paddle
  const ocrLanguages = ref(['zh', 'en'])
  const ocrApiUrl = ref('')
  const ocrToken = ref('')

  // 文档处理服务
  const docProvider = ref('mineru') // mineru | doc2x | mistral
  const docApiKey = ref('')
  const docApiEndpoint = ref('')

  const saveSettings = () => {
    const data = {
      ocrProvider: ocrProvider.value,
      ocrLanguages: ocrLanguages.value,
      ocrApiUrl: ocrApiUrl.value,
      ocrToken: ocrToken.value,
      docProvider: docProvider.value,
      docApiKey: docApiKey.value,
      docApiEndpoint: docApiEndpoint.value,
    }
    localStorage.setItem('doc.processing.settings', JSON.stringify(data))
  }

  const loadSettings = () => {
    const raw = localStorage.getItem('doc.processing.settings')
    if (!raw) return
    try {
      const data = JSON.parse(raw)
      if (data.ocrProvider) ocrProvider.value = data.ocrProvider
      if (Array.isArray(data.ocrLanguages)) ocrLanguages.value = data.ocrLanguages
      if (data.ocrApiUrl) ocrApiUrl.value = data.ocrApiUrl
      if (data.ocrToken) ocrToken.value = data.ocrToken
      if (data.docProvider) docProvider.value = data.docProvider
      if (data.docApiKey) docApiKey.value = data.docApiKey
      if (data.docApiEndpoint) docApiEndpoint.value = data.docApiEndpoint
    } catch {}
  }

  return {
    ocrProvider,
    ocrLanguages,
    ocrApiUrl,
    ocrToken,
    docProvider,
    docApiKey,
    docApiEndpoint,
    saveSettings,
    loadSettings,
  }
})