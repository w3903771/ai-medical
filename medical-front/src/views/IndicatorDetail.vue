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

// 模拟数据
const mockIndicatorDetails = {
  '体重': {
    category: '基础指标',
    introduction: '体重是衡量人体总质量的重要指标，包括肌肉、脂肪、骨骼和体液等组成部分的总和。',
    measurementMethod: '使用体重秤在早晨空腹、排尿后测量，穿着轻便衣物或不穿衣物。',
    clinicalSignificance: '体重变化可反映营养状况、水分平衡和代谢健康。体重过高或过低都可能与健康问题相关。',
    referenceRange: 'BMI 18.5-24.9 kg/m²',
    unit: 'kg',
    highMeaning: '可能表示超重或肥胖，增加心血管疾病、糖尿病等风险',
    lowMeaning: '可能表示营养不良、消化系统疾病或其他健康问题',
    highAdvice: '建议控制饮食摄入，增加身体活动，咨询医生或营养师制定减重计划。',
    lowAdvice: '建议增加营养摄入，咨询医生排除潜在疾病，制定增重计划。',
    normalAdvice: '继续保持健康的饮食和运动习惯，定期监测体重变化。',
    generalAdvice: '保持均衡饮食，规律运动，充足睡眠，避免过度节食或暴饮暴食。'
  },
  '血压': {
    category: '心血管指标',
    introduction: '血压是血液在血管中流动时对血管壁产生的压力，通常以收缩压/舒张压的形式表示，单位为毫米汞柱(mmHg)。',
    measurementMethod: '使用电子血压计或水银血压计，在安静休息5分钟后，坐姿测量，上臂与心脏保持同一水平。',
    clinicalSignificance: '血压是评估心血管健康的重要指标，持续高血压会增加心脏病、中风和肾脏疾病的风险。',
    referenceRange: '收缩压<120 mmHg，舒张压<80 mmHg',
    unit: 'mmHg',
    highMeaning: '高血压，增加心脑血管疾病风险',
    lowMeaning: '低血压，可能导致头晕、乏力或晕厥',
    highAdvice: '减少盐分摄入，保持健康体重，规律运动，限制酒精摄入，必要时遵医嘱服用降压药。',
    lowAdvice: '适当增加盐分和水分摄入，避免突然站立，必要时咨询医生。',
    normalAdvice: '继续保持健康生活方式，定期监测血压变化。',
    generalAdvice: '保持健康饮食，规律运动，避免吸烟和过量饮酒，控制压力，定期检查血压。'
  },
  '血糖': {
    category: '代谢指标',
    introduction: '血糖是指血液中葡萄糖的浓度，是人体能量代谢的重要指标。',
    measurementMethod: '使用血糖仪，通过指尖采血测量。空腹血糖在8小时未进食后测量，餐后血糖在进食后2小时测量。',
    clinicalSignificance: '血糖水平反映胰岛素功能和糖代谢状况，持续异常可能提示糖尿病或其他代谢疾病。',
    referenceRange: '空腹血糖3.9-6.1 mmol/L，餐后2小时<7.8 mmol/L',
    unit: 'mmol/L',
    highMeaning: '高血糖，可能提示糖尿病前期或糖尿病',
    lowMeaning: '低血糖，可能导致头晕、出汗、心悸、意识模糊等症状',
    highAdvice: '控制碳水化合物摄入，增加运动，保持健康体重，必要时遵医嘱服用降糖药。',
    lowAdvice: '及时补充碳水化合物，如糖果、果汁等，严重时需就医治疗。',
    normalAdvice: '继续保持健康饮食和生活习惯，定期监测血糖变化。',
    generalAdvice: '均衡饮食，控制碳水化合物摄入，规律运动，保持健康体重，避免过度饮酒。'
  },
  '心率': {
    category: '心血管指标',
    introduction: '心率是指心脏每分钟跳动的次数，反映心脏工作状态和自主神经系统功能。',
    measurementMethod: '可通过触摸颈动脉或桡动脉、使用心率监测器或智能手表测量，在安静状态下测量为静息心率。',
    clinicalSignificance: '心率变化可反映心脏功能、自主神经系统状态和身体适应能力，异常心率可能提示心脏疾病。',
    referenceRange: '成人静息心率60-100次/分钟',
    unit: '次/分钟',
    highMeaning: '心动过速，可能与焦虑、发热、贫血、心脏疾病等相关',
    lowMeaning: '心动过缓，可能与药物影响、心脏传导阻滞等相关',
    highAdvice: '避免咖啡因、酒精等刺激物，学习放松技巧，必要时咨询医生。',
    lowAdvice: '检查是否与药物相关，如有症状应咨询医生。',
    normalAdvice: '继续保持健康生活方式，定期监测心率变化。',
    generalAdvice: '规律运动，充足睡眠，避免过度压力，限制咖啡因和酒精摄入。'
  },
  '体温': {
    category: '基础指标',
    introduction: '体温是人体内部的温度，由体温调节中枢控制，反映人体代谢状态和健康状况。',
    measurementMethod: '可通过口腔、腋下、耳道或额头测量，使用水银温度计或电子温度计。',
    clinicalSignificance: '体温异常可能提示感染、炎症或其他疾病，是评估健康状况的基本指标。',
    referenceRange: '36.1-37.2°C（口腔测量）',
    unit: '°C',
    highMeaning: '发热，可能提示感染、炎症或其他疾病',
    lowMeaning: '体温过低，可能与环境温度低、代谢异常或严重疾病相关',
    highAdvice: '多休息，多饮水，必要时使用退热药物，如持续高热应就医。',
    lowAdvice: '保暖，如有严重症状应立即就医。',
    normalAdvice: '继续保持健康生活习惯。',
    generalAdvice: '保持充足睡眠，均衡饮食，适当运动，增强免疫力。'
  },
  '血氧': {
    category: '呼吸指标',
    introduction: '血氧饱和度是指血液中被氧气结合的血红蛋白与总血红蛋白的比例，反映血液携氧能力和组织供氧状况。',
    measurementMethod: '使用脉搏血氧仪，通过手指、耳垂或鼻子测量。',
    clinicalSignificance: '血氧饱和度是评估呼吸和循环功能的重要指标，低血氧可能提示呼吸系统或循环系统疾病。',
    referenceRange: '95-100%',
    unit: '%',
    highMeaning: '一般不会超过100%',
    lowMeaning: '低血氧，可能与呼吸系统疾病、心脏疾病或高海拔环境相关',
    highAdvice: '血氧饱和度正常不会超过100%，如测量值异常高，可能是测量误差。',
    lowAdvice: '如血氧低于90%，应立即就医；轻度低血氧可通过深呼吸、改善通风或氧疗改善。',
    normalAdvice: '继续保持健康生活习惯。',
    generalAdvice: '避免吸烟，保持室内空气流通，规律运动增强心肺功能，高海拔地区注意适应。'
  }
}

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
const loadIndicatorDetails = () => {
  loading.value = true
  
  // 模拟API调用
  setTimeout(() => {
    const details = mockIndicatorDetails[indicatorName.value] || {
      category: '未分类',
      introduction: '暂无介绍',
      measurementMethod: '暂无测量方法说明',
      clinicalSignificance: '暂无临床意义说明',
      referenceRange: '暂无参考范围',
      unit: '',
      highMeaning: '暂无说明',
      lowMeaning: '暂无说明',
      highAdvice: '暂无建议',
      lowAdvice: '暂无建议',
      normalAdvice: '暂无建议',
      generalAdvice: '暂无建议'
    }
    
    categoryName.value = details.category
    introductionText.value = details.introduction
    measurementMethod.value = details.measurementMethod
    clinicalSignificance.value = details.clinicalSignificance
    referenceRange.value = details.referenceRange
    unit.value = details.unit
    highMeaning.value = details.highMeaning
    lowMeaning.value = details.lowMeaning
    highAdvice.value = details.highAdvice
    lowAdvice.value = details.lowAdvice
    normalAdvice.value = details.normalAdvice
    generalAdvice.value = details.generalAdvice
    
    // 设置指标类型
    switch (details.category) {
      case '血常规':
      case '心血管指标':
        indicatorType.value = 'danger'
        break
      case '代谢指标':
        indicatorType.value = 'warning'
        break
      case '基础指标':
        indicatorType.value = 'success'
        break
      case '呼吸指标':
        indicatorType.value = 'info'
        break
      default:
        indicatorType.value = 'info'
    }
    
    // 加载历史数据
    historyData.value = generateMockHistoryData(indicatorName.value)
    
    // 设置最新状态
    if (historyData.value.length > 0) {
      latestStatus.value = historyData.value[historyData.value.length - 1].status
    }
    
    loading.value = false
    
    // 如果是历史数据页面，初始化图表
    if (activeMenu.value === 'history') {
      initChart()
    }
  }, 500)
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
  if (mockIndicatorDetails[indicatorName.value]) {
    const refRange = mockIndicatorDetails[indicatorName.value].referenceRange
    
    if (refRange.includes('-')) {
      const [min, max] = refRange.split('-').map(str => {
        const match = str.match(/[\d.]+/)
        return match ? parseFloat(match[0]) : null
      })
      
      if (min !== null) {
        markLines.push({ name: '下限', yAxis: min, lineStyle: { color: '#e6a23c' } })
      }
      
      if (max !== null) {
        markLines.push({ name: '上限', yAxis: max, lineStyle: { color: '#f56c6c' } })
      }
    }
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
  
  // 这里应该根据日期范围筛选数据
  // 模拟筛选
  const startDate = new Date(dateRange.value[0])
  const endDate = new Date(dateRange.value[1])
  
  const allData = generateMockHistoryData(indicatorName.value)
  historyData.value = allData.filter(item => {
    const itemDate = new Date(item.date)
    return itemDate >= startDate && itemDate <= endDate
  })
  
  // 更新图表
  nextTick(() => {
    initChart()
  })
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