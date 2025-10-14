<template>
  <div class="dashboard">
    <!-- 欢迎区域 -->
    <div class="welcome-section">
      <el-card class="welcome-card">
        <div class="welcome-content">
          <div class="welcome-text">
            <h1>欢迎回来！</h1>
            <p>今天是 {{ currentDate }}，让我们一起关注您的健康状况</p>
          </div>
          <div class="welcome-icon">
            <el-icon size="60" color="#409eff"><User /></el-icon>
          </div>
        </div>
      </el-card>
    </div>

    <!-- 关键指标卡片 -->
    <div class="metrics-section">
      <h2 class="section-title">关键健康指标</h2>
      <el-row :gutter="20">
        <el-col :xs="24" :sm="12" :md="8" v-for="metric in healthMetrics" :key="metric.id">
          <el-card class="metric-card" shadow="hover">
            <div class="metric-content">
              <div class="metric-icon" :style="{ backgroundColor: metric.color }">
                <el-icon size="24" color="white">
                  <component :is="metric.icon" />
                </el-icon>
              </div>
              <div class="metric-info">
                <h3>{{ metric.name }}</h3>
                <div class="metric-value">
                  <span class="value">{{ metric.value }}</span>
                  <span class="unit">{{ metric.unit }}</span>
                </div>
                <div class="metric-trend" :class="metric.trend">
                  <el-icon>
                    <component :is="metric.trend === 'up' ? 'ArrowUp' : metric.trend === 'down' ? 'ArrowDown' : 'Minus'" />
                  </el-icon>
                  <span>{{ metric.change }}</span>
                </div>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- 最近异常和当前用药 -->
    <el-row :gutter="20" class="info-section">
      <!-- 最近异常 -->
      <el-col :xs="24" :md="12">
        <el-card class="info-card">
          <template #header>
            <div class="card-header">
              <el-icon color="#f56c6c"><Warning /></el-icon>
              <span>最近异常</span>
              <div class="slider-container">
                <span class="slider-label">显示数量:</span>
                <el-slider
                  v-model="abnormalDisplayCount"
                  :min="1"
                  :max="maxAbnormalCount"
                  :step="1"
                  :disabled="recentAbnormals.length === 0"
                  @change="handleAbnormalCountChange"
                />
              </div>
            </div>
          </template>
          <div class="abnormal-list">
            <div v-for="abnormal in displayedAbnormals" :key="abnormal.id" class="abnormal-item">
              <div class="abnormal-indicator">
                <el-tag :type="abnormal.severity" size="small">{{ abnormal.indicator }}</el-tag>
              </div>
              <div class="abnormal-info">
                <div class="abnormal-value">{{ abnormal.value }} {{ abnormal.unit }}</div>
                <div class="abnormal-date">{{ abnormal.date }}</div>
                <div class="abnormal-desc">{{ abnormal.description }}</div>
              </div>
            </div>
            <div v-if="recentAbnormals.length === 0" class="no-data">
              <el-icon color="#67c23a"><CircleCheckFilled /></el-icon>
              <span>暂无异常数据</span>
            </div>
          </div>
        </el-card>
      </el-col>

      <!-- 当前用药 -->
      <el-col :xs="24" :md="12">
        <el-card class="info-card">
          <template #header>
            <div class="card-header">
              <el-icon color="#409eff"><FirstAidKit /></el-icon>
              <span>当前用药</span>
            </div>
          </template>
          <div class="medication-list">
            <div v-for="med in currentMedications" :key="med.id" class="medication-item">
              <div class="medication-name">{{ med.name }}</div>
              <div class="medication-dose">{{ med.dose }} - {{ med.frequency }}</div>
            </div>
            <div v-if="currentMedications.length === 0" class="no-data">
              <el-icon color="#909399"><Document /></el-icon>
              <span>暂无用药记录</span>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 生活建议 -->
    <div class="suggestions-section">
      <el-card class="suggestions-card">
        <template #header>
          <div class="card-header">
            <el-icon color="#67c23a"><Lightning /></el-icon>
            <span>今日健康建议</span>
          </div>
        </template>
        <div class="suggestions-content">
          <el-row :gutter="16">
            <el-col :xs="24" :md="8" v-for="suggestion in healthSuggestions" :key="suggestion.id">
              <div class="suggestion-item">
                <div class="suggestion-icon" :style="{ backgroundColor: suggestion.color }">
                  <el-icon size="20" color="white">
                    <component :is="suggestion.icon" />
                  </el-icon>
                </div>
                <div class="suggestion-content">
                  <h4>{{ suggestion.title }}</h4>
                  <p>{{ suggestion.content }}</p>
                </div>
              </div>
            </el-col>
          </el-row>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { 
  User, 
  Warning, 
  CircleCheckFilled, 
  Document, 
  FirstAidKit, 
  Lightning,
  ArrowUp,
  ArrowDown,
  Minus
} from '@element-plus/icons-vue'

