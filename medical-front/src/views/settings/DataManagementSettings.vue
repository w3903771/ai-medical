<template>
  <div class="data-management-settings">
    <el-card class="section-card" shadow="never">
      <template #header>
        <h2>数据管理</h2>
      </template>
      
      <el-form
        ref="dataFormRef"
        :model="dataForm"
        label-width="140px"
        class="data-form"
      >
        <!-- 仅保留数据存储位置；默认灰色不可编辑，点击“修改”后可编辑 -->
        <el-form-item label="数据存储位置">
          <el-input
            v-model="dataForm.storagePath"
            :disabled="!isEditingStoragePath"
            placeholder="数据存储路径"
            class="readonly-input"
          >
            <template #append>
              <el-button v-if="!isEditingStoragePath" @click="enableEditStoragePath">修改</el-button>
              <el-button v-else type="primary" @click="saveStoragePath">保存</el-button>
            </template>
          </el-input>
        </el-form-item>

        <el-divider content-position="left">其他功能</el-divider>

        <!-- 应用日志路径（打开） -->
        <el-form-item label="应用日志路径">
          <el-input v-model="dataForm.logPath" disabled class="readonly-input">
            <template #append>
              <el-button @click="handleOpenPath(dataForm.logPath)">打开</el-button>
            </template>
          </el-input>
        </el-form-item>

        <!-- 知识库目录（打开） -->
        <el-form-item label="知识库目录">
          <el-input v-model="dataForm.kbPath" disabled class="readonly-input">
            <template #append>
              <el-button @click="handleOpenPath(dataForm.kbPath)">打开</el-button>
            </template>
          </el-input>
        </el-form-item>

        <!-- 清除缓存（大小） -->
        <el-form-item label="清除缓存">
          <el-button type="warning" @click="handleClearCache">
            清除缓存（{{ Number(storageInfo.cacheSizeMB || 0).toFixed(1) }} MB）
          </el-button>
        </el-form-item>

        <!-- 重置 -->
        <el-form-item label="重置">
          <el-button type="danger" @click="handleResetSettings">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { useSettingsStore } from '../../stores/settings'

const settingsStore = useSettingsStore()
const dataForm = computed(() => settingsStore.dataForm)
const storageInfo = computed(() => settingsStore.storageInfo)

const dataFormRef = ref(null)
const isEditingStoragePath = ref(false)

// 启用编辑存储路径
const enableEditStoragePath = () => {
  isEditingStoragePath.value = true
}

// 保存存储路径并恢复为不可编辑
const saveStoragePath = () => {
  settingsStore.saveDataSettings()
  isEditingStoragePath.value = false
  ElMessage.success('数据存储位置已保存')
}

// 打开本地路径（浏览器环境可能受限）
const handleOpenPath = (path) => {
  try {
    const url = path.startsWith('file:///') ? path : `file:///${path}`
    window.open(url)
  } catch (e) {
    ElMessage.info('打开本地路径功能需要桌面环境支持')
  }
}

// 清除缓存
const handleClearCache = () => {
  settingsStore.clearCache && settingsStore.clearCache()
  ElMessage.success('缓存已清除')
}

// 重置设置
const handleResetSettings = () => {
  settingsStore.resetDataSettings && settingsStore.resetDataSettings()
  ElMessage.info('数据管理设置已重置')
}
</script>

<style scoped>
.data-management-settings {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.section-card {
  margin-bottom: 0;
}

.data-form {
  max-width: 700px;
}

.readonly-input :deep(.el-input__inner) {
  color: var(--el-text-color-secondary);
}

/* 旧的统计与操作区域已移除 */
</style>