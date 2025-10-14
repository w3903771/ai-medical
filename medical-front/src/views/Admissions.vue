<template>
  <div class="admissions-page">
    <!-- 页面头部 -->
    <div class="page-header">
      <h1>住院管理</h1>
      <p>管理住院记录和相关文档</p>
    </div>

    <div class="admissions-container">
      <!-- 左侧树形结构 -->
      <div class="tree-panel">
        <el-card class="tree-card" shadow="never">
          <template #header>
            <div class="tree-header">
              <span>住院记录</span>
              <el-button type="primary" size="small" @click="handleAddAdmission">
                <el-icon><Plus /></el-icon>
                新增
              </el-button>
            </div>
          </template>
          
          <el-tree
            ref="treeRef"
            :data="treeData"
            :props="treeProps"
            node-key="id"
            :expand-on-click-node="false"
            :highlight-current="true"
            @node-click="handleNodeClick"
            class="admission-tree"
          >
            <template #default="{ node, data }">
              <div class="tree-node">
                <el-icon v-if="data.type === 'year'" color="#409eff">
                  <Calendar />
                </el-icon>
                <el-icon v-else-if="data.type === 'month'" color="#67c23a">
                  <Timer />
                </el-icon>
                <el-icon v-else color="#e6a23c">
                  <Document />
                </el-icon>
                <span class="node-label">{{ data.label }}</span>
                <span v-if="data.type === 'admission'" class="node-extra">
                  {{ data.hospital }}
                </span>
              </div>
            </template>
          </el-tree>
        </el-card>
      </div>

      <!-- 右侧内容区域 -->
      <div class="content-panel">
        <!-- 总览页 -->
        <el-card v-if="!selectedAdmission" class="overview-card">
          <template #header>
            <div class="overview-header">
              <span>住院记录总览</span>
            </div>
          </template>
          
          <el-table :data="allAdmissions" style="width: 100%" @row-click="handleRowClick">
            <el-table-column prop="label" label="记录编号" width="120" />
            <el-table-column prop="hospital" label="医院名称" width="150" />
            <el-table-column prop="department" label="科室" width="120" />
            <el-table-column prop="diagnosis" label="诊断" width="150" />
            <el-table-column prop="admissionDate" label="入院日期" width="120" />
            <el-table-column prop="dischargeDate" label="出院日期" width="120" />
            <el-table-column label="操作" width="120">
              <template #default="{ row }">
                <el-button size="small" type="primary" @click.stop="handleViewDetail(row)">查看详情</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>

        <div v-else class="admission-detail">
          <!-- 住院记录标题 -->
          <div class="detail-header">
            <h2>{{ selectedAdmission.hospital }} - {{ selectedAdmission.department }}</h2>
            <div class="detail-meta">
              <el-tag type="info">{{ selectedAdmission.admissionDate }} 至 {{ selectedAdmission.dischargeDate }}</el-tag>
              <el-tag type="success" style="margin-left: 8px;">{{ selectedAdmission.diagnosis }}</el-tag>
            </div>
            <el-button class="back-button" @click="handleBackToOverview">
              <el-icon><Back /></el-icon> 返回总览
            </el-button>
          </div>

          <!-- 标签页 -->
          <el-tabs v-model="activeTab" class="detail-tabs">
            <!-- 住院信息 -->
            <el-tab-pane label="住院信息" name="info">
              <el-card class="info-card">
                <el-form :model="selectedAdmission" label-width="100px" class="admission-form">
                  <el-row :gutter="20">
                    <el-col :span="12">
                      <el-form-item label="医院名称">
                        <el-input v-model="selectedAdmission.hospital" readonly />
                      </el-form-item>
                    </el-col>
                    <el-col :span="12">
                      <el-form-item label="科室">
                        <el-input v-model="selectedAdmission.department" readonly />
                      </el-form-item>
                    </el-col>
                  </el-row>
                  <el-row :gutter="20">
                    <el-col :span="12">
                      <el-form-item label="入院日期">
                        <el-input v-model="selectedAdmission.admissionDate" readonly />
                      </el-form-item>
                    </el-col>
                    <el-col :span="12">
                      <el-form-item label="出院日期">
                        <el-input v-model="selectedAdmission.dischargeDate" readonly />
                      </el-form-item>
                    </el-col>
                  </el-row>
                  <el-form-item label="主要诊断">
                    <el-input v-model="selectedAdmission.diagnosis" readonly />
                  </el-form-item>
                  <el-form-item label="住院天数">
                    <el-input :value="calculateDays(selectedAdmission.admissionDate, selectedAdmission.dischargeDate) + ' 天'" readonly />
                  </el-form-item>
                  <el-form-item label="备注">
                    <el-input
                      v-model="selectedAdmission.notes"
                      type="textarea"
                      :rows="4"
                      readonly
                    />
                  </el-form-item>
                </el-form>
                
                <div class="form-actions">
                  <el-button type="primary" @click="handleEditAdmission">编辑信息</el-button>
                  <el-button type="danger" @click="handleDeleteAdmission">删除记录</el-button>
                </div>
              </el-card>
            </el-tab-pane>

            <!-- PDF阅读 -->
            <el-tab-pane label="PDF阅读" name="pdf">
              <el-card class="pdf-card">
                <div v-if="selectedFiles.length === 0" class="no-files">
                  <el-icon size="48" color="#c0c4cc"><Document /></el-icon>
                  <p>暂无PDF文件</p>
                  <el-button type="primary" @click="activeTab = 'upload'">上传文件</el-button>
                </div>
                
                <div v-else class="pdf-viewer-container">
                  <div class="pdf-toolbar">
                    <el-select v-model="selectedPdfId" placeholder="选择PDF文件" style="width: 300px;">
                      <el-option
                        v-for="file in selectedFiles"
                        :key="file.id"
                        :label="file.filename"
                        :value="file.id"
                      />
                    </el-select>
                    <el-button type="primary" @click="handleDownloadPdf">下载</el-button>
                    <el-button @click="handleExtractText">提取文本</el-button>
                    <el-button type="success" @click="handleAIAnalysis">AI分析</el-button>
                  </div>
                  
                  <div class="pdf-viewer">
                    <iframe
                      v-if="selectedPdfUrl"
                      :src="selectedPdfUrl"
                      width="100%"
                      height="600px"
                      frameborder="0"
                    ></iframe>
                    <div v-else class="pdf-placeholder">
                      <el-icon size="64" color="#c0c4cc"><Document /></el-icon>
                      <p>请选择要查看的PDF文件</p>
                    </div>
                  </div>
                </div>
              </el-card>
            </el-tab-pane>

            <!-- PDF上传 -->
            <el-tab-pane label="PDF上传" name="upload">
              <el-card class="upload-card">
                <el-upload
                  ref="uploadRef"
                  class="upload-demo"
                  drag
                  :action="uploadUrl"
                  :headers="uploadHeaders"
                  :data="uploadData"
                  :on-success="handleUploadSuccess"
                  :on-error="handleUploadError"
                  :before-upload="beforeUpload"
                  accept=".pdf"
                  multiple
                >
                  <el-icon class="el-icon--upload"><upload-filled /></el-icon>
                  <div class="el-upload__text">
                    将PDF文件拖到此处，或<em>点击上传</em>
                  </div>
                  <template #tip>
                    <div class="el-upload__tip">
                      只能上传PDF文件，且不超过10MB
                    </div>
                  </template>
                </el-upload>

                <!-- 文件列表 -->
                <div v-if="selectedFiles.length > 0" class="file-list">
                  <h3>已上传文件</h3>
                  <el-table :data="selectedFiles" style="width: 100%">
                    <el-table-column prop="filename" label="文件名" />
                    <el-table-column prop="uploadDate" label="上传时间" width="180" />
                    <el-table-column prop="pages" label="页数" width="80" />
                    <el-table-column label="OCR状态" width="100">
                      <template #default="{ row }">
                        <el-tag :type="row.ocrStatus === 'completed' ? 'success' : 'info'" size="small">
                          {{ row.ocrStatus === 'completed' ? '已完成' : '处理中' }}
                        </el-tag>
                      </template>
                    </el-table-column>
                    <el-table-column label="操作" width="200">
                      <template #default="{ row }">
                        <el-button size="small" @click="handlePreviewFile(row)">预览</el-button>
                        <el-button size="small" type="danger" @click="handleDeleteFile(row)">删除</el-button>
                      </template>
                    </el-table-column>
                  </el-table>
                </div>
              </el-card>
            </el-tab-pane>
          </el-tabs>
        </div>
      </div>
    </div>

    <!-- 新增/编辑住院记录对话框 -->
    <el-dialog
      v-model="admissionDialogVisible"
      :title="admissionDialogTitle"
      width="600px"
      @close="resetAdmissionForm"
    >
      <el-form
        ref="admissionFormRef"
        :model="admissionForm"
        :rules="admissionFormRules"
        label-width="100px"
      >
        <el-form-item label="医院名称" prop="hospital">
          <el-input v-model="admissionForm.hospital" placeholder="请输入医院名称" />
        </el-form-item>
        <el-form-item label="科室" prop="department">
          <el-input v-model="admissionForm.department" placeholder="请输入科室" />
        </el-form-item>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="入院日期" prop="admissionDate">
              <el-date-picker
                v-model="admissionForm.admissionDate"
                type="date"
                placeholder="选择入院日期"
                format="YYYY-MM-DD"
                value-format="YYYY-MM-DD"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="出院日期" prop="dischargeDate">
              <el-date-picker
                v-model="admissionForm.dischargeDate"
                type="date"
                placeholder="选择出院日期"
                format="YYYY-MM-DD"
                value-format="YYYY-MM-DD"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="主要诊断" prop="diagnosis">
          <el-input v-model="admissionForm.diagnosis" placeholder="请输入主要诊断" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input
            v-model="admissionForm.notes"
            type="textarea"
            :rows="3"
            placeholder="请输入备注信息"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="admissionDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmitAdmission">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, watch, onMounted, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useRouter } from 'vue-router'
