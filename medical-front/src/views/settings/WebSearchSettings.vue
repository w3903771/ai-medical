<template>
  <div class="websearch-settings">
    <el-card class="section-card" shadow="never">
      <template #header>
        <div class="header-row">
          <h2>网络搜索</h2>
          <div class="provider-select">
            <span class="label">搜索服务商</span>
            <el-select v-model="provider" size="small" style="width: 200px">
              <el-option label="Tavily" value="tavily" />
              <el-option label="Google" value="google" />
              <el-option label="Bing" value="bing" />
              <el-option label="Baidu" value="baidu" />
            </el-select>
          </div>
        </div>
      </template>

      <el-form label-width="120px" class="settings-form">
        <h3 class="section-title">API 设置</h3>
        <el-form-item label="API 密钥">
          <el-input v-model="apiKey" type="password" placeholder="请输入API密钥" />
        </el-form-item>
        <el-form-item label="API 密钥检测">
          <el-button type="primary" @click="detectApiKey" :loading="testing">检测</el-button>
          <div class="option-desc">将进行基本校验，后续可接入真实检测。</div>
        </el-form-item>
        <el-form-item label="API 地址">
          <el-input v-model="apiEndpoint" placeholder="https://api.example.com" />
        </el-form-item>

        <h3 class="section-title">常规设置</h3>
        <el-form-item label="搜索包含日期">
          <el-switch v-model="includeDate" />
        </el-form-item>
        <el-form-item label="搜索结果个数">
          <el-slider v-model="resultCount" :min="1" :max="100" :step="1" show-stops />
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="save">保存</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { useWebSearchStore } from '@/stores/webSearch'

const store = useWebSearchStore()
const provider = ref(store.provider)
const apiKey = ref(store.apiKey)
const apiEndpoint = ref(store.apiEndpoint)
const includeDate = ref(store.includeDate)
const resultCount = ref(store.resultCount)
const testing = ref(false)

const save = () => {
  store.provider = provider.value
  store.apiKey = apiKey.value
  store.apiEndpoint = apiEndpoint.value
  store.includeDate = includeDate.value
  store.resultCount = resultCount.value
  store.saveSettings()
  ElMessage.success('网络搜索设置已保存')
}

const detectApiKey = async () => {
  testing.value = true
  try {
    const ok = await store.testApiKey()
    ok ? ElMessage.success('API密钥检测通过') : ElMessage.error('API密钥检测失败')
  } finally {
    testing.value = false
  }
}

onMounted(() => {
  store.loadSettings()
  provider.value = store.provider
  apiKey.value = store.apiKey
  apiEndpoint.value = store.apiEndpoint
  includeDate.value = store.includeDate
  resultCount.value = store.resultCount
})
</script>

<style scoped>
.websearch-settings { display: flex; flex-direction: column; gap: 20px; }
.header-row { display: flex; align-items: center; justify-content: space-between; }
.provider-select { display: flex; align-items: center; gap: 10px; }
.provider-select .label { color: var(--text-secondary); }
.settings-form { max-width: 800px; }
.section-title { margin: 8px 0 16px; color: #303133; }
.option-desc { margin-top: 6px; font-size: 12px; color: var(--text-secondary); }
</style>