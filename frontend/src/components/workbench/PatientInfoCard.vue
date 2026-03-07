<template>
  <el-card class="patient-info-card" shadow="hover">
    <template #header>
      <div class="card-header">
        <span class="header-title">
          <el-icon><User /></el-icon>
          患者信息
        </span>
      </div>
    </template>

    <div class="info-content">
      <!-- 患者信息 -->
      <div class="info-section">
        <div class="info-item">
          <span class="label">姓名：</span>
          <span class="value highlight">{{ patientInfo?.patient_name || '-' }}</span>
        </div>
        <div class="info-item">
          <span class="label">性别：</span>
          <span class="value">{{ patientInfo?.gender || '-' }}</span>
        </div>
        <div class="info-item">
          <span class="label">年龄：</span>
          <span class="value">{{ patientInfo?.age || '-' }} 岁</span>
        </div>
        <div class="info-item">
          <span class="label">电话：</span>
          <span class="value">{{ patientInfo?.phone || '-' }}</span>
        </div>
      </div>
    </div>
  </el-card>
</template>

<script setup>
import { computed } from 'vue'
import { User } from '@element-plus/icons-vue'
import { useWorkbenchStore } from '@/stores/workbench'

const workbenchStore = useWorkbenchStore()

// 患者信息
const patientInfo = computed(() => workbenchStore.patientInfo)
</script>

<style scoped>
.patient-info-card {
  height: auto;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-title {
  font-size: 14px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 6px;
}

.info-content {
  padding: 0;
}

.info-section {
  margin-bottom: 0;
}

.info-item {
  display: flex;
  padding: 4px 0;
  font-size: 13px;
}

.info-item .label {
  color: #909399;
  min-width: 50px;
}

.info-item .value {
  color: #303133;
  font-weight: 500;
}

.info-item .value.highlight {
  color: #409eff;
  font-weight: 600;
}
</style>
