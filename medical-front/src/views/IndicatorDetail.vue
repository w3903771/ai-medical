<template>
  <div class="indicator-detail-container">
    <el-card class="header-card">
      <div class="header-content">
        <div class="title-section">
          <h2>{{ indicatorName }}</h2>
          <el-tag :type="indicatorType" class="ml-2">{{ categoryName }}</el-tag>
        </div>
        <div class="actions">
          <el-button @click="goBack" icon="ArrowLeft">返回</el-button>
        </div>
      </div>
    </el-card>

    <div class="content-container">
      <el-row :gutter="20">
        <el-col :span="6">
          <el-card class="menu-card">
            <template #header>
              <div class="card-header">
                <span>指标详情</span>
              </div>
            </template>
            <el-menu
              :default-active="activeMenu"
              class="detail-menu"
              @select="handleMenuSelect"
            >
              <el-menu-item index="intro">
                <el-icon><InfoFilled /></el-icon>
                <span>科普介绍</span>
              </el-menu-item>
              <el-menu-item index="history">
                <el-icon><Histogram /></el-icon>
                <span>历史数据</span>
              </el-menu-item>
              <el-menu-item index="reference">
                <el-icon><Document /></el-icon>
                <span>参考范围</span>
              </el-menu-item>
              <el-menu-item index="advice">
                <el-icon><ChatLineRound /></el-icon>
                <span>健康建议</span>
              </el-menu-item>
            </el-menu>
          </el-card>
        </el-col>
        <el-col :span="18">
          <el-card class="detail-card" v-loading="loading">
            <!-- 科普介绍 -->
            <div v-if="activeMenu === 'intro'" class="intro-content">
              <h3>{{ indicatorName }}介绍</h3>
              <div class="intro-text">
                <p>{{ introductionText }}</p>
              </div>
              <div class="measurement-info">
                <h4>测量方法</h4>
                <p>{{ measurementMethod }}</p>
              </div>
              <div class="importance-info">
                <h4>临床意义</h4>
                <p>{{ clinicalSignificance }}</p>
              </div>
            </div>

            <!-- 历史数据 -->
            <div v-if="activeMenu === 'history'" class="history-content">
              <div class="chart-filters">
                <el-date-picker
                  v-model="dateRange"
                  type="daterange"
                  range-separator="至"
                  start-placeholder="开始日期"
                  end-placeholder="结束日期"
                  format="YYYY年MM月DD日"
                  value-format="YYYY-MM-DD"
                  :shortcuts="dateShortcuts"
                  @change="handleDateRangeChange"
                />
              </div>
              <div class="chart-container">
                <div ref="chartRef" style="width: 100%; height: 400px"></div>
              </div>
              <div class="data-table" style="max-height: 300px; overflow-y: auto;">
                <el-table :data="historyData" style="width: 100%" stripe border>
                  <el-table-column prop="date" label="日期" width="180" />
                  <el-table-column prop="value" label="数值" width="120">
                    <template #default="{ row }">
                      <span :class="getValueClass(row)">{{ row.value }}</span>
                    </template>
                  </el-table-column>
                  <el-table-column prop="unit" label="单位" width="80" />
                  <el-table-column prop="status" label="状态" width="100">
                    <template #default="{ row }">
                      <el-tag :type="getStatusType(row)">{{ getStatusText(row) }}</el-tag>
                    </template>
                  </el-table-column>
                  <el-table-column prop="source" label="数据来源" />
                  <el-table-column prop="note" label="备注" />
                </el-table>
              </div>
            </div>

            <!-- 参考范围 -->
            <div v-if="activeMenu === 'reference'" class="reference-content">
              <h3>参考范围</h3>
              <el-descriptions border>
                <el-descriptions-item label="正常范围">{{ referenceRange }}</el-descriptions-item>
                <el-descriptions-item label="单位">{{ unit }}</el-descriptions-item>
                <el-descriptions-item label="偏高表示">{{ highMeaning }}</el-descriptions-item>
                <el-descriptions-item label="偏低表示">{{ lowMeaning }}</el-descriptions-item>
              </el-descriptions>
            </div>

            <!-- 健康建议 -->
            <div v-if="activeMenu === 'advice'" class="advice-content">
              <h3>健康建议</h3>
              <el-alert
                v-if="latestStatus === 'high'"
                title="指标偏高"
                type="warning"
                :description="highAdvice"
                show-icon
              />
              <el-alert
                v-if="latestStatus === 'low'"
                title="指标偏低"
                type="warning"
                :description="lowAdvice"
                show-icon
              />
              <el-alert
                v-if="latestStatus === 'normal'"
                title="指标正常"
                type="success"
                :description="normalAdvice"
                show-icon
              />
              <div class="general-advice">
                <h4>一般建议</h4>
                <p>{{ generalAdvice }}</p>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import { getIndicator, getDetail, listRecords } from '@/api/indicators'

const route = useRoute()
const router = useRouter()
const indicatorId = computed(() => route.params.id)
const indicatorName = computed(() => route.params.name)
const loading = ref(false)
const activeMenu = ref('intro')
const chartRef = ref(null)
const chart = ref(null)
const dateRange = ref([])
const historyData = ref([])
const categoryName = ref('未分类')
const indicatorType = ref('')