import { Calendar, Timer, Document, Plus, Back } from '@element-plus/icons-vue'

// 路由
const router = useRouter()

// 响应式数据
const treeRef = ref()
const uploadRef = ref()
const admissionFormRef = ref()
const activeTab = ref('info')
const selectedAdmission = ref(null)
const selectedPdfId = ref('')
const admissionDialogVisible = ref(false)

// 树形数据属性
const treeProps = {
  children: 'children',
  label: 'label'
}

// 模拟树形数据
const treeData = ref([
  {
    id: '2024',
    label: '2024年',
    type: 'year',
    children: [
      {
        id: '2024-01',
        label: '1月',
        type: 'month',
        children: [
          {
            id: 'admission-1',
            label: '住院记录 #001',
            type: 'admission',
            hospital: '市人民医院',
            department: '心内科',
            admissionDate: '2024-01-10',
            dischargeDate: '2024-01-15',
            diagnosis: '高血压',
            notes: '血压控制良好，按时服药'
          },
          {
            id: 'admission-2',
            label: '住院记录 #002',
            type: 'admission',
            hospital: '中医院',
            department: '内分泌科',
            admissionDate: '2024-01-20',
            dischargeDate: '2024-01-25',
            diagnosis: '糖尿病',
            notes: '血糖控制稳定，需要继续监测'
          }
        ]
      }
    ]
  },
  {
    id: '2023',
    label: '2023年',
    type: 'year',
    children: [
      {
        id: '2023-12',
        label: '12月',
        type: 'month',
        children: [
          {
            id: 'admission-3',
            label: '住院记录 #003',
            type: 'admission',
            hospital: '省医院',
            department: '消化科',
            admissionDate: '2023-12-15',
            dischargeDate: '2023-12-20',
            diagnosis: '胃炎',
            notes: '症状改善，注意饮食'
          }
        ]
      }
    ]
  }
])

