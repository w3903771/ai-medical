import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useExportStore = defineStore('export', () => {
  // 导出菜单开关（默认全部启用）
  const exportOptionsEnabled = ref({
    plainText: true,
    copyImage: true,
    exportImage: true,
    markdown: true,
    markdownThoughts: true,
    word: true
  })

  // Markdown 导出配置
  const markdownSettings = ref({
    forceLatexDollar: false,
    includeModelName: false,
    showProvider: false,
    standardize: false
  })

  // 网络搜索相关（导出时的包含与呈现方式）
  const webSearchSettings = ref({
    includeInExport: false,      // 在导出文件中包含网络搜索结果
    includeLinks: true,          // 展示来源链接
    maxResults: 5,               // 导出包含的搜索结果个数
    includeDateRange: false,     // 是否限定日期范围
    days: 7,                     // 日期范围（近几天）
    compressMethod: 'none'       // 结果压缩方法：none/simple/aggressive
  })

  const saveExportSettings = () => {
    localStorage.setItem('export.options.enabled', JSON.stringify(exportOptionsEnabled.value))
    localStorage.setItem('export.markdown.settings', JSON.stringify(markdownSettings.value))
    localStorage.setItem('export.websearch.settings', JSON.stringify(webSearchSettings.value))
  }

  const loadExportSettings = () => {
    const e = localStorage.getItem('export.options.enabled')
    if (e) exportOptionsEnabled.value = JSON.parse(e)
    const m = localStorage.getItem('export.markdown.settings')
    if (m) markdownSettings.value = JSON.parse(m)
    const w = localStorage.getItem('export.websearch.settings')
    if (w) webSearchSettings.value = JSON.parse(w)
  }

  const setExportOptionEnabled = (key, enabled) => {
    if (key in exportOptionsEnabled.value) {
      exportOptionsEnabled.value[key] = !!enabled
      saveExportSettings()
    }
  }

  const setMarkdownSetting = (key, value) => {
    if (key in markdownSettings.value) {
      markdownSettings.value[key] = value
      saveExportSettings()
    }
  }

  const setWebSearchSetting = (key, value) => {
    if (key in webSearchSettings.value) {
      webSearchSettings.value[key] = value
      saveExportSettings()
    }
  }

  return {
    exportOptionsEnabled,
    markdownSettings,
    webSearchSettings,
    saveExportSettings,
    loadExportSettings,
    setExportOptionEnabled,
    setMarkdownSetting,
    setWebSearchSetting
  }
})