// 日期快捷选项
const dateShortcuts = [
  {
    text: '最近一周',
    value: () => {
      const end = new Date()
      const start = new Date()
      start.setTime(start.getTime() - 3600 * 1000 * 24 * 7)
      return [start, end]
    }
  },
  {
    text: '最近一个月',
    value: () => {
      const end = new Date()
      const start = new Date()
      start.setMonth(start.getMonth() - 1)
      return [start, end]
    }
  },
  {
    text: '最近三个月',
    value: () => {
      const end = new Date()
      const start = new Date()
      start.setMonth(start.getMonth() - 3)
      return [start, end]
    }
  }
]

// 指标详情数据
const introductionText = ref('')
const measurementMethod = ref('')
const clinicalSignificance = ref('')
const referenceRange = ref('')
const unit = ref('')
const highMeaning = ref('')
const lowMeaning = ref('')
const highAdvice = ref('')
const lowAdvice = ref('')
const normalAdvice = ref('')
const generalAdvice = ref('')
const latestStatus = ref('normal')

let refLow = null
let refHigh = null

// 模拟历史数据
const generateMockHistoryData = (indicator) => {
  const today = new Date()
  const data = []
  
  // 生成过去30天的数据
  for (let i = 30; i >= 0; i -= 3) {
    const date = new Date(today)
    date.setDate(today.getDate() - i)
    
    let value, status
    
    // 根据不同指标生成不同范围的值
    switch (indicator) {
      case '体重':
        value = (65 + Math.random() * 10 - 5).toFixed(1)
        status = value > 70 ? 'high' : value < 60 ? 'low' : 'normal'
        break
      case '血压':
        const systolic = Math.floor(120 + Math.random() * 30 - 15)
        const diastolic = Math.floor(80 + Math.random() * 20 - 10)
        value = `${systolic}/${diastolic}`
        status = systolic > 130 || diastolic > 85 ? 'high' : 
                systolic < 100 || diastolic < 60 ? 'low' : 'normal'
        break
      case '血糖':
        value = (5.5 + Math.random() * 3 - 1.5).toFixed(1)
        status = value > 6.1 ? 'high' : value < 3.9 ? 'low' : 'normal'
        break
      case '心率':
        value = Math.floor(70 + Math.random() * 40 - 20)
        status = value > 100 ? 'high' : value < 60 ? 'low' : 'normal'
        break
      case '体温':
        value = (36.8 + Math.random() * 2 - 1).toFixed(1)
        status = value > 37.2 ? 'high' : value < 36.1 ? 'low' : 'normal'
        break
      case '血氧':
        value = Math.floor(97 + Math.random() * 5 - 2)
        status = value < 95 ? 'low' : 'normal'
        break
      default:
        value = Math.floor(Math.random() * 100)
        status = 'normal'
    }
    
    data.push({
      date: date.toISOString().split('T')[0],
      value,
      unit: getUnitByIndicator(indicator),
      status,
      source: i % 9 === 0 ? '医院检查' : '自我监测',
      note: ''
    })
  }
  
  return data
}

const getUnitByIndicator = (indicator) => {
  const units = {
    '体重': 'kg',
    '血压': 'mmHg',
    '血糖': 'mmol/L',
    '心率': '次/分钟',
    '体温': '°C',
    '血氧': '%'
  }
  return units[indicator] || ''
}

// 加载指标详情
const loadIndicatorDetails = async () => {
  loading.value = true
  try {
    const def = await getIndicator(indicatorId.value)
    const cats = Array.isArray(def?.categories) ? def.categories : []
    categoryName.value = cats[0] || '未分类'
    unit.value = def?.unit || ''
    refLow = def?.referenceMin ?? null
    refHigh = def?.referenceMax ?? null
    if (refLow !== null && refHigh !== null) {
      referenceRange.value = `${refLow}-${refHigh}`
    } else {
      referenceRange.value = ''
    }
    const det = await getDetail(indicatorId.value)
    introductionText.value = det?.introductionText || ''
    measurementMethod.value = det?.measurementMethod || ''
    clinicalSignificance.value = det?.clinicalSignificance || ''
    highMeaning.value = det?.highMeaning || ''
    lowMeaning.value = det?.lowMeaning || ''
    highAdvice.value = det?.highAdvice || ''
    lowAdvice.value = det?.lowAdvice || ''
    normalAdvice.value = det?.normalAdvice || ''
    generalAdvice.value = det?.generalAdvice || ''
    const rec = await listRecords(indicatorId.value, {
      page: 1,
      pageSize: 200,
      startDate: dateRange.value?.[0] || undefined,
      endDate: dateRange.value?.[1] || undefined,
    })
    historyData.value = Array.isArray(rec?.items) ? rec.items : []
    if (historyData.value.length > 0) {
      latestStatus.value = historyData.value[historyData.value.length - 1].status || 'normal'
    }
  } finally {
    loading.value = false
    if (activeMenu.value === 'history') {
      nextTick(() => initChart())
    }
  }
}

