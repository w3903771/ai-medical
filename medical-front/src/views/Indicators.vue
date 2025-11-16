<template>
  <div class="indicators-page">
    <!-- 页面头部 -->
    <div class="page-header">
      <h1>指标数据管理</h1>
      <p>管理和分析您的健康指标数据</p>
    </div>

    <!-- 工具栏 -->
    <el-card class="toolbar-card" shadow="never">
      <div class="toolbar">
        <div class="toolbar-left">
          <el-button type="primary" @click="handleAddIndicator">
            <el-icon><Plus /></el-icon>
            新增指标
          </el-button>
          <el-button 
            type="success" 
            :disabled="!hasSelection"
            @click="handleBatchAnalysis"
          >
            <el-icon><DataAnalysis /></el-icon>
            联合分析
          </el-button>
          <el-button type="info" @click="handleImport">
            <el-icon><Upload /></el-icon>
            导入数据
          </el-button>
          <el-button type="primary" @click="handleAdd">
            <el-icon><Plus /></el-icon>
            新增数据
          </el-button>
          <el-button type="warning" @click="openCategoryDialog">
            <el-icon><Setting /></el-icon>
            类别管理
          </el-button>
        </div>
        <div class="toolbar-right">
          <el-select
            v-model="categoryFilter"
            placeholder="按分类筛选"
            clearable
            style="width: 150px; margin-right: 12px;"
            @change="handleCategoryFilterChange"
          >
            <el-option
              v-for="category in indicatorCategoriesList"
              :key="category.id"
              :label="category.name"
              :value="category.id"
            />
          </el-select>
          <el-date-picker
            v-model="dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD"
            @change="handleDateRangeChange"
          />
          <el-input
            v-model="searchKeyword"
            placeholder="搜索指标..."
            style="width: 200px; margin-left: 12px;"
            clearable
            @input="handleSearch"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
        </div>
      </div>
    </el-card>

    <!-- 数据表格 -->
    <el-card class="table-card">
      <el-table
        ref="tableRef"
        :data="tableData"
        style="width: 100%"
        @selection-change="handleSelectionChange"
        @row-contextmenu="handleRowContextMenu"
        row-key="id"
        stripe
        border
      >
        <el-table-column type="selection" width="55" />
          <el-table-column prop="indicator" label="指标名称" width="120" fixed="left">
            <template #default="{ row }">
              <el-tag :type="getIndicatorType(row.indicator)" @click="handleView(row)" style="cursor: pointer">{{ row.indicator }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="value" label="数值" width="100">
          <template #default="{ row }">
            <span :class="getValueClass(row)">{{ row.value }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="unit" label="单位" width="80" />
        <el-table-column prop="referenceRange" label="参考范围" width="120" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)" size="small">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="measureDate" label="测量日期" width="120" />
        <el-table-column prop="category" label="分类" width="120">
          <template #default="{ row }">
            <el-tag size="small" effect="plain">{{ row.category ?? 'Null' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="source" label="数据来源" width="100">
          <template #default="{ row }">
            <el-tag size="small" effect="plain">{{ row.source }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="note" label="备注" min-width="150" show-overflow-tooltip />
        <el-table-column label="趋势图" width="120">
          <template #default="{ row }">
            <div class="trend-chart">
              <el-tooltip content="查看详细趋势">
                <div class="mini-chart" @click="handleViewTrend(row)">
                  <div class="chart-placeholder">
                    <el-icon><TrendCharts /></el-icon>
                  </div>
                </div>
              </el-tooltip>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="280" fixed="right">
          <template #default="{ row }">
            <el-button size="small" type="primary" @click="handleView(row)">查看</el-button>
            <el-button size="small" @click="handleEdit(row)">编辑</el-button>
            <el-button size="small" type="success" @click="handleAnalyze(row)">分析</el-button>
            <el-button size="small" type="danger" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-wrapper">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <!-- 右键菜单 -->
    <div
      v-show="contextMenuVisible"
      :style="{ left: contextMenuLeft + 'px', top: contextMenuTop + 'px' }"
      class="context-menu"
      @blur="hideContextMenu"
      tabindex="-1"
    >
      <div class="menu-item" @click="handleContextEdit">
        <el-icon><Edit /></el-icon>
        编辑
      </div>
      <div class="menu-item" @click="handleContextDelete">
        <el-icon><Delete /></el-icon>
        删除
      </div>
      <div class="menu-divider"></div>
      <div class="menu-item" @click="handleContextAddData">
        <el-icon><Plus /></el-icon>
        新增数据
      </div>
      <div class="menu-item" @click="handleContextViewTrend">
        <el-icon><TrendCharts /></el-icon>
        查看变化
      </div>
      <div class="menu-item" @click="handleContextAIAnalysis">
        <el-icon><ChatDotRound /></el-icon>
        大模型分析
      </div>
    </div>

    <!-- 新增/编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="600px"
      @close="resetForm"
    >
      <el-form
        ref="formRef"
        :model="form"
        :rules="formRules"
        label-width="100px"
      >
        <el-form-item label="指标名称" prop="indicator">
          <el-select
            v-model="form.indicator"
            placeholder="请选择或输入指标"
            style="width: 100%"
            filterable
            allow-create
            default-first-option
            clearable
            @change="handleIndicatorChange"
          >
            <el-option
              v-for="name in indicatorNameOptions"
              :key="name"
              :label="name"
              :value="name"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="分类" prop="category">
          <el-select v-model="form.category" placeholder="请选择分类" style="width: 100%">
            <el-option 
              v-for="category in indicatorCategoryOptions" 
              :key="category.id" 
              :label="category.name" 
              :value="category.id" 
            />
          </el-select>
        </el-form-item>
        <el-form-item label="数值" prop="value">
          <el-input v-model="form.value" placeholder="请输入数值" />
        </el-form-item>
        <el-form-item label="单位" prop="unit">
          <el-input v-model="form.unit" placeholder="请输入单位" />
        </el-form-item>
        <el-form-item label="参考范围">
          <el-row :gutter="10">
            <el-col :span="11">
              <el-form-item prop="referenceMin">
                <el-input v-model="form.referenceMin" placeholder="最小值" />
              </el-form-item>
            </el-col>
            <el-col :span="2" class="text-center">
              <span>-</span>
            </el-col>
            <el-col :span="11">
              <el-form-item prop="referenceMax">
                <el-input v-model="form.referenceMax" placeholder="最大值" />
              </el-form-item>
            </el-col>
          </el-row>
        </el-form-item>
        <el-form-item label="测量日期" prop="measureDate">
          <el-date-picker
            v-model="form.measureDate"
            type="date"
            placeholder="选择日期"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="数据来源" prop="source">
          <el-select v-model="form.source" placeholder="请选择来源">
            <el-option label="手动录入" value="手动录入" />
            <el-option label="设备同步" value="设备同步" />
            <el-option label="医院检查" value="医院检查" />
            <el-option label="OCR识别" value="OCR识别" />
          </el-select>
        </el-form-item>
        <el-form-item label="备注">
          <el-input
            v-model="form.note"
            type="textarea"
            :rows="3"
            placeholder="请输入备注信息"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>

    <!-- 分类管理对话框 -->
    <el-dialog
      v-model="indicatorCategoryDialogVisible"
      title="分类管理"
      width="500px"
    >
      <div class="category-form">
        <el-input 
          v-model="indicatorNewCategoryName" 
          placeholder="请输入分类名称" 
          style="width: calc(100% - 100px)"
        />
        <el-button 
          type="primary" 
          @click="indicatorEditingCategoryId ? saveCategory() : addCategory()"
        >
          {{ indicatorEditingCategoryId ? '保存' : '添加' }}
        </el-button>
      </div>
      
      <el-table :data="indicatorCategoriesList" style="width: 100%; margin-top: 20px">
        <el-table-column prop="name" label="分类名称" />
        <el-table-column label="操作" width="150">
          <template #default="{ row }">
            <el-button type="primary" text @click="editCategory(row)">
              <el-icon><Edit /></el-icon>
              编辑
            </el-button>
            <el-button type="danger" text @click="deleteCategory(row)">
              <el-icon><Delete /></el-icon>
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <template #footer>
        <el-button @click="indicatorCategoryDialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>

    <!-- 新增指标对话框 -->
    <el-dialog
      v-model="indicatorDialogVisible"
      title="新增指标"
      width="500px"
      @close="resetIndicatorForm"
    >
      <el-form
        ref="indicatorFormRef"
        :model="indicatorForm"
        :rules="indicatorFormRules"
        label-width="100px"
      >
        <el-form-item label="指标名称" prop="name">
          <el-input v-model="indicatorForm.name" placeholder="请输入指标名称" />
        </el-form-item>
        <el-form-item label="指标英文名" prop="nameEn">
          <el-input v-model="indicatorForm.nameEn" placeholder="请输入指标英文名" />
        </el-form-item>
        <el-form-item label="单位" prop="unit">
          <el-input v-model="indicatorForm.unit" placeholder="请输入单位" />
        </el-form-item>
        <el-form-item label="分类" prop="category">
          <el-select v-model="indicatorForm.category" placeholder="请选择分类" style="width: 100%">
            <el-option 
              v-for="category in indicatorCategoryOptions" 
              :key="category.id" 
              :label="category.name" 
              :value="category.id" 
            />
          </el-select>
        </el-form-item>
        <el-form-item label="参考范围">
          <el-row :gutter="10">
            <el-col :span="11">
              <el-form-item prop="referenceMin">
                <el-input v-model="indicatorForm.referenceMin" placeholder="最小值" />
              </el-form-item>
            </el-col>
            <el-col :span="2" class="text-center">
              <span>-</span>
            </el-col>
            <el-col :span="11">
              <el-form-item prop="referenceMax">
                <el-input v-model="indicatorForm.referenceMax" placeholder="最大值" />
              </el-form-item>
            </el-col>
          </el-row>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="indicatorDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmitIndicator">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useRouter } from 'vue-router'
import { Search, Plus, Edit, Delete, Setting } from '@element-plus/icons-vue'
import { getIndicators, createIndicator, deleteIndicator, createRecord } from '@/api/indicators'
import { listCategories } from '@/api/categories'

// 路由
const router = useRouter()

// 响应式数据
const tableRef = ref()
const formRef = ref()
const searchKeyword = ref('')
const dateRange = ref([])
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)
const selectedRows = ref([])
const dialogVisible = ref(false)
const contextMenuVisible = ref(false)
const contextMenuLeft = ref(0)
const contextMenuTop = ref(0)
const categoryFilter = ref('')

// 分类管理相关
const indicatorCategoriesList = ref([])
const indicatorCategoryDialogVisible = ref(false)
const indicatorNewCategoryName = ref('')
const indicatorEditingCategoryId = ref(null)

// 新增指标表单数据
const indicatorForm = reactive({
  name: '',
  englishName: '',
  unit: '',
  referenceMin: '',
  referenceMax: '',
  category: ''
})
const indicatorFormRules = {
  name: [
    { required: true, message: '请输入指标名称', trigger: 'blur' },
    { max: 50, message: '长度不能超过50个字符', trigger: 'blur' }
  ],
  nameEn: [
    { required: true, message: '请输入指标英文名', trigger: 'blur' },
    { max: 100, message: '长度不能超过100个字符', trigger: 'blur' }
  ],
  unit: [
    { required: true, message: '请输入单位', trigger: 'blur' },
    { max: 20, message: '长度不能超过20个字符', trigger: 'blur' }
  ],
  referenceMin: [
    { pattern: /^-?\d+(\.\d+)?$/, message: '请输入有效的数字', trigger: 'blur' }
  ],
  referenceMax: [
    { pattern: /^-?\d+(\.\d+)?$/, message: '请输入有效的数字', trigger: 'blur' }
  ],
  category: []
}

const indicatorFormRef = ref()
const indicatorDialogVisible = ref(false)
// 加载数据相关
const loading = ref(false)

// 指标分类数据
const indicatorCategoryOptions = ref([])

// 分类管理对话框
const indicatorDialogCategory = ref(false)
const indicatorInputCategoryName = ref('')
const indicatorEditCategoryId = ref(null)

// 接口数据
const currentContextRow = ref(null)

// 指标名称选项（从接口列表聚合）
const indicatorNameOptions = ref([])

// 表单数据
const form = reactive({
  id: null,
  indicator: '',
  value: '',
  unit: '',
  referenceRange: '',
  referenceMin: '',
  referenceMax: '',
  measureDate: '',
  source: '',
  note: '',
  category: '' // 添加分类字段
})

// 表单验证规则
const formRules = {
  indicator: [{ required: true, message: '请输入或选择指标名称', trigger: 'change' }],
  value: [{ required: true, message: '请输入数值', trigger: 'blur' }],
  unit: [{ required: true, message: '请输入单位', trigger: 'blur' }],
  referenceMin: [{ pattern: /^-?\d+(\.\d+)?$/, message: '请输入有效的数字', trigger: 'blur' }],
  referenceMax: [{ pattern: /^-?\d+(\.\d+)?$/, message: '请输入有效的数字', trigger: 'blur' }],
  measureDate: [{ required: true, message: '请选择测量日期', trigger: 'change' }],
  source: [{ required: true, message: '请选择数据来源', trigger: 'change' }],
  category: [{ required: true, message: '请选择分类', trigger: 'change' }]
}

const tableData = ref([])

// 计算属性
const hasSelection = computed(() => selectedRows.value.length > 0)
const dialogTitle = computed(() => form.id ? '编辑指标数据' : '新增指标数据')

// 方法
const getIndicatorType = (indicator) => {
  const types = {
    '体重': 'primary',
    '血压': 'success',
    '血糖': 'warning',
    '心率': 'info',
    '体温': 'danger',
    '血氧': 'primary'
  }
  return types[indicator] || ''
}

const getValueClass = (row) => {
  if (row.status === 'high') return 'value-high'
  if (row.status === 'low') return 'value-low'
  return 'value-normal'
}

const getStatusType = (status) => {
  const types = {
    'normal': 'success',
    'high': 'danger',
    'low': 'warning'
  }
  return types[status] || 'info'
}

const getStatusText = (status) => {
  const texts = {
    'normal': '正常',
    'high': '偏高',
    'low': '偏低'
  }
  return texts[status] || '未知'
}

const handleAdd = () => {
  resetForm()
  dialogVisible.value = true
}

const handleEdit = (row) => {
  Object.assign(form, { ...row })
  dialogVisible.value = true
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm('确定要删除该指标吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await deleteIndicator(row.id)
    ElMessage.success('删除成功')
    loadData()
  } catch {}
}

const handleSelectionChange = (selection) => {
  selectedRows.value = selection
}

const handleBatchAnalysis = () => {
  ElMessage.info(`已选择 ${selectedRows.value.length} 条记录进行联合分析`)
  // 这里可以跳转到分析页面或打开分析对话框
}

const handleImport = () => {
  ElMessage.info('导入功能开发中...')
}

const handleDateRangeChange = () => {
  loadData()
}

const handleSearch = () => {
  loadData()
}

const handleSizeChange = (size) => {
  pageSize.value = size
  loadData()
}

const handleCurrentChange = (page) => {
  currentPage.value = page
  loadData()
}

const handleRowContextMenu = (row, column, event) => {
  event.preventDefault()
  currentContextRow.value = row
  contextMenuLeft.value = event.clientX
  contextMenuTop.value = event.clientY
  contextMenuVisible.value = true
  
  nextTick(() => {
    const menu = document.querySelector('.context-menu')
    if (menu) {
      menu.focus()
    }
  })
}

const hideContextMenu = () => {
  contextMenuVisible.value = false
  currentContextRow.value = null
}

const handleContextEdit = () => {
  if (currentContextRow.value) {
    handleEdit(currentContextRow.value)
  }
  hideContextMenu()
}

const handleContextDelete = () => {
  if (currentContextRow.value) {
    handleDelete(currentContextRow.value)
  }
  hideContextMenu()
}

const handleContextAddData = () => {
  handleAdd()
  hideContextMenu()
}

// 处理指标变化，自动设置对应的分类
const handleIndicatorChange = (value) => {
  // 根据指标名称查找对应的分类
  const indicatorCategoryMap = {
    '体重': 5, // 假设5是"其他"分类
    '血压': 1, // 假设1是"血常规"分类
    '血糖': 5, // 假设5是"血糖"分类
    '心率': 5, // 假设5是"其他"分类
    '体温': 5, // 假设5是"其他"分类
    '血氧': 1  // 假设1是"血常规"分类
  }
  
  // 设置对应的分类
  form.category = indicatorCategoryMap[value] || ''

  // 若用户手动输入了新指标名称，则加入到下拉选项供后续复用
  if (typeof value === 'string' && value && !indicatorNameOptions.value.includes(value)) {
    indicatorNameOptions.value.push(value)
  }
}

// 打开新增指标对话框
const handleAddIndicator = () => {
  resetIndicatorForm()
  indicatorDialogVisible.value = true
}

// 处理分类筛选变化
const handleCategoryFilterChange = () => {
  loadData()
}

// 加载数据
const loadData = async () => {
  loading.value = true
  const params = {
    page: currentPage.value,
    pageSize: pageSize.value,
    keyword: searchKeyword.value || undefined,
    startDate: dateRange.value?.[0] || undefined,
    endDate: dateRange.value?.[1] || undefined,
  }
  if (categoryFilter.value) {
    const cat = indicatorCategoriesList.value.find(c => c.id === categoryFilter.value)
    if (cat) params.category = cat.name
  }
  try {
    const res = await getIndicators(params)
    tableData.value = Array.isArray(res?.items) ? res.items : []
    total.value = Number(res?.total || 0)
    const names = [...new Set(tableData.value.map(i => i.indicator || i.nameCn).filter(Boolean))]
    indicatorNameOptions.value = names
  } finally {
    loading.value = false
  }
}

const handleView = (row) => {
  ElMessage.info(`查看指标 ${row.indicator} 的记录`)
  // 跳转到指标详情页面
  router.push({
    name: 'indicatorDetail',
    params: { id: row.id, name: row.indicator }
  })
}

// 分析指标
const handleAnalyze = (row) => {
  console.log('分析指标', row)
  ElMessage.success(`开始分析指标: ${row.indicator}`)
  // 这里可以添加跳转到分析页面或打开分析弹窗的逻辑
}

const handleViewTrend = (row) => {
  ElMessage.info(`查看 ${row.indicator} 的趋势图`)
  // 这里可以跳转到趋势图页面或打开趋势图对话框
  router.push({
    name: 'IndicatorRecord',
    params: { id: row.id, name: row.indicator },
    query: { view: 'chart' }
  })
}

// 提交表单
const handleSubmit = async () => {
  try {
    await formRef.value.validate()
    const name = form.indicator
    const target = tableData.value.find(i => (i.indicator || i.nameCn) === name)
    if (!target) {
      ElMessage.warning('请先在“新增指标”中创建该指标，或选择已存在的指标')
      return
    }
    const payload = {
      date: form.measureDate,
      value: String(form.value),
      unit: form.unit,
      referenceMin: form.referenceMin ? Number(form.referenceMin) : undefined,
      referenceMax: form.referenceMax ? Number(form.referenceMax) : undefined,
      source: form.source || 'manual',
      note: form.note || ''
    }
    await createRecord(target.id, payload)
    ElMessage.success('添加成功')
    dialogVisible.value = false
    loadData()
  } catch {}
}

const resetForm = () => {
  Object.assign(form, {
    id: null,
    indicator: '',
    value: '',
    unit: '',
    referenceMin: '',
    referenceMax: '',
    measureDate: '',
    source: '',
    note: '',
    category: ''
  })
  if (formRef.value) {
    formRef.value.clearValidate()
  }
}

// 打开分类管理对话框
const openCategoryDialog = () => {
  indicatorNewCategoryName.value = ''
  indicatorEditingCategoryId.value = null
  indicatorCategoryDialogVisible.value = true
}

// 添加新分类（后端暂不支持，提示只读）
const addCategory = () => {
  ElMessage.warning('分类由后端维护，当前不可在前端新增')
}

// 编辑分类
const editCategory = (category) => {
  indicatorNewCategoryName.value = category.name
  indicatorEditingCategoryId.value = category.id
}

// 保存编辑的分类（后端暂不支持，提示只读）
const saveCategory = () => {
  ElMessage.warning('分类由后端维护，当前不可在前端编辑')
}

// 删除分类（后端暂不支持，提示只读）
const deleteCategory = () => {
  ElMessage.warning('分类由后端维护，当前不可在前端删除')
}

// 提交新增指标表单
const handleSubmitIndicator = async () => {
  try {
    await indicatorFormRef.value.validate()
    const categoryName = indicatorCategoryOptions.value.find(c => c.id === indicatorForm.category)?.name
    const payload = {
      nameCn: indicatorForm.name,
      nameEn: indicatorForm.nameEn || undefined,
      type: 'numeric',
      unit: indicatorForm.unit,
      referenceMin: indicatorForm.referenceMin ? Number(indicatorForm.referenceMin) : undefined,
      referenceMax: indicatorForm.referenceMax ? Number(indicatorForm.referenceMax) : undefined,
      categories: categoryName ? [categoryName] : undefined,
    }
    await createIndicator(payload)
    ElMessage.success('成功添加指标')
    indicatorDialogVisible.value = false
    loadData()
  } catch {}
}

// 重置新增指标表单
const resetIndicatorForm = () => {
  Object.assign(indicatorForm, {
    name: '',
    nameEn: '',
    unit: '',
    referenceMin: '',
    referenceMax: '',
    category: ''
  })
  if (indicatorFormRef.value) {
    indicatorFormRef.value.resetFields()
  }
}

// 点击页面其他地方隐藏右键菜单
const handleDocumentClick = () => {
  if (contextMenuVisible.value) {
    hideContextMenu()
  }
}

onMounted(async () => {
  document.addEventListener('click', handleDocumentClick)
  const cats = await listCategories({ page: 1, pageSize: 100 })
  const items = Array.isArray(cats?.items) ? cats.items : []
  indicatorCategoryOptions.value = items
  indicatorCategoriesList.value = items
  await loadData()
})
</script>

<style scoped>
.indicators-page {
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

.toolbar-card {
  margin-bottom: 16px;
}

.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.toolbar-left {
  display: flex;
  gap: 12px;
}

.toolbar-right {
  display: flex;
  align-items: center;
}

.table-card {
  min-height: 600px;
}

.pagination-wrapper {
  display: flex;
  justify-content: center;
  margin-top: 20px;
}

.value-high {
  color: var(--danger-color);
  font-weight: 600;
}

.value-low {
  color: var(--warning-color);
  font-weight: 600;
}

.value-normal {
  color: var(--text-primary);
}

.context-menu {
  position: fixed;
  background: white;
  border: 1px solid var(--border-color);
  border-radius: 6px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  z-index: 1000;
  min-width: 120px;
  padding: 4px 0;
}

.menu-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  cursor: pointer;
  font-size: 14px;
  color: var(--text-primary);
  transition: background-color 0.2s;
}

.menu-item:hover {
  background-color: var(--el-color-primary-light-9);
}

.menu-divider {
  height: 1px;
  background-color: var(--border-color);
  margin: 4px 0;
}

.text-center {
  text-align: center;
  line-height: 32px;
}

.category-form {
  display: flex;
  align-items: center;
  gap: 10px;
}

.category-select-container {
  display: flex;
  align-items: center;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .toolbar {
    flex-direction: column;
    gap: 16px;
    align-items: stretch;
  }
  
  .toolbar-left,
  .toolbar-right {
    justify-content: center;
  }
  
  .toolbar-right {
    flex-direction: column;
    gap: 12px;
  }
}
</style>
