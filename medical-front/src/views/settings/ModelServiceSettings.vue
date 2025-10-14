<template>
  <div class="model-service-settings">
    <div class="settings-layout">
      <!-- 左侧服务商菜单 -->
      <div class="provider-menu">
        <el-card class="menu-card" shadow="never">
          <template #header>
            <div class="menu-header">
              <h3>模型服务商</h3>
            </div>
          </template>
          
          <el-menu
            :default-active="selectedProviderId"
            @select="handleProviderSelect"
            class="provider-menu-list"
          >
            <el-menu-item
              v-for="provider in modelProviders"
              :key="provider.id"
              :index="provider.id"
              class="provider-menu-item"
            >
              <div class="menu-item-content">
                <div class="provider-info">
                  <span class="provider-name">{{ provider.name }}</span>
                  <el-tag 
                    :type="provider.enabled ? 'success' : 'info'" 
                    size="small"
                    class="provider-status"
                  >
                    {{ provider.enabled ? '已启用' : '未启用' }}
                  </el-tag>
                </div>
                <div class="provider-models-count">
                  {{ provider.selectedModels?.length || 0 }}/{{ provider.models?.length || 0 }} 模型
                </div>
              </div>
            </el-menu-item>
          </el-menu>
        </el-card>
      </div>

      <!-- 右侧配置区域 -->
      <div class="provider-config-area">
        <el-card class="config-card" shadow="never">
          <template #header>
            <div class="config-header">
              <div class="header-left">
                <h2>{{ selectedProvider?.name || '请选择服务商' }}</h2>
                <el-tag v-if="selectedProvider" :type="selectedProvider.enabled ? 'success' : 'danger'">
                  {{ selectedProvider.enabled ? '已启用' : '已禁用' }}
                </el-tag>
              </div>
              <div class="header-actions">
                <el-button 
                  v-if="selectedProvider" 
                  :type="selectedProvider.enabled ? 'warning' : 'success'"
                  @click="toggleProviderStatus"
                >
                  {{ selectedProvider.enabled ? '禁用服务' : '启用服务' }}
                </el-button>
                <el-button type="primary" @click="handleSaveModelConfigs">保存配置</el-button>
              </div>
            </div>
          </template>

          <!-- 未选择服务商时的提示 -->
          <div v-if="!selectedProvider" class="no-selection">
            <el-empty description="请从左侧选择一个模型服务商进行配置" />
          </div>

          <!-- 选中服务商的配置 -->
          <div v-else class="provider-config">
            <!-- 基础配置 -->
            <div class="config-section">
              <h3>基础配置</h3>
              <el-form label-width="120px" class="config-form">
                <el-form-item label="API Key" required>
                  <el-input
                    v-model="selectedProvider.apiKey"
                    placeholder="请输入API Key"
                    :type="selectedProvider.showApiKey ? 'text' : 'password'"
                    clearable
                  >
                    <template #append>
                      <el-button @click="selectedProvider.showApiKey = !selectedProvider.showApiKey">
                        <el-icon>
                          <component :is="selectedProvider.showApiKey ? 'Hide' : 'View'" />
                        </el-icon>
                      </el-button>
                    </template>
                  </el-input>
                </el-form-item>

                <el-form-item label="自定义端点">
                  <el-switch 
                    v-model="selectedProvider.customEndpoint"
                    active-text="启用"
                    inactive-text="禁用"
                  />
                </el-form-item>

                <el-form-item v-if="selectedProvider.customEndpoint" label="端点URL">
                  <el-input
                    v-model="selectedProvider.endpoint"
                    placeholder="请输入自定义端点URL"
                    clearable
                  />
                </el-form-item>

                <el-form-item>
                  <el-button @click="handleTestApi(selectedProvider)" :loading="testingApi">
                    <el-icon><Connection /></el-icon>
                    测试API连接
                  </el-button>
                  <el-button @click="resetModelConfig(selectedProvider)">
                    <el-icon><Refresh /></el-icon>
                    重置配置
                  </el-button>
                </el-form-item>
              </el-form>
            </div>

            <!-- 模型配置 -->
            <div class="config-section">
              <div class="section-header">
                <h3>可用模型</h3>
                <div class="model-actions" v-if="selectedProvider.enabled">
                  <el-button size="small" @click="selectAllModels">全选</el-button>
                  <el-button size="small" @click="clearAllModels">清空</el-button>
                </div>
              </div>
              
              <div v-if="selectedProvider.enabled" class="models-grid">
                <el-checkbox-group v-model="selectedProvider.selectedModels" @change="handleModelSelectionChange">
                  <div v-for="model in selectedProvider.models" :key="model.id" class="model-card">
                    <el-checkbox :label="model.id" class="model-checkbox">
                      <div class="model-info">
                        <div class="model-name">{{ model.name }}</div>
                        <div class="model-description">{{ model.description }}</div>
                        <div class="model-meta">
                          <el-tag size="small" type="info">{{ model.type || '通用' }}</el-tag>
                          <span class="model-context" v-if="model.contextLength">
                            上下文: {{ model.contextLength }}
                          </span>
                        </div>
                      </div>
                    </el-checkbox>
                  </div>
                </el-checkbox-group>
              </div>

              <!-- 禁用状态下的模型预览 -->
              <div v-else class="models-preview">
                <div class="models-grid">
                  <div v-for="model in selectedProvider.models" :key="model.id" class="model-card disabled">
                    <div class="model-info">
                      <div class="model-name">{{ model.name }}</div>
                      <div class="model-description">{{ model.description }}</div>
                      <div class="model-meta">
                        <el-tag size="small" type="info" effect="plain">{{ model.type || '通用' }}</el-tag>
                        <span class="model-context" v-if="model.contextLength">
                          上下文: {{ model.contextLength }}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
                <div class="disabled-overlay">
                  <el-alert
                    title="服务已禁用"
                    description="请先启用此服务商才能选择模型"
                    type="warning"
                    :closable="false"
                  />
                </div>
              </div>
            </div>
          </div>
        </el-card>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { View, Hide, Connection, Refresh } from '@element-plus/icons-vue'
