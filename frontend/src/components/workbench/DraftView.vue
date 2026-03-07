<template>
  <div class="draft-view">
    <div v-if="draft" class="draft-content">
      <el-alert
        title="AI生成草稿，仅供医生参考"
        type="warning"
        :closable="false"
        show-icon
        class="draft-notice"
      />

      <div class="field-item">
        <div class="field-label">主诉</div>
        <div class="field-value">{{ draft.chief_complaint || '-' }}</div>
      </div>

      <div class="field-item">
        <div class="field-label">现病史</div>
        <div class="field-value">{{ draft.present_illness || '-' }}</div>
      </div>

      <div class="field-item">
        <div class="field-label">既往史</div>
        <div class="field-value">{{ draft.past_history || '-' }}</div>
      </div>

      <div class="field-item">
        <div class="field-label">过敏史</div>
        <div class="field-value">{{ draft.allergy_history || '-' }}</div>
      </div>

      <div class="field-item">
        <div class="field-label">体格检查</div>
        <div class="field-value">{{ draft.physical_exam || '-' }}</div>
      </div>

      <div class="field-item">
        <div class="field-label">初步诊断</div>
        <div class="field-value">{{ draft.preliminary_diagnosis || '-' }}</div>
      </div>

      <div class="field-item">
        <div class="field-label">建议检查</div>
        <div class="field-value">{{ draft.suggested_exams || '-' }}</div>
      </div>

      <div class="field-item">
        <div class="field-label">治疗方案</div>
        <div class="field-value" style="white-space: pre-line">{{ draft.treatment_plan || '-' }}</div>
      </div>
    </div>
    <el-empty v-else description="暂无病历草稿" :image-size="100" />
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useWorkbenchStore } from '@/stores/workbench'

const workbenchStore = useWorkbenchStore()

// 病历草稿
const draft = computed(() => workbenchStore.draft)
</script>

<style scoped>
.draft-view {
  padding: 10px;
}

.draft-notice {
  margin-bottom: 16px;
}

.draft-content {
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
</style>
