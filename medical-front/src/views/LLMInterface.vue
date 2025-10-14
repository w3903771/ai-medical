<template>
  <div class="llm-interface">
    <!-- 页面头部 -->
    <div class="page-header">
      <h1>AI问答</h1>
      <p>基于检索增强的智能问答系统</p>
    </div>

    <div class="interface-container">
      <!-- 左侧配置面板 -->
      <div class="config-panel">
        <el-card class="config-card" shadow="never">
          <template #header>
            <div class="card-header">
              <span>查询配置</span>
              <el-button type="text" @click="resetConfig">
                <el-icon><Refresh /></el-icon>
                重置
              </el-button>
            </div>
          </template>

          <!-- 数据范围选择 -->
          <div class="config-section">
            <h3>数据范围</h3>
            <el-radio-group v-model="queryConfig.dataScope" @change="handleDataScopeChange">
              <el-radio label="all">全部数据</el-radio>
              <el-radio label="indicators">指标数据</el-radio>
              <el-radio label="admissions">住院档案</el-radio>
              <el-radio label="custom">自定义</el-radio>
            </el-radio-group>
          </div>

          <!-- 具体数据选择 -->
          <div v-if="queryConfig.dataScope === 'indicators'" class="config-section">
            <h3>指标类型</h3>
            <el-checkbox-group v-model="queryConfig.selectedIndicators">
              <el-checkbox label="weight">体重</el-checkbox>
              <el-checkbox label="bloodPressure">血压</el-checkbox>
              <el-checkbox label="bloodSugar">血糖</el-checkbox>
              <el-checkbox label="heartRate">心率</el-checkbox>
              <el-checkbox label="temperature">体温</el-checkbox>
            </el-checkbox-group>
          </div>

          <div v-if="queryConfig.dataScope === 'admissions'" class="config-section">
            <h3>住院记录</h3>
            <el-select
              v-model="queryConfig.selectedAdmissions"
              multiple
              placeholder="选择住院记录"
              style="width: 100%"
            >
              <el-option
                v-for="admission in admissionsList"
                :key="admission.id"
                :label="admission.label"
                :value="admission.id"
              />
            </el-select>
          </div>

          <div v-if="queryConfig.dataScope === 'custom'" class="config-section">
            <h3>时间范围</h3>
            <el-date-picker
              v-model="queryConfig.dateRange"
              type="daterange"
              range-separator="至"
              start-placeholder="开始日期"
              end-placeholder="结束日期"
              format="YYYY-MM-DD"
              value-format="YYYY-MM-DD"
              style="width: 100%"
            />
          </div>

          <!-- 模型配置 -->
          <div class="config-section">
            <h3>模型设置</h3>
            <el-form label-width="80px" size="small">
              <el-form-item label="模型">
                <el-select 
                  v-model="queryConfig.model" 
                  style="width: 100%"
                  :placeholder="availableModelProviders.length === 0 ? '暂无可用模型' : '请选择模型'"
                  :disabled="availableModelProviders.length === 0"
                >
                  <template v-for="provider in availableModelProviders" :key="provider.id">
                    <el-option-group :label="`${provider.name} ${getProviderStatusText(provider)}`">
                      <el-option 
                        v-for="model in provider.models.filter(m => m.enabled)" 
                        :key="`${provider.id}-${model.id}`"
                        :label="model.name" 
                        :value="`${provider.id}:${model.id}`" 
                      />
                    </el-option-group>
                  </template>
                </el-select>
                <div v-if="availableModelProviders.length === 0" class="model-status-hint">
                  <el-text type="warning" size="small">
                    <el-icon><Warning /></el-icon>
                    请前往设置页面配置模型服务
                  </el-text>
                </div>
              </el-form-item>
              <el-form-item label="温度">
                <el-slider
                  v-model="queryConfig.temperature"
                  :min="0"
                  :max="1"
                  :step="0.1"
                  show-input
                  :input-size="'small'"
                />
              </el-form-item>
              <el-form-item label="检索数量">
                <el-input-number
                  v-model="queryConfig.retrievalCount"
                  :min="1"
                  :max="20"
                  size="small"
                  style="width: 100%"
                />
              </el-form-item>
            </el-form>
          </div>

          <!-- 快捷问题 -->
          <div class="config-section">
            <h3>快捷问题</h3>
            <div class="quick-questions">
              <el-button
                v-for="question in quickQuestions"
                :key="question.id"
                size="small"
                type="primary"
                @click="handleQuickQuestion(question.text)"
                class="question-btn"
              >
                {{ question.text }}
              </el-button>
            </div>
          </div>
        </el-card>
      </div>

      <!-- 右侧对话区域 -->
      <div class="chat-panel">
        <el-card class="chat-card" shadow="never">
          <!-- 对话历史 -->
          <div class="chat-history" ref="chatHistoryRef">
            <div v-if="chatHistory.length === 0" class="empty-chat">
              <el-icon size="64" color="#c0c4cc"><ChatDotRound /></el-icon>
              <p>开始您的智能问答之旅</p>
              <p class="tips">您可以询问关于健康数据的任何问题</p>
            </div>

            <div
              v-for="message in chatHistory"
              :key="message.id"
              :class="['message', message.role]"
            >
              <div class="message-avatar">
                <el-avatar v-if="message.role === 'user'" :size="32">
                  <el-icon><User /></el-icon>
                </el-avatar>
                <el-avatar v-else :size="32" style="background-color: #409eff">
                  <el-icon><Avatar /></el-icon>
                </el-avatar>
              </div>
              
              <div class="message-content">
                <div class="message-header">
                  <span class="message-role">
                    {{ message.role === 'user' ? '您' : 'AI助手' }}
                  </span>
                  <span class="message-time">{{ message.timestamp }}</span>
                </div>
                
                <div class="message-text" v-html="formatMessage(message.content)"></div>
                
                <!-- 检索到的相关数据 -->
                <div v-if="message.retrievedData && message.retrievedData.length > 0" class="retrieved-data">
                  <el-collapse>
                    <el-collapse-item title="相关数据" name="data">
                      <div class="data-items">
                        <div
                          v-for="(item, index) in message.retrievedData"
                          :key="index"
                          class="data-item"
                        >
                          <el-tag size="small" type="info">{{ item.type }}</el-tag>
                          <span class="data-content">{{ item.content }}</span>
                          <span class="data-score">相关度: {{ (item.score * 100).toFixed(1) }}%</span>
                        </div>
                      </div>
                    </el-collapse-item>
                  </el-collapse>
                </div>

                <!-- 消息操作 -->
                <div class="message-actions">
                  <el-button size="small" text @click="handleCopyMessage(message.content)">
                    <el-icon><CopyDocument /></el-icon>
                    复制
                  </el-button>
                  <el-dropdown trigger="hover" @command="cmd => handleMessageExportCommand(cmd, message)">
                    <span class="el-dropdown-link">
                      <el-button size="small" text>
                        <el-icon><Download /></el-icon>
                        导出
                      </el-button>
                    </span>
                    <template #dropdown>
                      <el-dropdown-menu>
                        <el-dropdown-item v-if="exportEnabled.plainText" command="msgCopyText">复制为纯文本</el-dropdown-item>
                        <el-dropdown-item v-if="exportEnabled.copyImage" command="msgCopyImage">复制为图片</el-dropdown-item>
                        <el-dropdown-item v-if="exportEnabled.exportImage" command="msgExportImage">导出为图片</el-dropdown-item>
                        <el-dropdown-item v-if="exportEnabled.markdown" command="msgExportMd">导出为Markdown</el-dropdown-item>
                        <el-dropdown-item v-if="exportEnabled.markdownThoughts" command="msgExportMdThoughts">导出为Markdown（包含思考）</el-dropdown-item>
                        <el-dropdown-item v-if="exportEnabled.word" command="msgExportWord">导出为Word</el-dropdown-item>
                      </el-dropdown-menu>
                    </template>
                  </el-dropdown>
                  <template v-if="message.role === 'assistant'">
                    <el-button size="small" text @click="handleRegenerateResponse(message.id)">
                      <el-icon><Refresh /></el-icon>
                      重新生成
                    </el-button>
                    <el-button size="small" text @click="handleLikeMessage(message.id)">
                      <el-icon><StarFilled /></el-icon>
                      {{ message.liked ? '已赞' : '点赞' }}
                    </el-button>
                  </template>
                </div>
              </div>
            </div>

            <!-- 加载状态 -->
            <div v-if="isLoading" class="message assistant loading">
              <div class="message-avatar">
                <el-avatar :size="32" style="background-color: #409eff">
                  <el-icon><Avatar /></el-icon>
                </el-avatar>
              </div>
              <div class="message-content">
                <div class="message-header">
                  <span class="message-role">AI助手</span>
                </div>
                <div class="loading-dots">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
              </div>
            </div>
          </div>

          <!-- 输入区域 -->
          <div class="chat-input">
            <div class="input-toolbar">
              <el-button size="small" @click="handleClearHistory">
                <el-icon><Delete /></el-icon>
                清空对话
              </el-button>
              <el-dropdown trigger="hover" @command="handleConversationExportCommand">
                <span class="el-dropdown-link">
                  <el-button size="small">
                    <el-icon><Download /></el-icon>
                    导出对话
                  </el-button>
                </span>
                <template #dropdown>
                  <el-dropdown-menu>
          <el-dropdown-item v-if="exportEnabled.plainText" command="convCopyText">复制为纯文本</el-dropdown-item>
          <el-dropdown-item v-if="exportEnabled.copyImage" command="convCopyImage">复制为图片</el-dropdown-item>
          <el-dropdown-item v-if="exportEnabled.exportImage" command="convExportImage">导出为图片</el-dropdown-item>
          <el-dropdown-item v-if="exportEnabled.markdown" command="convExportMd">导出为Markdown</el-dropdown-item>
          <el-dropdown-item v-if="exportEnabled.markdownThoughts" command="convExportMdThoughts">导出为Markdown（包含思考）</el-dropdown-item>
          <el-dropdown-item v-if="exportEnabled.word" command="convExportWord">导出为Word</el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
              <div class="input-stats">
                <span>数据范围: {{ dataScopeText }}</span>
                <span>模型: {{ getModelDisplayName() }}</span>
              </div>
            </div>
            
            <div class="input-container">
              <el-input
                v-model="currentMessage"
                type="textarea"
                :rows="3"
                placeholder="请输入您的问题..."
                @keydown.ctrl.enter="handleSendMessage"
                :disabled="isLoading"
                class="message-input"
              />
              <div class="input-actions">
                <el-button
                  type="primary"
                  @click="handleSendMessage"
                  :loading="isLoading"
                  :disabled="!currentMessage.trim()"
                >
                  <el-icon><Promotion /></el-icon>
                  发送 (Ctrl+Enter)
                </el-button>
              </div>
            </div>
          </div>
        </el-card>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, nextTick, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  Refresh, 
  ChatDotRound, 
  User, 
  Avatar, 
  CopyDocument, 
  StarFilled,
  Warning 
} from '@element-plus/icons-vue'
import { useExportStore } from '@/stores/export'

