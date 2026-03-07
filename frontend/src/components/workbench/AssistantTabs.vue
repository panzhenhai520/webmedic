<template>
  <el-card class="assistant-tabs" shadow="hover">
    <template #header>
      <div class="card-header">
        <span class="header-title">
          <el-icon><Memo /></el-icon>
          智能辅助
        </span>
      </div>
    </template>

    <el-tabs v-model="activeTab" class="tabs-content">
      <!-- 追问建议 -->
      <el-tab-pane label="追问建议" name="questions">
        <div class="tab-content">
          <div v-if="followupQuestions.length > 0" class="questions-list">
            <div
              v-for="(question, index) in followupQuestions"
              :key="index"
              class="question-item"
            >
              <div class="question-number">{{ index + 1 }}</div>
              <div class="question-content">
                <div class="question-text">{{ question.question }}</div>
                <div v-if="question.reason" class="question-reason">
                  原因：{{ question.reason }}
                </div>
              </div>
            </div>
          </div>
          <el-empty v-else description="暂无追问建议" :image-size="100" />
        </div>
      </el-tab-pane>

      <!-- 结构化病历 -->
      <el-tab-pane label="结构化病历" name="structured">
        <div class="tab-content">
          <div v-if="structuredRecord" class="structured-content">
            <div class="field-item">
              <div class="field-label">主诉：</div>
              <div class="field-value">{{ structuredRecord.chief_complaint || '-' }}</div>
            </div>
            <div class="field-item">
              <div class="field-label">现病史：</div>
              <div class="field-value">{{ structuredRecord.present_illness || '-' }}</div>
            </div>
            <div class="field-item">
              <div class="field-label">既往史：</div>
              <div class="field-value">{{ structuredRecord.past_history || '-' }}</div>
            </div>
            <div class="field-item">
              <div class="field-label">过敏史：</div>
              <div class="field-value">{{ structuredRecord.allergy_history || '-' }}</div>
            </div>
            <div class="field-item">
              <div class="field-label">体格检查：</div>
              <div class="field-value">{{ structuredRecord.physical_exam || '-' }}</div>
            </div>
            <div class="field-item">
              <div class="field-label">初步诊断：</div>
              <div class="field-value">{{ structuredRecord.preliminary_diagnosis || '-' }}</div>
            </div>
            <div class="field-item">
              <div class="field-label">建议检查：</div>
              <div class="field-value">{{ structuredRecord.suggested_exams || '-' }}</div>
            </div>
            <div class="field-item">
              <div class="field-label">风险标记：</div>
              <div class="field-value">{{ structuredRecord.warning_flags || '-' }}</div>
            </div>
          </div>
          <el-empty v-else description="暂无结构化病历数据" :image-size="100" />
        </div>
      </el-tab-pane>

      <!-- 病历草稿 -->
      <el-tab-pane label="病历草稿" name="draft">
        <div class="tab-content">
          <DraftView />
        </div>
      </el-tab-pane>

      <!-- 相似病历 -->
      <el-tab-pane label="相似病历" name="similar">
        <div class="tab-content">
          <div v-if="similarCases.length > 0" class="similar-list">
            <div
              v-for="(item, index) in similarCases"
              :key="index"
              class="similar-item"
            >
              <div class="similar-header">
                <span
                  class="similar-title clickable"
                  @click="handleViewDocument(item.document_id)"
                  title="点击查看 PDF 文件"
                >
                  {{ item.file_name }}
                </span>
                <el-tag size="small" type="success">
                  相似度: {{ (item.score * 100).toFixed(1) }}%
                </el-tag>
              </div>
              <div class="similar-reason">{{ item.reason_text }}</div>
            </div>
          </div>
          <el-empty v-else description="暂无相似病历" :image-size="100" />
        </div>
      </el-tab-pane>

      <!-- 风险提示 -->
      <el-tab-pane label="风险提示" name="warnings">
        <div class="tab-content">
          <div v-if="clinicalHints.length > 0" class="hints-list">
            <el-alert
              v-for="(hint, index) in clinicalHints"
              :key="index"
              :title="hint.hint_title"
              :type="getHintType(hint.severity)"
              :description="hint.hint_content"
              show-icon
              :closable="false"
              class="hint-item"
            />
          </div>
          <el-empty v-else description="暂无风险提示" :image-size="100" />
        </div>
      </el-tab-pane>
    </el-tabs>
  </el-card>
