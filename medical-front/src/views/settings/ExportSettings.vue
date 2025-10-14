<template>
  <div class="export-settings">
    <el-card class="section-card" shadow="never">
      <template #header>
        <h2>导出设置</h2>
      </template>

      <el-tabs v-model="activeTab">
        <el-tab-pane label="导出菜单设置" name="menu">
          <el-form label-width="140px" class="export-form">
            <el-form-item label="复制为纯文本">
              <el-switch v-model="options.plainText" @change="save" />
              <div class="option-desc">启用后，可将内容以纯文本复制到剪贴板。</div>
            </el-form-item>
            <el-form-item label="复制为图片">
              <el-switch v-model="options.copyImage" @change="save" />
              <div class="option-desc">将消息渲染为图片并复制到剪贴板（浏览器需支持）。</div>
            </el-form-item>
            <el-form-item label="导出为图片">
              <el-switch v-model="options.exportImage" @change="save" />
              <div class="option-desc">将消息或整段对话导出为PNG图片文件。</div>
            </el-form-item>
            <el-form-item label="导出为 Markdown">
              <el-switch v-model="options.markdown" @change="save" />
              <div class="option-desc">以Markdown格式导出，适合文档与知识库。</div>
            </el-form-item>
            <el-form-item label="导出为 Markdown（包含思考）">
              <el-switch v-model="options.markdownThoughts" @change="save" />
              <div class="option-desc">若模型返回思考内容，将一并导出；否则添加说明。</div>
            </el-form-item>
            <el-form-item label="导出为 Word">
              <el-switch v-model="options.word" @change="save" />
              <div class="option-desc">以Word（.doc）格式导出，便于办公场景使用。</div>
            </el-form-item>
          </el-form>
        </el-tab-pane>

        <el-tab-pane label="Markdown导出设置" name="markdown">
          <el-form label-width="180px" class="export-form">
            <el-form-item label="强制使用 $$ 标记 LaTeX 公式">
              <el-switch v-model="md.forceLatexDollar" @change="save" />
              <div class="option-desc">开启后，将在导出文档中使用 $$ 包裹公式，便于渲染。</div>
            </el-form-item>
            <el-form-item label="导出时包含模型名称">
              <el-switch v-model="md.includeModelName" @change="save" />
              <div class="option-desc">在导出文档头部附加当前模型名称，便于溯源。</div>
            </el-form-item>
            <el-form-item label="显示模型供应商">
              <el-switch v-model="md.showProvider" @change="save" />
              <div class="option-desc">与模型名称一并显示供应商（如 OpenAI、Azure 等）。</div>
            </el-form-item>
            <el-form-item label="启用标准化输出">
              <el-switch v-model="md.standardize" @change="save" />
              <div class="option-desc">统一标题、时间与元信息格式，便于版本管理与归档。</div>
            </el-form-item>
          </el-form>
        </el-tab-pane>

        
      </el-tabs>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useExportStore } from '@/stores/export'

const activeTab = ref('menu')
const exportStore = useExportStore()

const options = computed({
  get: () => exportStore.exportOptionsEnabled,
  set: (val) => (exportStore.exportOptionsEnabled = val),
})

const md = computed({
  get: () => exportStore.markdownSettings,
  set: (val) => (exportStore.markdownSettings = val),
})

 

const save = () => {
  exportStore.saveExportSettings()
}

onMounted(() => {
  exportStore.loadExportSettings()
})
</script>

<style scoped>
.export-settings {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.export-form {
  max-width: 760px;
}

.option-desc {
  margin-top: 6px;
  font-size: 12px;
  color: var(--text-secondary);
}
</style>