import { useSettingsStore } from '@/stores/settings'

const settingsStore = useSettingsStore()

// 响应式数据
const selectedProviderId = ref('')
const testingApi = ref(false)

// 从store获取模型提供商数据
const modelProviders = computed(() => settingsStore.modelProviders)

// 当前选中的服务商
const selectedProvider = computed(() => {
  return modelProviders.value.find(p => p.id === selectedProviderId.value)
})

// 组件挂载时初始化
onMounted(() => {
  // 确保数据已加载
  settingsStore.initSettings()
  
  // 初始化选择第一个服务商
  if (modelProviders.value.length > 0 && !selectedProviderId.value) {
    selectedProviderId.value = modelProviders.value[0].id
  }
})

// 处理服务商选择
const handleProviderSelect = (providerId) => {
  selectedProviderId.value = providerId
}

// 切换服务商启用状态（与保存逻辑合并，强制同步写入）
const toggleProviderStatus = () => {
  if (!selectedProvider.value) return

  // 切换启用状态
  selectedProvider.value.enabled = !selectedProvider.value.enabled

  // 合并切换与保存逻辑：立即同步模型启用到各模型条目
  if (!selectedProvider.value.enabled) {
    // 服务禁用则清空选择，所有模型标记为未启用
    selectedProvider.value.selectedModels = []
  } else {
    // 服务启用且未选择模型时，默认根据模型自身enabled初始化
    if (!selectedProvider.value.selectedModels || selectedProvider.value.selectedModels.length === 0) {
      selectedProvider.value.selectedModels = selectedProvider.value.models
        .filter(m => m.enabled)
        .map(m => m.id)
    }
  }

  // 写入localStorage供LLM页面读取（会把selectedModels映射到model.enabled）
  handleSaveModelConfigs()

  ElMessage.success(`${selectedProvider.value.name} 已${selectedProvider.value.enabled ? '启用' : '禁用'}，已同步模型配置`)
}

// 测试API连接
const handleTestApi = async (provider) => {
  testingApi.value = true
  try {
    await settingsStore.testApiConnection(provider)
    ElMessage.success(`${provider.name} API连接测试成功`)
  } catch (error) {
    ElMessage.error(`${provider.name} API连接测试失败: ${error.message}`)
  } finally {
    testingApi.value = false
  }
}

// 重置模型配置
const resetModelConfig = (provider) => {
  settingsStore.resetModelConfig(provider.id)
  ElMessage.info(`已重置 ${provider.name} 配置`)
}

// 处理模型选择变化
const handleModelSelectionChange = () => {
  // 实时保存配置，确保与LLM页面同步
  handleSaveModelConfigs()
}

// 全选模型
const selectAllModels = () => {
  if (selectedProvider.value) {
    selectedProvider.value.selectedModels = selectedProvider.value.models.map(m => m.id)
    // 自动保存配置
    handleSaveModelConfigs()
  }
}