// 当前日期
const currentDate = computed(() => {
  return new Date().toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    weekday: 'long'
  })
})

// 健康指标数据
const healthMetrics = ref([
  {
    id: 1,
    name: '体重',
    value: '68.5',
    unit: 'kg',
    change: '↓0.5kg',
    trend: 'down',
    color: '#409eff',
    icon: 'Scale'
  },
  {
    id: 2,
    name: '血压',
    value: '120/80',
    unit: 'mmHg',
    change: '正常',
    trend: 'stable',
    color: '#67c23a',
    icon: 'Monitor'
  },
  {
    id: 3,
    name: '血糖',
    value: '5.8',
    unit: 'mmol/L',
    change: '↑0.2',
    trend: 'up',
    color: '#e6a23c',
    icon: 'DataAnalysis'
  }
])

// 最近异常数据
const recentAbnormals = ref([
  {
    id: 1,
    indicator: '血糖',
    value: '8.2',
    unit: 'mmol/L',
    date: '2024-01-15',
    severity: 'warning',
    description: '餐后血糖偏高，建议减少碳水摄入'
  },
  {
    id: 2,
    indicator: '血压',
    value: '145/95',
    unit: 'mmHg',
    date: '2024-01-12',
    severity: 'danger',
    description: '血压明显升高，请遵医嘱服用降压药'
  },
  {
    id: 3,
    indicator: '心率',
    value: '105',
    unit: '次/分',
    date: '2024-01-10',
    severity: 'warning',
    description: '静息心率偏高，建议减少咖啡因摄入，保持充分休息'
  },
  {
    id: 4,
    indicator: '胆固醇',
    value: '6.2',
    unit: 'mmol/L',
    date: '2024-01-05',
    severity: 'warning',
    description: '总胆固醇偏高，建议调整饮食结构，减少高脂肪食物摄入'
  },
  {
    id: 5,
    indicator: '尿酸',
    value: '480',
    unit: 'μmol/L',
    date: '2023-12-28',
    severity: 'danger',
    description: '尿酸水平明显升高，请注意饮食控制，避免高嘌呤食物'
  }
])

// 异常数据显示相关
const abnormalDisplayCount = ref(2) // 默认显示2条
const maxAbnormalCount = computed(() => Math.max(recentAbnormals.value.length, 1))
const displayedAbnormals = computed(() => {
  return recentAbnormals.value.slice(0, abnormalDisplayCount.value)
})

// 处理滑块变化
const handleAbnormalCountChange = (value) => {
  abnormalDisplayCount.value = value
}

// 当前用药
const currentMedications = ref([
  {
    id: 1,
    name: '二甲双胍',
    dose: '500mg',
    frequency: '每日2次'
  },
  {
    id: 2,
    name: '阿司匹林',
    dose: '100mg',
    frequency: '每日1次'
  }
])

// 健康建议
const healthSuggestions = ref([
  {
    id: 1,
    title: '饮食建议',
    content: '建议减少糖分摄入，多食用蔬菜和优质蛋白',
    icon: 'Food',
    color: '#67c23a'
  },
  {
    id: 2,
    title: '运动建议',
    content: '每天进行30分钟中等强度运动，如快走或游泳',
    icon: 'Bicycle',
    color: '#409eff'
  },
  {
    id: 3,
    title: '作息建议',
    content: '保持规律作息，每晚11点前入睡，保证7-8小时睡眠',
    icon: 'Moon',
    color: '#9c27b0'
  }
])
</script>