// 住院记录表单
const admissionForm = reactive({
  id: null,
  hospital: '',
  department: '',
  admissionDate: '',
  dischargeDate: '',
  diagnosis: '',
  notes: ''
})

// 表单验证规则
const admissionFormRules = {
  hospital: [{ required: true, message: '请输入医院名称', trigger: 'blur' }],
  department: [{ required: true, message: '请输入科室', trigger: 'blur' }],
  admissionDate: [{ required: true, message: '请选择入院日期', trigger: 'change' }],
  dischargeDate: [{ required: true, message: '请选择出院日期', trigger: 'change' }],
  diagnosis: [{ required: true, message: '请输入主要诊断', trigger: 'blur' }]
}

// 模拟文件数据
const fileData = ref({
  'admission-1': [
    {
      id: 'file-1',
      filename: '入院记录.pdf',
      uploadDate: '2024-01-10 14:30:00',
      pages: 5,
      ocrStatus: 'completed',
      url: '/api/v1/files/file-1.pdf'
    },
    {
      id: 'file-2',
      filename: '检查报告.pdf',
      uploadDate: '2024-01-12 09:15:00',
      pages: 3,
      ocrStatus: 'completed',
      url: '/api/v1/files/file-2.pdf'
    }
  ],
  'admission-2': [
    {
      id: 'file-3',
      filename: '出院小结.pdf',
      uploadDate: '2024-01-25 16:45:00',
      pages: 2,
      ocrStatus: 'processing',
      url: '/api/v1/files/file-3.pdf'
    }
  ]
})

