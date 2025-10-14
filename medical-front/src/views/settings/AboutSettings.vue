<template>
  <div class="about-section">
    <el-card class="section-card" shadow="never">
      <template #header>
        <h2>关于系统</h2>
      </template>
      <div class="about-content">
        <div class="logo-container">
          <el-icon :size="80" color="#409EFF"><InfoFilled /></el-icon>
        </div>
        <h3>医疗智能辅助系统</h3>
        <p>版本: 1.0.0</p>
        <p>构建日期: 2025-10-01</p>
        <p>版权所有 © 2025 医疗智能辅助系统团队</p>
        <div class="about-links">
          <el-button type="primary" link>检查更新</el-button>
          <el-button type="primary" link>查看文档</el-button>
          <el-button type="primary" link>联系支持</el-button>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
// 无需导入任何内容，这是一个纯静态组件
</script>

<style scoped>
.about-section {
  padding: 20px;
  max-width: 800px;
  margin: 0 auto;
}

.section-card {
  margin-bottom: 20px;
  border-radius: 8px;
}

.about-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  padding: 20px 0;
}

.logo-container {
  margin-bottom: 20px;
}

.system-logo {
  width: 120px;
  height: 120px;
}

.about-links {
  margin-top: 20px;
  display: flex;
  gap: 16px;
  justify-content: center;
}
</style>