// 响应式数据
const chatHistoryRef = ref()
const currentMessage = ref('')
const isLoading = ref(false)
const chatHistory = ref([])
const exportStore = useExportStore()
const exportEnabled = computed(() => exportStore.exportOptionsEnabled)

// 查询配置
const queryConfig = reactive({
  dataScope: 'all',
  selectedIndicators: ['weight', 'bloodPressure', 'bloodSugar'],
  selectedAdmissions: [],
  dateRange: null,
  model: '',
  temperature: 0.7,
  retrievalCount: 5
})

// 可用模型提供商
const availableModelProviders = ref([])

// 从本地存储加载模型配置并检查状态
const loadModelProvidersFromStorage = async () => {
  const savedProviders = localStorage.getItem('modelProviders')
  if (savedProviders) {
    const providers = JSON.parse(savedProviders)
    
    // 检查每个提供商的状态
    for (const provider of providers) {
      if (provider.enabled && provider.apiKey) {
        try {
          // 检查API连接状态
          await checkProviderStatus(provider)
        } catch (error) {
          console.warn(`模型提供商 ${provider.name} 状态检查失败:`, error)
          // 可以选择禁用该提供商或标记为不可用
          provider.status = 'unavailable'
        }
      } else {
        provider.status = provider.enabled ? 'no-api-key' : 'disabled'
      }
    }
    
    // 只保留启用且可用的提供商
    availableModelProviders.value = providers.filter(p => p.enabled && p.status !== 'unavailable')
    
    // 如果有可用模型，设置默认选中的模型
    if (availableModelProviders.value.length > 0) {
      const firstProvider = availableModelProviders.value[0]
      const enabledModel = firstProvider.models.find(m => m.enabled)
      if (enabledModel) {
        queryConfig.model = `${firstProvider.id}:${enabledModel.id}`
      }
    } else {
      // 如果没有可用模型，清空当前选择
      queryConfig.model = ''
    }
  }
}