// 计算属性
const selectedFiles = computed(() => {
  return selectedAdmission.value ? (fileData.value[selectedAdmission.value.id] || []) : []
})

// 获取所有住院记录列表
const allAdmissions = computed(() => {
  const admissions = []
  treeData.value.forEach(yearNode => {
    if (yearNode.children) {
      yearNode.children.forEach(monthNode => {
        if (monthNode.children) {
          monthNode.children.forEach(admission => {
            if (admission.type === 'admission') {
              admissions.push(admission)
            }
          })
        }
      })
    }
  })
  return admissions
})

const selectedPdfUrl = computed(() => {
  if (!selectedPdfId.value) return ''
  const file = selectedFiles.value.find(f => f.id === selectedPdfId.value)
  return file ? file.url : ''
})

const admissionDialogTitle = computed(() => {
  return admissionForm.id ? '编辑住院记录' : '新增住院记录'
})

const uploadUrl = computed(() => '/api/v1/admissions/upload')
const uploadHeaders = computed(() => ({ Authorization: `Bearer ${localStorage.getItem('token')}` }))
const uploadData = computed(() => ({ admissionId: selectedAdmission.value?.id }))

// 方法
const handleNodeClick = (data) => {
  if (data.type === 'admission') {
    selectedAdmission.value = data
    activeTab.value = 'info'
    selectedPdfId.value = ''
  }
}

// 从列表进入住院详情
const handleRowClick = (row) => {
  handleViewDetail(row)
}

// 查看住院详情
const handleViewDetail = (row) => {
  selectedAdmission.value = row
  activeTab.value = 'info'
  selectedPdfId.value = ''
}

// 返回总览页
const handleBackToOverview = () => {
  selectedAdmission.value = null
}

