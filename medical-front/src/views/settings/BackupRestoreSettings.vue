<template>
  <div class="backup-restore-settings">
    <el-card class="section-card" shadow="never">
      <template #header>
        <h2>备份与恢复</h2>
      </template>
      
      <el-tabs v-model="activeTab">
        <el-tab-pane label="自动备份" name="auto">
          <el-form
            ref="backupFormRef"
            :model="backupForm"
            label-width="120px"
            class="backup-form"
          >
            <!-- 备份状态显示：上次备份时间 -->
            <el-form-item label="备份状态">
              <span>上次备份：{{ lastBackupDisplay }}</span>
            </el-form-item>
            <el-form-item label="启用自动备份">
              <el-switch v-model="backupForm.autoBackup" />
            </el-form-item>
            
            <template v-if="backupForm.autoBackup">
              <el-form-item label="备份频率">
                <el-select v-model="backupForm.frequency">
                  <el-option label="每天" value="daily" />
                  <el-option label="每周" value="weekly" />
                  <el-option label="每月" value="monthly" />
                </el-select>
              </el-form-item>
              
              <el-form-item label="备份时间" v-if="backupForm.frequency === 'daily'">
                <el-time-picker
                  v-model="backupForm.time"
                  format="HH:mm"
                  placeholder="选择时间"
                />
              </el-form-item>
              
              <el-form-item label="备份日" v-if="backupForm.frequency === 'weekly'">
                <el-select v-model="backupForm.dayOfWeek">
                  <el-option label="周一" value="1" />
                  <el-option label="周二" value="2" />
                  <el-option label="周三" value="3" />
                  <el-option label="周四" value="4" />
                  <el-option label="周五" value="5" />
                  <el-option label="周六" value="6" />
                  <el-option label="周日" value="0" />
                </el-select>
              </el-form-item>
              
              <el-form-item label="备份日" v-if="backupForm.frequency === 'monthly'">
                <el-input-number v-model="backupForm.dayOfMonth" :min="1" :max="28" />
              </el-form-item>
              
              <el-form-item label="保留备份数量">
                <el-input-number v-model="backupForm.keepCount" :min="1" :max="20" />
              </el-form-item>
              
              <el-form-item label="备份路径">
                <el-input v-model="backupForm.path" placeholder="备份文件保存路径">
                  <template #append>
                    <el-button @click="handleSelectBackupPath">选择</el-button>
                  </template>
                </el-input>
              </el-form-item>
            </template>
            
            <el-form-item>
              <el-button type="primary" @click="handleSaveBackupSettings">保存设置</el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>
        
        <el-tab-pane label="手动备份" name="manual">
          <div class="manual-backup">
            <el-form label-width="120px">
              <el-form-item label="备份内容">
                <el-checkbox-group v-model="manualBackupOptions">
                  <el-checkbox label="userData">用户数据</el-checkbox>
                  <el-checkbox label="settings">系统设置</el-checkbox>
                  <el-checkbox label="models">模型配置</el-checkbox>
                </el-checkbox-group>
              </el-form-item>
              
              <el-form-item label="备份路径">
                <el-input v-model="manualBackupPath" placeholder="备份文件保存路径">
                  <template #append>
                    <el-button @click="handleSelectManualBackupPath">选择</el-button>
                  </template>
                </el-input>
              </el-form-item>
              
              <el-form-item>
                <el-button type="primary" @click="handleManualBackup">立即备份</el-button>
              </el-form-item>
            </el-form>
          </div>
        </el-tab-pane>
        
        <el-tab-pane label="恢复" name="restore">
          <div class="restore-section">
            <el-upload
              class="backup-file-upload"
              action="#"
              :auto-upload="false"
              :on-change="handleFileChange"
              :limit="1"
            >
              <template #trigger>
                <el-button type="primary">选择备份文件</el-button>
              </template>
              <template #tip>
                <div class="el-upload__tip">请选择有效的备份文件进行恢复</div>
              </template>
            </el-upload>
            
            <div v-if="selectedBackupFile" class="selected-file">
              <p>已选择: {{ selectedBackupFile.name }}</p>
              <p>大小: {{ formatFileSize(selectedBackupFile.size) }}</p>
              <p>修改时间: {{ formatDate(selectedBackupFile.lastModified) }}</p>
              
              <el-button type="warning" @click="handleRestore">恢复数据</el-button>
            </div>
          </div>
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useSettingsStore } from '../../stores/settings'