// 检查提供商状态
const checkProviderStatus = async (provider) => {
  if (!provider.apiKey) {
    provider.status = 'no-api-key'
    return false
  }
  
  try {
    // 模拟API连接测试
    // 实际应用中这里应该调用真实的API测试
    const response = await new Promise((resolve, reject) => {
      setTimeout(() => {
        // 模拟90%的成功率
        if (Math.random() > 0.1) {
          resolve({ status: 'ok' })
        } else {
          reject(new Error('连接超时'))
        }
      }, 1000)
    })
    
    provider.status = 'available'
    return true
  } catch (error) {
    provider.status = 'unavailable'
    throw error
  }
}

// 获取提供商状态文本
const getProviderStatusText = (provider) => {
  switch (provider.status) {
    case 'available':
      return '(可用)'
    case 'unavailable':
      return '(不可用)'
    case 'no-api-key':
      return '(未配置API Key)'
    case 'disabled':
      return '(已禁用)'
    default:
      return ''
  }
}

// 住院记录列表
const admissionsList = ref([
  { id: 'admission-1', label: '2024-01 市人民医院 心内科' },
  { id: 'admission-2', label: '2024-01 中医院 内分泌科' },
  { id: 'admission-3', label: '2023-12 省医院 消化科' }
])

// 快捷问题
const quickQuestions = ref([
  { id: 1, text: '我的血压趋势如何？' },
  { id: 2, text: '最近的血糖控制情况' },
  { id: 3, text: '体重变化分析' },
  { id: 4, text: '住院期间的恢复情况' },
  { id: 5, text: '用药建议和注意事项' },
  { id: 6, text: '生活方式改善建议' }
])