<style scoped>
.dashboard {
  padding: 0;
}

.welcome-section {
  margin-bottom: 24px;
}

.welcome-card {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  color: white;
}

.welcome-card :deep(.el-card__body) {
  padding: 30px;
}

.welcome-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.welcome-text h1 {
  margin: 0 0 8px 0;
  font-size: 28px;
  font-weight: 600;
}

.welcome-text p {
  margin: 0;
  font-size: 16px;
  opacity: 0.9;
}

.section-title {
  margin: 0 0 16px 0;
  font-size: 20px;
  font-weight: 600;
  color: var(--text-primary);
}

.metrics-section {
  margin-bottom: 24px;
}

.metric-card {
  height: 120px;
  transition: all 0.3s ease;
}

.metric-card:hover {
  transform: translateY(-4px);
}

.metric-content {
  display: flex;
  align-items: center;
  height: 100%;
  padding-top: 0;
  margin-top: -10px;
}

.metric-icon {
  width: 60px;
  height: 60px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 16px;
}

.metric-info h3 {
  margin: 0 0 8px 0;
  font-size: 16px;
  color: var(--text-primary);
}

.metric-value {
  display: flex;
  align-items: baseline;
  margin-bottom: 4px;
}

.metric-value .value {
  font-size: 24px;
  font-weight: 600;
  color: var(--text-primary);
  margin-right: 4px;
}

.metric-value .unit {
  font-size: 14px;
  color: var(--text-secondary);
}

.metric-trend {
  display: flex;
  align-items: center;
  font-size: 12px;
}

.metric-trend.up {
  color: var(--danger-color);
}

.metric-trend.down {
  color: var(--success-color);
}

.metric-trend.stable {
  color: var(--text-secondary);
}

.info-section {
  margin-bottom: 24px;
}

.info-card {
  height: 300px;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
}

.slider-container {
  display: flex;
  align-items: center;
  margin-left: auto;
  width: 200px;
}

.slider-label {
  font-size: 12px;
  color: var(--text-secondary);
  margin-right: 8px;
  white-space: nowrap;
}

.slider-container .el-slider {
  margin-right: 0;
  margin-top: 0;
  margin-bottom: 0;
}

.abnormal-list,
.medication-list {
  max-height: 220px;
  overflow-y: auto;
}

.abnormal-item,
.medication-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 0;
  border-bottom: 1px solid var(--border-color);
}

.abnormal-item:last-child,
.medication-item:last-child {
  border-bottom: none;
}

.abnormal-info {
  text-align: right;
}

.abnormal-value {
  font-weight: 600;
  color: var(--text-primary);
}

.abnormal-date {
  font-size: 12px;
  color: var(--text-secondary);
}

.abnormal-desc {
  font-size: 13px;
  color: var(--text-regular);
  margin-top: 4px;
  line-height: 1.4;
}

.medication-name {
  font-weight: 600;
  color: var(--text-primary);
}

.medication-dose {
  font-size: 14px;
  color: var(--text-secondary);
}

.no-data {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 120px;
  color: var(--text-secondary);
  gap: 8px;
}

.suggestions-section {
  margin-bottom: 24px;
}

.suggestions-card {
  min-height: 200px;
}

.suggestion-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 16px;
  background: #f8f9fa;
  border-radius: 8px;
  margin-bottom: 16px;
}

.suggestion-icon {
  width: 40px;
  height: 40px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.suggestion-content h4 {
  margin: 0 0 8px 0;
  font-size: 16px;
  color: var(--text-primary);
}

.suggestion-content p {
  margin: 0;
  font-size: 14px;
  color: var(--text-regular);
  line-height: 1.5;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .welcome-content {
    flex-direction: column;
    text-align: center;
    gap: 16px;
  }
  
  .metric-card {
    margin-bottom: 16px;
  }
  
  .info-section {
    margin-bottom: 16px;
  }
  
  .info-card {
    height: auto;
    margin-bottom: 16px;
  }
  
  .suggestion-item {
    flex-direction: column;
    text-align: center;
  }
}
</style>