// 清空模型选择
const clearAllModels = () => {
  if (selectedProvider.value) {
    selectedProvider.value.selectedModels = []
    // 自动保存配置
    handleSaveModelConfigs()
  }
}

// 保存所有模型配置
const handleSaveModelConfigs = () => {
  settingsStore.saveModelConfigs()
  
  // 同步更新localStorage中的模型配置，供LLM页面使用
  const modelProvidersForLLM = modelProviders.value.map(provider => ({
    ...provider,
    models: provider.models.map(model => ({
      ...model,
      enabled: provider.selectedModels?.includes(model.id) || false
    }))
  }))
  
  localStorage.setItem('modelProviders', JSON.stringify(modelProvidersForLLM))
  
  ElMessage.success('模型服务配置已保存，AI问答页面将同步更新')
}
</script>

<style scoped>
.model-service-settings {
  height: 100%;
}

.settings-layout {
  display: flex;
  height: 100%;
  gap: 20px;
}

/* 左侧服务商菜单 */
.provider-menu {
  width: 300px;
  flex-shrink: 0;
}

.menu-card {
  height: 100%;
}

.menu-header h3 {
  margin: 0;
  color: #303133;
}

.provider-menu-list {
  border: none;
}

.provider-menu-item {
  height: auto !important;
  padding: 0 !important;
  margin-bottom: 8px;
}

.menu-item-content {
  width: 100%;
  padding: 12px 16px;
}

.provider-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 4px;
}

.provider-name {
  font-weight: 500;
  color: #303133;
}

.provider-status {
  margin-left: 8px;
}

.provider-models-count {
  font-size: 12px;
  color: #909399;
}

/* 选中状态下的模型数量文字 */
.provider-menu-item.is-active .provider-models-count {
  color: #ffffff;
}

/* 右侧配置区域 */
.provider-config-area {
  flex: 1;
  min-width: 0;
}

.config-card {
  height: 100%;
}

.config-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.header-left h2 {
  margin: 0;
  color: #303133;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.no-selection {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 400px;
}

/* 配置区域 */
.provider-config {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.config-section {
  border: 1px solid #ebeef5;
  border-radius: 8px;
  padding: 20px;
}

.config-section h3 {
  margin: 0 0 16px 0;
  color: #303133;
  font-size: 16px;
}

.config-form {
  margin-top: 16px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.model-actions {
  display: flex;
  gap: 8px;
}

/* 模型网格 */
.models-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
  max-height: 400px;
  overflow-y: auto;
  padding: 8px;
}

.model-card {
  border: 1px solid #ebeef5;
  border-radius: 6px;
  padding: 16px;
  transition: all 0.3s;
  background: #fafafa;
}

.model-card:hover {
  border-color: #409eff;
  background: #f0f9ff;
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.2);
}

.model-checkbox {
  width: 100%;
}

.model-info {
  margin-left: 24px;
}

.model-name {
  font-weight: 500;
  color: #303133;
  margin-bottom: 4px;
}

.model-description {
  color: #606266;
  font-size: 13px;
  margin-bottom: 8px;
  line-height: 1.4;
}

.model-meta {
  display: flex;
  align-items: center;
  gap: 8px;
}

.model-context {
  font-size: 12px;
  color: #909399;
}

.disabled-notice {
  padding: 20px;
  text-align: center;
}

/* 禁用状态下的模型预览 */
.models-preview {
  position: relative;
}

.models-preview .model-card.disabled {
  opacity: 0.6;
  pointer-events: none;
  background: #f5f7fa;
}

.models-preview .model-card.disabled .model-name {
  color: #909399;
}

.models-preview .model-card.disabled .model-description {
  color: #c0c4cc;
}

.disabled-overlay {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  z-index: 10;
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .settings-layout {
    flex-direction: column;
    height: auto;
  }
  
  .provider-menu {
    width: 100%;
  }
  
  .provider-menu-list {
    display: flex;
    overflow-x: auto;
    white-space: nowrap;
  }
  
  .provider-menu-item {
    flex-shrink: 0;
    margin-right: 8px;
  }
  
  .models-grid {
    grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  }
}

@media (max-width: 768px) {
  .config-header {
    flex-direction: column;
    gap: 12px;
    align-items: stretch;
  }
  
  .header-actions {
    justify-content: center;
  }
  
  .models-grid {
    grid-template-columns: 1fr;
  }
}
</style>