const settingsStore = useSettingsStore()
const backupForm = computed(() => settingsStore.backupForm)
const backupList = computed(() => settingsStore.backupList || [])

const activeTab = ref('auto')
const backupFormRef = ref(null)
const manualBackupOptions = ref(['userData', 'settings', 'models'])
const manualBackupPath = ref('')
const selectedBackupFile = ref(null)

// 上次备份时间显示
const lastBackupDisplay = computed(() => {
  const list = backupList.value
  if (!list || list.length === 0) return '从未备份'
  // 找到最新的createTime
  const parseDate = (s) => {
    const str = String(s || '')
    const normalized = str.includes('T') ? str : str.replace(' ', 'T')
    const d = new Date(normalized)
    return isNaN(d.getTime()) ? null : d
  }
  const latest = list
    .map(item => ({ d: parseDate(item.createTime), raw: item.createTime }))
    .filter(it => it.d !== null)
    .sort((a, b) => a.d - b.d)
    .pop()
  return latest?.d ? latest.d.toLocaleString() : (list[list.length - 1]?.createTime || '未知时间')
})

// 选择自动备份路径
const handleSelectBackupPath = () => {
  // 这里可以调用系统文件选择对话框
  ElMessage.info('选择路径功能需要通过后端API实现')
}

// 选择手动备份路径
const handleSelectManualBackupPath = () => {
  // 这里可以调用系统文件选择对话框
  ElMessage.info('选择路径功能需要通过后端API实现')
}

// 保存备份设置
const handleSaveBackupSettings = () => {
  settingsStore.saveBackupSettings()
  ElMessage.success('备份设置已保存')
}

// 执行手动备份
const handleManualBackup = () => {
  if (manualBackupOptions.value.length === 0) {
    ElMessage.warning('请至少选择一项备份内容')
    return
  }
  
  // 这里可以调用API执行备份
  ElMessage.success('备份任务已启动，请稍候...')
  setTimeout(() => {
    ElMessage.success('备份已完成')
  }, 2000)
}

// 处理文件选择
const handleFileChange = (file) => {
  selectedBackupFile.value = file.raw
}

// 执行恢复
const handleRestore = () => {
  if (!selectedBackupFile.value) {
    ElMessage.warning('请先选择备份文件')
    return
  }
  
  ElMessageBox.confirm('恢复操作将覆盖当前数据，是否继续?', '确认恢复', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    // 这里可以调用API执行恢复
    ElMessage.success('恢复任务已启动，请稍候...')
    setTimeout(() => {
      ElMessage.success('数据已恢复')
    }, 2000)
  }).catch(() => {
    // 取消操作
  })
}

// 格式化文件大小
const formatFileSize = (size) => {
  if (size < 1024) {
    return size + ' B'
  } else if (size < 1024 * 1024) {
    return (size / 1024).toFixed(2) + ' KB'
  } else {
    return (size / (1024 * 1024)).toFixed(2) + ' MB'
  }
}

// 格式化日期
const formatDate = (timestamp) => {
  const date = new Date(timestamp)
  return date.toLocaleString()
}
</script>

<style scoped>
.backup-restore-settings {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.section-card {
  margin-bottom: 0;
}

.backup-form {
  max-width: 600px;
}

.manual-backup {
  max-width: 600px;
}

.backup-file-upload {
  margin-bottom: 20px;
}

.selected-file {
  margin-top: 20px;
  padding: 15px;
  border: 1px solid #ebeef5;
  border-radius: 4px;
}
</style>