// 初始化时展开最新一年最新一个月的记录
onMounted(() => {
  nextTick(() => {
    if (treeRef.value) {
      // 找出ID值最大的年份节点（最新年份）
      let latestYearId = '';
      let maxYearValue = 0;
      
      treeData.value.forEach(yearNode => {
        if (yearNode.type === 'year') {
          const yearValue = parseInt(yearNode.id);
          if (yearValue > maxYearValue) {
            maxYearValue = yearValue;
            latestYearId = yearNode.id;
          }
        }
      });
      
      if (latestYearId) {
        // 展开最新年份节点
        treeRef.value.store.nodesMap[latestYearId].expanded = true;
        
        // 找出该年份下ID值最大的月份节点（最新月份）
        const latestYearNode = treeData.value.find(node => node.id === latestYearId);
        if (latestYearNode && latestYearNode.children && latestYearNode.children.length > 0) {
          let latestMonthId = '';
          let maxMonthValue = 0;
          
          latestYearNode.children.forEach(monthNode => {
            if (monthNode.type === 'month') {
              // 月份ID格式为 "YYYY-MM"，提取月份部分
              const monthValue = parseInt(monthNode.id.split('-')[1]);
              if (monthValue > maxMonthValue) {
                maxMonthValue = monthValue;
                latestMonthId = monthNode.id;
              }
            }
          });
          
          if (latestMonthId) {
            // 展开最新月份节点
            treeRef.value.store.nodesMap[latestMonthId].expanded = true;
          }
        }
      }
    }
  });
})

const calculateDays = (startDate, endDate) => {
  const start = new Date(startDate)
  const end = new Date(endDate)
  const diffTime = Math.abs(end - start)
  return Math.ceil(diffTime / (1000 * 60 * 60 * 24))
}

const handleAddAdmission = () => {
  resetAdmissionForm()
  admissionDialogVisible.value = true
}

const handleEditAdmission = () => {
  if (selectedAdmission.value) {
    Object.assign(admissionForm, selectedAdmission.value)
    admissionDialogVisible.value = true
  }
}