</template>

<script setup>
import { computed, watch } from 'vue'
import { Memo } from '@element-plus/icons-vue'
import { useWorkbenchStore } from '@/stores/workbench'
import DraftView from './DraftView.vue'

const workbenchStore = useWorkbenchStore()

// 当前激活的标签页（双向绑定到 store）
const activeTab = computed({
  get: () => workbenchStore.activeAssistantTab,
  set: (value) => {
    workbenchStore.setActiveAssistantTab(value)
  }
})

// 监听 store 中的变化
watch(() => workbenchStore.activeAssistantTab, (newVal) => {
  console.log('AssistantTabs: activeTab 变化为', newVal)
})

// 结构化病历
const structuredRecord = computed(() => workbenchStore.structuredRecord)

// 相似病历
const similarCases = computed(() => workbenchStore.similarCases)

// 临床提示
const clinicalHints = computed(() => workbenchStore.clinicalHints)

// 追问建议
const followupQuestions = computed(() => workbenchStore.followupQuestions)

// 获取提示类型
const getHintType = (severity) => {
  switch (severity) {
    case 'high':
      return 'error'
    case 'warn':
      return 'warning'
    default:
      return 'info'
  }
}

// 查看文档
const handleViewDocument = (documentId) => {
  // 在新标签页打开 PDF
  const url = `/api/v1/documents/view/${documentId}`
  window.open(url, '_blank')
}

// 切换到指定标签页
const switchToTab = (tabName) => {
  activeTab.value = tabName
}

// 暴露方法供父组件调用
defineExpose({
  switchToTab
})
</script>

<style scoped>
.assistant-tabs {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-title {
  font-size: 16px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 8px;
}

.tabs-content {
  flex: 1;
  overflow: hidden;
}

.tab-content {
  height: calc(100vh - 350px);
  overflow-y: auto;
  padding: 10px;
}

/* 结构化病历样式 */
.structured-content {
  padding: 10px;
}

.field-item {
  margin-bottom: 16px;
  padding: 12px;
  background: #f9f9f9;
  border-radius: 4px;
  border-left: 3px solid #409eff;
}

.field-label {
  font-size: 14px;
  font-weight: 600;
  color: #606266;
  margin-bottom: 8px;
}

.field-value {
  font-size: 14px;
  color: #303133;
  line-height: 1.6;
}

/* 相似病历样式 */
.similar-list {
  padding: 10px;
}

.similar-item {
  margin-bottom: 16px;
  padding: 12px;
  background: #f9f9f9;
  border-radius: 4px;
  border: 1px solid #e4e7ed;
}

.similar-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.similar-title {
  font-size: 14px;
  font-weight: 600;
  color: #303133;
}

.similar-title.clickable {
  color: #409eff;
  cursor: pointer;
  text-decoration: underline;
  text-decoration-style: dotted;
}

.similar-title.clickable:hover {
  color: #66b1ff;
  text-decoration-style: solid;
}

.similar-reason {
  font-size: 13px;
  color: #606266;
  line-height: 1.6;
}

/* 风险提示样式 */
.hints-list {
  padding: 10px;
}

.hint-item {
  margin-bottom: 12px;
}

/* 追问建议样式 */
.questions-list {
  padding: 10px;
}

.question-item {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
  padding: 12px;
  background: #f9f9f9;
  border-radius: 4px;
}

.question-number {
  flex-shrink: 0;
  width: 28px;
  height: 28px;
  line-height: 28px;
  text-align: center;
  background: #409eff;
  color: white;
  border-radius: 50%;
  font-size: 14px;
  font-weight: 600;
}

.question-content {
  flex: 1;
}

.question-text {
  font-size: 14px;
  color: #303133;
  font-weight: 500;
  margin-bottom: 6px;
}

.question-reason {
  font-size: 13px;
  color: #909399;
  line-height: 1.6;
}

/* 滚动条样式 */
.tab-content::-webkit-scrollbar {
  width: 6px;
}

.tab-content::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.tab-content::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

.tab-content::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}
</style>
