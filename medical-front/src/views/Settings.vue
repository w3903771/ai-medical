<template>
  <div class="settings-page">
    <!-- 页面头部 -->
    <div class="page-header">
      <h1>系统设置</h1>
      <p>管理账号信息、数据和系统配置</p>
    </div>

    <!-- 引入模块化设置组件 -->
    <SettingsIndex />
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useSettingsStore } from '@/stores/settings'
import SettingsIndex from './settings/index.vue'

const settingsStore = useSettingsStore()

// 组件挂载时初始化
onMounted(() => {
  // 初始化设置
  settingsStore.initSettings()
})
</script>

<style scoped>
.settings-page {
  padding: 20px;
  height: 100%;
}

.page-header {
  margin-bottom: 20px;
}

.page-header h1 {
  font-size: 24px;
  margin-bottom: 8px;
}

.page-header p {
  color: var(--text-secondary);
}
</style>