const handleDeleteAdmission = async () => {
  try {
    await ElMessageBox.confirm('确定要删除这条住院记录吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    ElMessage.success('删除成功')
    selectedAdmission.value = null
  } catch {
    // 用户取消删除
  }
}

const resetAdmissionForm = () => {
  Object.assign(admissionForm, {
    id: null,
    hospital: '',
    department: '',
    admissionDate: '',
    dischargeDate: '',
    diagnosis: '',
    notes: ''
  })
  if (admissionFormRef.value) {
    admissionFormRef.value.clearValidate()
  }
}

const handleSubmitAdmission = async () => {
  try {
    await admissionFormRef.value.validate()
    
    if (admissionForm.id) {
      ElMessage.success('编辑成功')
    } else {
      ElMessage.success('新增成功')
    }
    
    admissionDialogVisible.value = false
  } catch (error) {
    console.error('表单验证失败:', error)
  }
}

const handlePreviewFile = (file) => {
  selectedPdfId.value = file.id
  activeTab.value = 'pdf'
}

const handleDeleteFile = async (file) => {
  try {
    await ElMessageBox.confirm('确定要删除这个文件吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    ElMessage.success('删除成功')
  } catch {
    // 用户取消删除
  }
}

const handleDownloadPdf = () => {
  if (selectedPdfUrl.value) {
    window.open(selectedPdfUrl.value, '_blank')
  }
}

const handleExtractText = () => {
  ElMessage.info('文本提取功能开发中...')
}

const beforeUpload = (file) => {
  const isPDF = file.type === 'application/pdf'
  const isLt10M = file.size / 1024 / 1024 < 10

  if (!isPDF) {
    ElMessage.error('只能上传PDF格式的文件!')
    return false
  }
  if (!isLt10M) {
    ElMessage.error('上传文件大小不能超过10MB!')
    return false
  }
  return true
}

const handleUploadSuccess = (response, file) => {
  ElMessage.success('上传成功')
  // 这里应该更新文件列表
}

const handleUploadError = (error) => {
  ElMessage.error('上传失败')
  console.error('上传错误:', error)
}

// 处理AI分析
const handleAIAnalysis = () => {
  if (!selectedPdfId.value) {
    ElMessage.warning('请先选择一个PDF文件')
    return
  }
  
  // 获取当前选中的PDF文件
  const currentPdf = selectedFiles.value.find(file => file.id === selectedPdfId.value)
  
  // 跳转到大模型界面，并传递相关参数
  router.push({
    path: '/llm-interface',
    query: {
      source: 'pdf',
      pdfId: selectedPdfId.value,
      pdfName: currentPdf?.filename || '',
      admissionId: selectedAdmission.value?.id || '',
      hospital: selectedAdmission.value?.hospital || '',
      diagnosis: selectedAdmission.value?.diagnosis || ''
    }
  })
}

// 监听选中的PDF文件变化
watch(selectedFiles, (newFiles) => {
  if (newFiles.length > 0 && !selectedPdfId.value) {
    selectedPdfId.value = newFiles[0].id
  }
}, { immediate: true })
</script>

<style scoped>
.admissions-page {
  padding: 0;
}

.page-header {
  margin-bottom: 24px;
}

.page-header h1 {
  margin: 0 0 8px 0;
  font-size: 24px;
  font-weight: 600;
  color: var(--text-primary);
}

.page-header p {
  margin: 0;
  color: var(--text-secondary);
}

.admissions-container {
  display: flex;
  gap: 20px;
  height: calc(100vh - 200px);
}

.tree-panel {
  width: 300px;
  flex-shrink: 0;
}

.tree-card {
  height: 100%;
}

.tree-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
}

.admission-tree {
  height: calc(100% - 60px);
  overflow-y: auto;
}

.tree-node {
  display: flex;
  align-items: center;
  gap: 8px;
  width: 100%;
}

.node-label {
  flex: 1;
  font-size: 14px;
}

.node-extra {
  font-size: 12px;
  color: var(--text-secondary);
}

.content-panel {
  flex: 1;
  overflow: hidden;
}

.empty-card {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.empty-content {
  text-align: center;
  color: var(--text-secondary);
}

.empty-content p {
  margin: 16px 0 0 0;
  font-size: 16px;
}

.admission-detail {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.detail-header {
  margin-bottom: 16px;
}

.detail-header h2 {
  margin: 0 0 8px 0;
  font-size: 20px;
  color: var(--text-primary);
}

.detail-meta {
  display: flex;
  align-items: center;
}

.detail-tabs {
  flex: 1;
  overflow: hidden;
}

.detail-tabs :deep(.el-tabs__content) {
  height: calc(100% - 55px);
  overflow-y: auto;
}

.info-card,
.pdf-card,
.upload-card {
  height: 100%;
}

.admission-form {
  margin-bottom: 20px;
}

.form-actions {
  text-align: center;
  padding-top: 20px;
  border-top: 1px solid var(--border-color);
}

.no-files {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 300px;
  color: var(--text-secondary);
}

.no-files p {
  margin: 16px 0;
}

.pdf-viewer-container {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.pdf-toolbar {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
  padding-bottom: 16px;
  border-bottom: 1px solid var(--border-color);
}

.pdf-viewer {
  flex: 1;
  overflow: hidden;
}

.pdf-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 400px;
  color: var(--text-secondary);
}

.pdf-placeholder p {
  margin: 16px 0 0 0;
}

.upload-demo {
  margin-bottom: 20px;
}

.file-list {
  margin-top: 20px;
}

.file-list h3 {
  margin: 0 0 16px 0;
  font-size: 16px;
  color: var(--text-primary);
}

/* 响应式设计 */
@media (max-width: 1024px) {
  .admissions-container {
    flex-direction: column;
    height: auto;
  }
  
  .tree-panel {
    width: 100%;
    height: 300px;
  }
  
  .content-panel {
    height: 600px;
  }
}

@media (max-width: 768px) {
  .detail-header h2 {
    font-size: 18px;
  }
  
  .detail-meta {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
  
  .pdf-toolbar {
    flex-direction: column;
    align-items: stretch;
  }
  
  .pdf-toolbar .el-select {
    width: 100% !important;
  }
}
</style>