// 获取当前选择模型的显示名称
const getModelDisplayName = () => {
  if (!queryConfig.model) return '未选择'
  
  const [providerId, modelId] = queryConfig.model.split(':')
  const provider = availableModelProviders.value.find(p => p.id === providerId)
  if (!provider) return queryConfig.model
  
  const model = provider.models.find(m => m.id === modelId)
  if (!model) return queryConfig.model
  
  return `${provider.name} - ${model.name}`
}

// 计算属性
const dataScopeText = computed(() => {
  const scopeMap = {
    all: '全部数据',
    indicators: '指标数据',
    admissions: '住院档案',
    custom: '自定义范围'
  }
  return scopeMap[queryConfig.dataScope] || '未知'
})

// 方法
const handleDataScopeChange = (value) => {
  // 重置相关配置
  if (value !== 'indicators') {
    queryConfig.selectedIndicators = []
  }
  if (value !== 'admissions') {
    queryConfig.selectedAdmissions = []
  }
  if (value !== 'custom') {
    queryConfig.dateRange = null
  }
}

const resetConfig = () => {
  Object.assign(queryConfig, {
    dataScope: 'all',
    selectedIndicators: ['weight', 'bloodPressure', 'bloodSugar'],
    selectedAdmissions: [],
    dateRange: null,
    model: 'gpt-4',
    temperature: 0.7,
    retrievalCount: 5
  })
}

const handleQuickQuestion = (question) => {
  currentMessage.value = question
  handleSendMessage()
}

const handleSendMessage = async () => {
  if (!currentMessage.value.trim() || isLoading.value) return

  const userMessage = {
    id: Date.now(),
    role: 'user',
    content: currentMessage.value,
    timestamp: new Date().toLocaleTimeString()
  }

  chatHistory.value.push(userMessage)
  const question = currentMessage.value
  currentMessage.value = ''
  isLoading.value = true

  // 滚动到底部
  await nextTick()
  scrollToBottom()

  try {
    // 模拟API调用
    await new Promise(resolve => setTimeout(resolve, 2000))

    // 模拟检索到的相关数据
    const retrievedData = [
      {
        type: '血压数据',
        content: '2024-01-15: 收缩压 135mmHg, 舒张压 85mmHg',
        score: 0.95
      },
      {
        type: '用药记录',
        content: '氨氯地平片 5mg，每日一次',
        score: 0.87
      },
      {
        type: '医生建议',
        content: '建议低盐饮食，适量运动',
        score: 0.82
      }
    ]

    const assistantMessage = {
      id: Date.now() + 1,
      role: 'assistant',
      content: generateMockResponse(question),
      timestamp: new Date().toLocaleTimeString(),
      retrievedData: retrievedData,
      liked: false
    }

    chatHistory.value.push(assistantMessage)
    
    await nextTick()
    scrollToBottom()
  } catch (error) {
    ElMessage.error('发送消息失败，请重试')
    console.error('发送消息错误:', error)
  } finally {
    isLoading.value = false
  }
}

