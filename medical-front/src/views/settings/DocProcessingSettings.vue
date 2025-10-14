<template>
  <div class="docproc-settings">
    <!-- 块一：OCR服务 -->
    <el-card class="section-card" shadow="never">
      <template #header>
        <h2>OCR服务</h2>
      </template>
      <el-form label-width="160px" class="settings-form">
        <el-form-item label="选择OCR图片服务商">
          <el-select v-model="ocrProvider" style="width:240px">
            <el-option label="系统OCR" value="system" />
            <el-option label="Paddle OCR" value="paddle" />
          </el-select>
          <div class="option-desc">默认使用系统OCR</div>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 块二：选中的OCR -->
    <el-card class="section-card" shadow="never">
      <template #header>
        <h2>{{ ocrProviderLabel }}</h2>
      </template>
      <el-form label-width="160px" class="settings-form">
        <template v-if="ocrProvider === 'system'">
          <el-form-item label="支持的语言">
            <el-tooltip placement="top">
              <template #content>选择OCR识别语言，默认包含中文与英文</template>
              <el-icon class="info-icon"><InfoFilled /></el-icon>
            </el-tooltip>
          </el-form-item>
          <el-form-item label="语言选择">
            <el-select v-model="ocrLanguages" multiple filterable style="width:480px">
              <el-option label="中文" value="zh" />
              <el-option label="英文" value="en" />
              <el-option label="日文" value="ja" />
              <el-option label="法文" value="fr" />
              <el-option label="德文" value="de" />
              <el-option label="韩文" value="ko" />
            </el-select>
          </el-form-item>
        </template>

        <template v-if="ocrProvider === 'paddle'">
          <el-form-item label="API URL">
            <el-input v-model="ocrApiUrl" placeholder="https://api.example.com" />
          </el-form-item>
          <el-form-item label="访问令牌">
            <el-input v-model="ocrToken" type="password" placeholder="请输入访问令牌" />
          </el-form-item>
        </template>
      </el-form>
    </el-card>

    <!-- 块三：文档处理服务选择 -->
    <el-card class="section-card" shadow="never">
      <template #header>
        <h2>文档处理</h2>
      </template>
      <el-form label-width="160px" class="settings-form">
        <el-form-item label="选择文档处理服务商">
          <el-select v-model="docProvider" style="width:240px">
            <el-option label="MinerU" value="mineru" />
            <el-option label="Doc2x" value="doc2x" />
            <el-option label="Mistral" value="mistral" />
          </el-select>
          <div class="option-desc">默认使用 MinerU</div>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 块四：选中的文档处理服务商详情 -->
    <el-card class="section-card" shadow="never">
      <template #header>
        <h2>{{ docProviderLabel }}</h2>
      </template>
      <el-form label-width="160px" class="settings-form">
        <el-form-item label="API 密钥">
          <el-input v-model="docApiKey" type="password" placeholder="请输入API密钥" />
        </el-form-item>
        <el-form-item label="API 地址">
          <el-input v-model="docApiEndpoint" placeholder="https://api.example.com" />
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="save">保存</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { InfoFilled } from '@element-plus/icons-vue'
import { useDocProcessingStore } from '@/stores/docProcessing'

const store = useDocProcessingStore()
const ocrProvider = ref(store.ocrProvider)
const ocrLanguages = ref(store.ocrLanguages)
const ocrApiUrl = ref(store.ocrApiUrl)
const ocrToken = ref(store.ocrToken)
const docProvider = ref(store.docProvider)
const docApiKey = ref(store.docApiKey)
const docApiEndpoint = ref(store.docApiEndpoint)

const ocrProviderLabel = computed(() => {
  return ocrProvider.value === 'paddle' ? 'Paddle OCR' : '系统OCR'
})

const docProviderLabel = computed(() => {
  const map = { mineru: 'MinerU', doc2x: 'Doc2x', mistral: 'Mistral' }
  return map[docProvider.value] || '文档处理服务商'
})

const save = () => {
  store.ocrProvider = ocrProvider.value
  store.ocrLanguages = ocrLanguages.value
  store.ocrApiUrl = ocrApiUrl.value
  store.ocrToken = ocrToken.value
  store.docProvider = docProvider.value
  store.docApiKey = docApiKey.value
  store.docApiEndpoint = docApiEndpoint.value
  store.saveSettings()
  ElMessage.success('文档处理设置已保存')
}

onMounted(() => {
  store.loadSettings()
  ocrProvider.value = store.ocrProvider
  ocrLanguages.value = store.ocrLanguages
  ocrApiUrl.value = store.ocrApiUrl
  ocrToken.value = store.ocrToken
  docProvider.value = store.docProvider
  docApiKey.value = store.docApiKey
  docApiEndpoint.value = store.docApiEndpoint
})
</script>

<style scoped>
.docproc-settings { display: flex; flex-direction: column; gap: 20px; }
.settings-form { max-width: 800px; }
.option-desc { margin-top: 6px; font-size: 12px; color: var(--text-secondary); }
.info-icon { color: #909399; }
</style>