// 初始化图表
const initChart = () => {
  if (!chartRef.value) return
  
  // 如果已经有图表实例，先销毁
  if (chart.value) {
    chart.value.dispose()
  }
  
  // 创建图表实例
  chart.value = echarts.init(chartRef.value)
  
  // 准备数据
  const dates = historyData.value.map(item => item.date)
  let values = []
  
  // 处理血压特殊情况
  if (indicatorName.value === '血压') {
    const systolicValues = historyData.value.map(item => parseInt(item.value.split('/')[0]))
    const diastolicValues = historyData.value.map(item => parseInt(item.value.split('/')[1]))
    
    // 设置图表选项
    const option = {
      title: {
        text: '血压历史记录'
      },
      tooltip: {
        trigger: 'axis'
      },
      legend: {
        data: ['收缩压', '舒张压']
      },
      xAxis: {
        type: 'category',
        data: dates
      },
      yAxis: {
        type: 'value',
        name: 'mmHg'
      },
      series: [
        {
          name: '收缩压',
          type: 'line',
          data: systolicValues,
          markLine: {
            data: [
              { name: '正常上限', yAxis: 120, lineStyle: { color: '#f56c6c' } },
              { name: '正常下限', yAxis: 90, lineStyle: { color: '#e6a23c' } }
            ]
          }
        },
        {
          name: '舒张压',
          type: 'line',
          data: diastolicValues,
          markLine: {
            data: [
              { name: '正常上限', yAxis: 80, lineStyle: { color: '#f56c6c' } },
              { name: '正常下限', yAxis: 60, lineStyle: { color: '#e6a23c' } }
            ]
          }
        }
      ]
    }
    
    chart.value.setOption(option)
    return
  }
  
  // 其他指标处理
  values = historyData.value.map(item => {
    // 确保值是数字
    const val = parseFloat(item.value)
    return isNaN(val) ? null : val
  })
  
  // 设置参考范围
  let markLines = []
  if (refLow !== null) {
    markLines.push({ name: '下限', yAxis: Number(refLow), lineStyle: { color: '#e6a23c' } })
  }
  if (refHigh !== null) {
    markLines.push({ name: '上限', yAxis: Number(refHigh), lineStyle: { color: '#f56c6c' } })
  }
  
  // 设置图表选项
  const option = {
    title: {
      text: `${indicatorName.value}历史记录`
    },
    tooltip: {
      trigger: 'axis'
    },
    xAxis: {
      type: 'category',
      data: dates
    },
    yAxis: {
      type: 'value',
      name: unit.value
    },
    series: [
      {
        name: indicatorName.value,
        type: 'line',
        data: values,
        markLine: {
          data: markLines
        }
      }
    ]
  }
  
  chart.value.setOption(option)
}

// 处理菜单选择
const handleMenuSelect = (index) => {
  activeMenu.value = index
  
  // 如果选择历史数据，初始化图表
  if (index === 'history') {
    // 使用nextTick确保DOM已更新
    nextTick(() => {
      initChart()
    })
  }
}

// 处理日期范围变化
const handleDateRangeChange = () => {
  if (!dateRange.value || dateRange.value.length !== 2) return
  
  loadIndicatorDetails()
}

// 获取值的样式类
const getValueClass = (row) => {
  if (row.status === 'high') return 'text-danger'
  if (row.status === 'low') return 'text-warning'
  return 'text-success'
}

// 获取状态类型
const getStatusType = (row) => {
  if (row.status === 'high') return 'danger'
  if (row.status === 'low') return 'warning'
  return 'success'
}

// 获取状态文本
const getStatusText = (row) => {
  if (row.status === 'high') return '偏高'
  if (row.status === 'low') return '偏低'
  return '正常'
}

// 返回上一页
const goBack = () => {
  router.back()
}

// 监听路由参数变化
watch(
  () => route.params,
  () => {
    loadIndicatorDetails()
  }
)

onMounted(() => {
  loadIndicatorDetails()
  
  // 监听窗口大小变化，调整图表大小
  window.addEventListener('resize', () => {
    if (chart.value) {
      chart.value.resize()
    }
  })
})
</script>

<style scoped>
.indicator-detail-container {
  padding: 20px;
}

.header-card {
  margin-bottom: 20px;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.title-section {
  display: flex;
  align-items: center;
  gap: 10px;
}

.title-section h2 {
  margin: 0;
}

.content-container {
  margin-top: 20px;
}

.menu-card {
  height: 100%;
}

.detail-card {
  min-height: 600px;
}

.intro-content,
.history-content,
.reference-content,
.advice-content {
  padding: 10px;
}

.intro-text,
.measurement-info,
.importance-info,
.general-advice {
  margin-bottom: 20px;
}

.chart-filters {
  margin-bottom: 20px;
}

.chart-container {
  margin-bottom: 30px;
}

.data-table {
  margin-top: 20px;
}

.text-danger {
  color: #f56c6c;
}

.text-warning {
  color: #e6a23c;
}

.text-success {
  color: #67c23a;
}

.ml-2 {
  margin-left: 8px;
}
</style>