const generateMockResponse = (question) => {
  // 简单的模拟响应生成
  if (question.includes('血压')) {
    return `根据您的血压数据分析：

**当前状态：**
- 最近一次测量：收缩压 135mmHg，舒张压 85mmHg
- 血压水平：轻度高血压（1级）

**趋势分析：**
- 近30天平均收缩压：132mmHg（较上月下降3mmHg）
- 近30天平均舒张压：83mmHg（较上月下降2mmHg）
- 整体趋势：稳中有降，控制良好

**建议：**
1. 继续按医嘱服用降压药物
2. 保持低盐饮食（每日盐摄入量<6g）
3. 适量有氧运动，每周3-5次，每次30分钟
4. 定期监测血压，建议每周2-3次

**注意事项：**
如血压持续超过140/90mmHg，请及时就医调整用药方案。`
  }
  
  return `感谢您的提问。基于您的健康数据，我为您提供以下分析和建议：

这是一个模拟回复，实际系统会根据您的具体数据和问题提供个性化的专业建议。

如需更详细的分析，请提供更具体的问题或时间范围。`
}

const formatMessage = (content) => {
  // 简单的markdown格式化
  return content
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    .replace(/\n/g, '<br>')
}

const scrollToBottom = () => {
  if (chatHistoryRef.value) {
    chatHistoryRef.value.scrollTop = chatHistoryRef.value.scrollHeight
  }
}

const handleCopyMessage = async (content) => {
  try {
    await navigator.clipboard.writeText(content.replace(/<[^>]*>/g, ''))
    ElMessage.success('已复制到剪贴板')
  } catch (error) {
    ElMessage.error('复制失败')
  }
}

const handleRegenerateResponse = async (messageId) => {
  const messageIndex = chatHistory.value.findIndex(msg => msg.id === messageId)
  if (messageIndex === -1) return

  // 找到对应的用户问题
  const userMessageIndex = messageIndex - 1
  if (userMessageIndex >= 0) {
    const userMessage = chatHistory.value[userMessageIndex]
    
    // 删除原回复
    chatHistory.value.splice(messageIndex, 1)
    
    // 重新生成回复
    currentMessage.value = userMessage.content
    await handleSendMessage()
  }
}

const handleLikeMessage = (messageId) => {
  const message = chatHistory.value.find(msg => msg.id === messageId)
  if (message) {
    message.liked = !message.liked
    ElMessage.success(message.liked ? '感谢您的反馈' : '已取消点赞')
  }
}

