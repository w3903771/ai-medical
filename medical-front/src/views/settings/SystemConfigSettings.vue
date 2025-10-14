<template>
  <div class="system-config-settings">
    <el-card class="section-card" shadow="never">
      <template #header>
        <h2>系统配置</h2>
      </template>
      
      <el-form
        ref="systemFormRef"
        :model="systemConfig"
        label-width="120px"
        class="system-form"
      >
        <el-form-item label="界面主题">
          <el-select v-model="systemConfig.theme">
            <el-option label="浅色" value="light" />
            <el-option label="深色" value="dark" />
            <el-option label="跟随系统" value="auto" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="界面语言">
          <el-select v-model="systemConfig.language">
            <el-option label="简体中文" value="zh-CN" />
            <el-option label="English" value="en-US" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="自动更新">
          <el-switch v-model="systemConfig.autoUpdate" />
        </el-form-item>
        
        <el-form-item label="开机自启">
          <el-switch v-model="systemConfig.autoStart" />
        </el-form-item>
        
        <el-form-item label="最小化到托盘">
          <el-switch v-model="systemConfig.minimizeToTray" />
        </el-form-item>
        
        <el-form-item label="代理设置">
          <el-radio-group v-model="systemConfig.proxyType">
            <el-radio label="none">不使用代理</el-radio>
            <el-radio label="system">使用系统代理</el-radio>
            <el-radio label="manual">手动设置</el-radio>
          </el-radio-group>
        </el-form-item>
        
        <template v-if="systemConfig.proxyType === 'manual'">
          <el-form-item label="代理地址">
            <el-input v-model="systemConfig.proxyHost" placeholder="例如: 127.0.0.1" />
          </el-form-item>
          
          <el-form-item label="代理端口">
            <el-input-number v-model="systemConfig.proxyPort" :min="1" :max="65535" />
          </el-form-item>
          
          <el-form-item label="需要认证">
            <el-switch v-model="systemConfig.proxyAuth" />
          </el-form-item>
          
          <template v-if="systemConfig.proxyAuth">
            <el-form-item label="用户名">
              <el-input v-model="systemConfig.proxyUsername" />
            </el-form-item>
            
            <el-form-item label="密码">
              <el-input v-model="systemConfig.proxyPassword" type="password" show-password />
            </el-form-item>
          </template>
        </template>
        
        <el-divider />
        
        <el-form-item>
          <el-button type="primary" @click="handleSaveSystemConfig">保存配置</el-button>
          <el-button @click="resetSystemConfig">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { useSettingsStore } from '@/stores/settings'

const settingsStore = useSettingsStore()
const systemConfig = settingsStore.systemConfig
const systemFormRef = ref(null)

// 保存系统配置
const handleSaveSystemConfig = () => {
  settingsStore.saveSystemConfig()
  ElMessage.success('系统配置已保存')
}

// 重置系统配置
const resetSystemConfig = () => {
  settingsStore.resetSystemConfig()
  ElMessage.info('系统配置已重置')
}
</script>

<style scoped>
.system-config-settings {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.section-card {
  margin-bottom: 0;
}

.system-form {
  max-width: 600px;
}
</style>