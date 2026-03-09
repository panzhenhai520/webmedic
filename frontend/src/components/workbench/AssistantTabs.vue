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
                <div class="similar-actions">
                  <el-tag size="small" type="success">
                    相似度: {{ (item.score * 100).toFixed(1) }}%
                  </el-tag>
                  <el-button
                    size="small"
                    type="primary"
                    link
                    @click="handleViewSimilarity(item)"
                  >
                    查看详情
                  </el-button>
                </div>
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

    <!-- 相似性详情对话框 -->
    <el-dialog
      v-model="similarityDialogVisible"
      title="相似性详情对比"
      width="80%"
      :close-on-click-modal="false"
    >
      <div v-if="currentSimilarCase" class="similarity-detail">
        <div class="detail-header">
          <div class="header-item">
            <span class="label">文件名：</span>
            <span>{{ currentSimilarCase.file_name }}</span>
          </div>
          <div class="header-item">
            <span class="label">相似度：</span>
            <el-tag type="success" size="large">
              {{ (currentSimilarCase.score * 100).toFixed(1) }}%
            </el-tag>
          </div>
        </div>

        <!-- 结构化对比 -->
        <div class="comparison-container">
          <!-- 主诉对比 -->
          <div class="comparison-section">
            <h4 class="section-title">主诉对比</h4>
            <div class="comparison-row">
              <div class="comparison-col current">
                <div class="col-header">当前患者</div>
                <div class="col-content" v-html="highlightSimilarText(
                  currentSimilarCase.current_chief_complaint,
                  currentSimilarCase.similar_chief_complaint
                )"></div>
              </div>
              <div class="comparison-col similar">
                <div class="col-header">相似病历</div>
                <div class="col-content" v-html="highlightSimilarText(
                  currentSimilarCase.similar_chief_complaint,
                  currentSimilarCase.current_chief_complaint
                )"></div>
              </div>
            </div>
          </div>

          <!-- 现病史对比 -->
          <div class="comparison-section">
            <h4 class="section-title">现病史对比</h4>
            <div class="comparison-row">
              <div class="comparison-col current">
                <div class="col-header">当前患者</div>
                <div class="col-content" v-html="highlightSimilarText(
                  currentSimilarCase.current_present_illness,
                  currentSimilarCase.similar_present_illness
                )"></div>
              </div>
              <div class="comparison-col similar">
                <div class="col-header">相似病历</div>
                <div class="col-content" v-html="highlightSimilarText(
                  currentSimilarCase.similar_present_illness,
                  currentSimilarCase.current_present_illness
                )"></div>
              </div>
            </div>
          </div>
        </div>

        <div class="detail-section">
          <el-alert
            title="说明"
            type="info"
            :closable="false"
          >
            <p>• 相似度基于语义向量计算，系统通过 BGE-M3 模型将文本转换为向量，然后使用余弦相似度匹配</p>
            <p>• <span class="highlight-demo">红色高亮</span> 表示两段文本中相似或相同的内容</p>
            <p>• 相似度越高，表示两段文本在语义上越接近</p>
          </el-alert>
        </div>
      </div>

      <template #footer>
        <el-button @click="similarityDialogVisible = false">关闭</el-button>
        <el-button
          type="primary"
          @click="handleViewDocument(currentSimilarCase?.document_id)"
        >
          查看完整 PDF
        </el-button>
      </template>
    </el-dialog>
  </el-card>
</template>

<script setup>
import { computed, watch, ref } from 'vue'
import { Memo } from '@element-plus/icons-vue'
import { useWorkbenchStore } from '@/stores/workbench'
import DraftView from './DraftView.vue'

const workbenchStore = useWorkbenchStore()

// 相似性详情对话框
const similarityDialogVisible = ref(false)
const currentSimilarCase = ref(null)

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

// 查看相似性详情
const handleViewSimilarity = (item) => {
  currentSimilarCase.value = item
  similarityDialogVisible.value = true
}

// 高亮相似文本
const highlightSimilarText = (text1, text2) => {
  if (!text1 || !text2) return text1 || '无'

  // 将文本分词（简单按字符分）
  const chars1 = text1.split('')
  const chars2 = text2.split('')

  // 找出相同的字符序列
  const commonChars = new Set()

  // 查找连续的相同子串（至少2个字符）
  for (let i = 0; i < chars1.length - 1; i++) {
    for (let j = 0; j < chars2.length - 1; j++) {
      let k = 0
      while (
        i + k < chars1.length &&
        j + k < chars2.length &&
        chars1[i + k] === chars2[j + k]
      ) {
        if (k >= 1) { // 至少2个字符才算相似
          for (let m = 0; m <= k; m++) {
            commonChars.add(i + m)
          }
        }
        k++
      }
    }
  }

  // 构建高亮后的HTML
  let result = ''
  for (let i = 0; i < chars1.length; i++) {
    if (commonChars.has(i)) {
      result += `<span class="highlight">${chars1[i]}</span>`
    } else {
      result += chars1[i]
    }
  }

  return result || text1
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

.similar-actions {
  display: flex;
  align-items: center;
  gap: 10px;
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

/* 相似性详情对话框样式 */
.similarity-detail {
  padding: 10px;
}

.detail-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px;
  background: #f5f7fa;
  border-radius: 4px;
  margin-bottom: 20px;
}

.header-item {
  display: flex;
  align-items: center;
  gap: 10px;
}

.header-item .label {
  font-weight: 600;
  color: #606266;
}

.comparison-container {
  margin-bottom: 20px;
}

.comparison-section {
  margin-bottom: 25px;
}

.section-title {
  margin: 0 0 15px 0;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  padding-bottom: 10px;
  border-bottom: 2px solid #409eff;
}

.comparison-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

.comparison-col {
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  overflow: hidden;
}

.col-header {
  padding: 10px 15px;
  font-weight: 600;
  font-size: 14px;
  color: white;
}

.comparison-col.current .col-header {
  background: #409eff;
}

.comparison-col.similar .col-header {
  background: #67c23a;
}

.col-content {
  padding: 15px;
  min-height: 80px;
  line-height: 1.8;
  font-size: 14px;
  color: #606266;
  background: white;
}

.col-content :deep(.highlight) {
  background-color: #fef0f0;
  color: #f56c6c;
  font-weight: 600;
  padding: 2px 0;
}

.highlight-demo {
  background-color: #fef0f0;
  color: #f56c6c;
  font-weight: 600;
  padding: 2px 4px;
  border-radius: 2px;
}

.detail-section {
  margin-bottom: 20px;
}

.detail-section h4 {
  margin: 0 0 10px 0;
  font-size: 14px;
  font-weight: 600;
  color: #303133;
}

.detail-section p {
  margin: 5px 0;
  font-size: 14px;
  color: #606266;
}

.detail-section .el-alert p {
  margin: 5px 0;
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