const handleClearHistory = async () => {
  try {
    await ElMessageBox.confirm('确定要清空所有对话记录吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    chatHistory.value = []
    ElMessage.success('对话记录已清空')
  } catch {
    // 用户取消
  }
}

const handleExportHistory = () => {
  if (chatHistory.value.length === 0) {
    ElMessage.warning('暂无对话记录可导出')
    return
  }

  const exportData = chatHistory.value.map(msg => ({
    角色: msg.role === 'user' ? '用户' : 'AI助手',
    时间: msg.timestamp,
    内容: msg.content.replace(/<[^>]*>/g, '')
  }))

  const jsonStr = JSON.stringify(exportData, null, 2)
  const blob = new Blob([jsonStr], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  
  const a = document.createElement('a')
  a.href = url
  a.download = `对话记录_${new Date().toISOString().split('T')[0]}.json`
  a.click()
  
  URL.revokeObjectURL(url)
  ElMessage.success('对话记录已导出')
}

// 对话与消息导出子菜单命令处理 & 导出工具函数
const handleConversationExportCommand = async (command) => {
  switch (command) {
    case 'convCopyText':
      await copyConversationAsText()
      break
    case 'convCopyImage':
      await copyConversationAsImage()
      break
    case 'convExportImage':
      await exportConversationAsImage()
      break
    case 'convExportMd':
      await exportConversationAsMarkdown(false)
      break
    case 'convExportMdThoughts':
      await exportConversationAsMarkdown(true)
      break
    case 'convExportWord':
      await exportConversationAsWord()
      break
  }
}

const handleMessageExportCommand = async (command, message) => {
  switch (command) {
    case 'msgCopyText':
      await handleCopyMessage(textFromMessage(message))
      break
    case 'msgCopyImage':
      await copyTextImageToClipboard(textFromMessage(message))
      break
    case 'msgExportImage':
      await exportTextAsImage(textFromMessage(message), `消息_${message.id}.png`)
      break
    case 'msgExportMd':
      await exportSingleMessageMarkdown(message, false)
      break
    case 'msgExportMdThoughts':
      await exportSingleMessageMarkdown(message, true)
      break
    case 'msgExportWord':
      await exportTextAsWord(textFromMessage(message), `消息_${message.id}.doc`)
      break
  }
}

const textFromMessage = (msg) => {
  const base = (msg?.content || '').replace(/<[^>]*>/g, '')
  const refs = Array.isArray(msg?.retrievedData)
    ? '\n\n参考数据:\n' + msg.retrievedData.map((d, i) => `${i + 1}. [${d.type}] ${d.content}`).join('\n')
    : ''
  return base + (refs || '')
}

const renderTextToCanvas = async (text, width = 800) => {
  const padding = 20
  const ctx = document.createElement('canvas').getContext('2d')
  ctx.font = '14px -apple-system,Segoe UI,Roboto,Helvetica Neue,Arial,Noto Sans,Noto Sans CJK SC,sans-serif'
  const lineHeight = 22
  const maxWidth = width - padding * 2
  const words = text.split('\n')
  const lines = []
  words.forEach(w => {
    const parts = w.split(' ')
    let current = ''
    parts.forEach(p => {
      const test = current ? current + ' ' + p : p
      if (ctx.measureText(test).width > maxWidth) {
        if (current) lines.push(current)
        current = p
      } else {
        current = test
      }
    })
    lines.push(current)
  })
  const height = padding * 2 + lines.length * lineHeight
  const canvas = document.createElement('canvas')
  canvas.width = width
  canvas.height = Math.max(height, 200)
  const c = canvas.getContext('2d')
  c.fillStyle = '#ffffff'
  c.fillRect(0, 0, canvas.width, canvas.height)
  c.fillStyle = '#333333'
  c.font = ctx.font
  let y = padding + 14
  lines.forEach(line => {
    c.fillText(line, padding, y)
    y += lineHeight
  })
  return canvas
}

const exportTextAsImage = async (text, filename = '导出图片.png') => {
  const canvas = await renderTextToCanvas(text)
  const url = canvas.toDataURL('image/png')
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  a.click()
}

const copyTextImageToClipboard = async (text) => {
  try {
    const canvas = await renderTextToCanvas(text)
    canvas.toBlob(async (blob) => {
      if (!blob) return
      await navigator.clipboard.write([
        new window.ClipboardItem({ 'image/png': blob })
      ])
      ElMessage.success('图片已复制到剪贴板')
    })
  } catch (e) {
    ElMessage.error('复制图片失败')
  }
}

const copyConversationAsText = async () => {
  const text = chatHistory.value.map(m => `${m.role === 'user' ? '用户' : 'AI助手'}(${m.timestamp}):\n${textFromMessage(m)}\n`).join('\n')
  await navigator.clipboard.writeText(text)
  ElMessage.success('纯文本已复制到剪贴板')
}

const exportConversationAsImage = async () => {
  const text = chatHistory.value.map(m => `${m.role === 'user' ? '用户' : 'AI助手'}(${m.timestamp}):\n${textFromMessage(m)}\n`).join('\n')
  await exportTextAsImage(text, `对话_${new Date().toISOString().slice(0,10)}.png`)
}

const copyConversationAsImage = async () => {
  const text = chatHistory.value.map(m => `${m.role === 'user' ? '用户' : 'AI助手'}(${m.timestamp}):\n${textFromMessage(m)}\n`).join('\n')
  await copyTextImageToClipboard(text)
}

const exportTextAsWord = async (text, filename = '导出文档.doc') => {
  const html = `<!DOCTYPE html><html><head><meta charset=\"utf-8\"></head><body><pre style=\"font-family: inherit; white-space: pre-wrap\">${text.replace(/[&<>]/g, s => ({'&':'&amp;','<':'&lt;','>':'&gt;'}[s]))}</pre></body></html>`
  const blob = new Blob([html], { type: 'application/msword' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  a.click()
  URL.revokeObjectURL(url)
}

const getModelMeta = () => {
  if (!queryConfig.model) return { provider: '', model: '' }
  const [providerId, modelId] = queryConfig.model.split(':')
  const provider = availableModelProviders.value.find(p => p.id === providerId)
  const model = provider?.models?.find(m => m.id === modelId)
  return { provider: provider?.name || providerId || '', model: model?.name || modelId || '' }
}

const toMarkdown = (message, includeThoughts = false) => {
  const role = message.role === 'user' ? '用户' : 'AI助手'
  const time = message.timestamp
  const content = textFromMessage(message)
  let md = `### ${role} (${time})\n\n${content}\n`
  if (includeThoughts) {
    const thoughts = message.thoughts ? String(message.thoughts) : '此模型未返回思考内容。'
    md += `\n> 思考：${thoughts}\n`
  }
  if (exportStore.markdownSettings.forceLatexDollar) {
    md = `> 注意：已启用 $$ 公式标记。\n\n` + md
  }
  return md
}

const exportConversationAsMarkdown = async (includeThoughts = false) => {
  const meta = getModelMeta()
  const headerLines = []
  if (exportStore.markdownSettings.includeModelName || exportStore.markdownSettings.showProvider) {
    headerLines.push(`模型：${exportStore.markdownSettings.showProvider ? meta.provider + ' - ' : ''}${meta.model}`)
  }
  headerLines.push(`导出时间：${new Date().toLocaleString()}`)
  const header = exportStore.markdownSettings.standardize ? `---\n${headerLines.map(l => l).join('\n')}\n---\n\n` : headerLines.join('\n') + '\n\n'
  const body = chatHistory.value.map(m => toMarkdown(m, includeThoughts)).join('\n\n')
  const blob = new Blob([header + body], { type: 'text/markdown' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `对话_${new Date().toISOString().slice(0,10)}.md`
  a.click()
  URL.revokeObjectURL(url)
}

const exportSingleMessageMarkdown = async (message, includeThoughts = false) => {
  const meta = getModelMeta()
  const headerLines = []
  if (exportStore.markdownSettings.includeModelName || exportStore.markdownSettings.showProvider) {
    headerLines.push(`模型：${exportStore.markdownSettings.showProvider ? meta.provider + ' - ' : ''}${meta.model}`)
  }
  headerLines.push(`导出时间：${new Date().toLocaleString()}`)
  const header = exportStore.markdownSettings.standardize ? `---\n${headerLines.join('\n')}\n---\n\n` : headerLines.join('\n') + '\n\n'
  const body = toMarkdown(message, includeThoughts)
  const blob = new Blob([header + body], { type: 'text/markdown' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `消息_${message.id}.md`
  a.click()
  URL.revokeObjectURL(url)
}

const exportConversationAsWord = async () => {
  const text = chatHistory.value.map(m => `${m.role === 'user' ? '用户' : 'AI助手'}(${m.timestamp}):\n${textFromMessage(m)}\n`).join('\n')
  await exportTextAsWord(text, `对话_${new Date().toISOString().slice(0,10)}.doc`)
}

// 生命周期
onMounted(async () => {
  exportStore.loadExportSettings()
  await loadModelProvidersFromStorage()
  // 初始化欢迎消息
  chatHistory.value.push({
    id: 0,
    role: 'assistant',
    content: '您好！我是您的健康数据AI助手。我可以帮您分析健康指标、解读医疗报告、提供个性化建议。请告诉我您想了解什么？',
    timestamp: new Date().toLocaleTimeString(),
    liked: false
  })
})
</script>

<style scoped>
.llm-interface {
  padding: 0;
}

.page-header {
  margin-bottom: 24px;
}

.page-header h1 {
  margin: 0 0 8px 0;
  font-size: 24px;
  font-weight: 600;
  color: var(--text-primary);
}

.page-header p {
  margin: 0;
  color: var(--text-secondary);
}

.interface-container {
  display: flex;
  gap: 20px;
  height: calc(100vh - 200px);
}

.config-panel {
  width: 320px;
  flex-shrink: 0;
}

.config-card {
  height: 100%;
  overflow-y: auto;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
}

.config-section {
  margin-bottom: 24px;
}

.config-section h3 {
  margin: 0 0 12px 0;
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
}

.config-section .el-radio-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.config-section .el-checkbox-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.quick-questions {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.question-btn {
  text-align: left;
  height: auto;
  padding: 8px 12px;
  white-space: normal;
  line-height: 1.4;
}

.chat-panel {
  flex: 1;
  overflow: hidden;
}

.chat-card {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.chat-card :deep(.el-card__body) {
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: 0;
}

.chat-history {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  background: #fafafa;
}

.empty-chat {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: var(--text-secondary);
  text-align: center;
}

.empty-chat p {
  margin: 16px 0 0 0;
}

.empty-chat .tips {
  font-size: 14px;
  color: var(--text-tertiary);
}

.message {
  display: flex;
  gap: 12px;
  margin-bottom: 24px;
}

.message.user {
  flex-direction: row-reverse;
}

.message.user .message-content {
  background: #409eff;
  color: white;
}

.message.user .message-header .message-role {
  color: rgba(255, 255, 255, 0.8);
}

.message.user .message-header .message-time {
  color: rgba(255, 255, 255, 0.6);
}

.message-avatar {
  flex-shrink: 0;
}

.message-content {
  flex: 1;
  max-width: 70%;
  background: white;
  border-radius: 12px;
  padding: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.message.user .message-content {
  max-width: 70%;
  margin-left: auto;
}

.message-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.message-role {
  font-weight: 600;
  font-size: 14px;
  color: var(--text-primary);
}

.message-time {
  font-size: 12px;
  color: var(--text-tertiary);
}

.message-text {
  line-height: 1.6;
  word-wrap: break-word;
}

.retrieved-data {
  margin-top: 16px;
}

.data-items {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.data-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px;
  background: #f5f7fa;
  border-radius: 6px;
  font-size: 14px;
}

.data-content {
  flex: 1;
}

.data-score {
  font-size: 12px;
  color: var(--text-secondary);
}

.message-actions {
  display: flex;
  gap: 8px;
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid #f0f0f0;
}

.loading {
  opacity: 0.8;
}

.loading-dots {
  display: flex;
  gap: 4px;
  align-items: center;
}

.loading-dots span {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #409eff;
  animation: loading-bounce 1.4s ease-in-out infinite both;
}

.loading-dots span:nth-child(1) { animation-delay: -0.32s; }
.loading-dots span:nth-child(2) { animation-delay: -0.16s; }

@keyframes loading-bounce {
  0%, 80%, 100% {
    transform: scale(0);
  }
  40% {
    transform: scale(1);
  }
}

.chat-input {
  border-top: 1px solid var(--border-color);
  padding: 16px 20px;
  background: white;
}

.input-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.input-stats {
  display: flex;
  gap: 16px;
  font-size: 12px;
  color: var(--text-secondary);
}

.input-container {
  display: flex;
  gap: 12px;
  align-items: flex-end;
}

.model-status-hint {
  margin-top: 4px;
}

.model-status-hint .el-text {
  display: flex;
  align-items: center;
  gap: 4px;
}

.message-input {
  flex: 1;
}

.input-actions {
  display: flex;
  align-items: flex-end;
}

/* 响应式设计 */
@media (max-width: 1024px) {
  .interface-container {
    flex-direction: column;
    height: auto;
  }
  
  .config-panel {
    width: 100%;
    height: auto;
  }
  
  .chat-panel {
    height: 600px;
  }
}

@media (max-width: 768px) {
  .message-content {
    max-width: 85%;
  }
  
  .input-container {
    flex-direction: column;
    align-items: stretch;
  }
  
  .input-actions {
    margin-top: 8px;
    justify-content: flex-end;
  }
  
  .input-toolbar {
    flex-direction: column;
    align-items: stretch;
    gap: 8px;
  }
  
  .input-stats {
    justify-content: center;
  }
}
</style>