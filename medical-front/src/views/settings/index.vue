<template>
  <div class="settings-container">
    <div class="settings-sidebar">
      <el-menu
        :default-active="activeMenu"
        class="settings-menu"
        @select="handleMenuSelect"
      >
        <el-menu-item index="account">
          <el-icon><User /></el-icon>
          <span>账号管理</span>
        </el-menu-item>
        <el-menu-item index="model">
          <el-icon><Connection /></el-icon>
          <span>模型服务</span>
        </el-menu-item>
        <el-menu-item index="data">
          <el-icon><DataAnalysis /></el-icon>
          <span>数据管理</span>
        </el-menu-item>
        <el-menu-item index="backup">
          <el-icon><CopyDocument /></el-icon>
          <span>备份恢复</span>
        </el-menu-item>
        <el-menu-item index="export">
          <el-icon><CopyDocument /></el-icon>
          <span>导出设置</span>
        </el-menu-item>
        <el-menu-item index="websearch">
          <el-icon><Connection /></el-icon>
          <span>网络搜索</span>
        </el-menu-item>
        <el-menu-item index="docproc">
          <el-icon><CopyDocument /></el-icon>
          <span>文档处理</span>
        </el-menu-item>
        <el-menu-item index="system">
          <el-icon><Setting /></el-icon>
          <span>系统配置</span>
        </el-menu-item>
        <el-menu-item index="about">
          <el-icon><InfoFilled /></el-icon>
          <span>关于系统</span>
        </el-menu-item>
      </el-menu>
    </div>
    
    <div class="settings-content">
      <keep-alive>
        <component :is="currentComponent" />
      </keep-alive>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, markRaw, h } from 'vue'
import { useSettingsStore } from '@/stores/settings'
import { 
  User, 
  Connection, 
  DataAnalysis, 
  CopyDocument, 
  Setting, 
  InfoFilled 
} from '@element-plus/icons-vue'

// 导入子组件
import AccountSettings from './AccountSettings.vue'
import ModelServiceSettings from './ModelServiceSettings.vue'
import DataManagementSettings from './DataManagementSettings.vue'
import BackupRestoreSettings from './BackupRestoreSettings.vue'
import ExportSettings from './ExportSettings.vue'
import WebSearchSettings from './WebSearchSettings.vue'
import DocProcessingSettings from './DocProcessingSettings.vue'
import SystemConfigSettings from './SystemConfigSettings.vue'
import AboutSettings from './AboutSettings.vue'

// 使用 markRaw 包装组件以避免不必要的代理
const components = {
  account: markRaw(AccountSettings),
  model: markRaw(ModelServiceSettings),
  data: markRaw(DataManagementSettings),
  backup: markRaw(BackupRestoreSettings),
  export: markRaw(ExportSettings),
  websearch: markRaw(WebSearchSettings),
  docproc: markRaw(DocProcessingSettings),
  system: markRaw(SystemConfigSettings),
  about: markRaw(AboutSettings)
};

const settingsStore = useSettingsStore()
const activeMenu = ref('account')
const currentComponent = computed(() => components[activeMenu.value])

// 处理菜单选择
const handleMenuSelect = (key) => {
  activeMenu.value = key
}

// 组件挂载时初始化设置
onMounted(() => {
  settingsStore.initSettings()
})
</script>

<style scoped>
.settings-container {
  display: flex;
  height: 100%;
  background-color: #f5f7fa;
}

.settings-sidebar {
  width: 220px;
  background-color: #fff;
  border-right: 1px solid #e6e6e6;
}

.settings-menu {
  border-right: none;
}

.settings-content {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
}

.about-section {
  max-width: 600px;
}

.about-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
}

.logo-container {
  margin-bottom: 20px;
}

.system-logo {
  width: 100px;
  height: 100px;
}

.about-links {
  margin-top: 20px;
  display: flex;
  gap: 10px;
}
</style>