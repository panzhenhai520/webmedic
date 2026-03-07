<template>
  <div class="session-history">
    <el-container>
      <!-- 顶部导航栏 -->
      <el-header class="header">
        <div class="header-content">
          <div class="header-left">
            <h1>
              <el-icon><Notebook /></el-icon>
              Doctor Workbench
            </h1>
            <!-- 医生信息 -->
            <div v-if="doctorInfo" class="doctor-info">
              <el-divider direction="vertical" />
              <span class="doctor-name">{{ doctorInfo.doctor_name }}</span>
              <el-tag size="small" type="info">{{ doctorInfo.title }}</el-tag>
              <el-tag size="small" type="success">{{ doctorInfo.department }}</el-tag>
            </div>
          </div>
          <div class="header-nav">
            <el-menu
              mode="horizontal"
              :default-active="activeMenu"
              @select="handleMenuSelect"
              :ellipsis="false"
            >
              <el-menu-item index="/">
                <el-icon><House /></el-icon>
                <span>工作站</span>
              </el-menu-item>
              <el-menu-item index="/sessions">
                <el-icon><Clock /></el-icon>
                <span>会话历史</span>
              </el-menu-item>
              <el-menu-item index="/documents">
                <el-icon><Folder /></el-icon>
                <span>病历管理</span>
              </el-menu-item>
            </el-menu>
          </div>
          <div class="header-info">
            <el-tag type="success">阶段 9 - 完善与打磨</el-tag>
            <el-tag type="info">v0.1.0</el-tag>
          </div>
        </div>
      </el-header>

      <!-- 主体内容 -->
      <div class="main-content">
        <el-card class="header-card">
          <template #header>
            <div class="card-header">
              <span class="header-title">
                <el-icon><Clock /></el-icon>
                会话历史
              </span>
              <div class="header-actions">
                <el-select
                  v-model="statusFilter"
                  placeholder="状态筛选"
                  clearable
                  @change="loadSessions"
                  style="width: 150px; margin-right: 10px;"
                >
                  <el-option label="全部" value="" />
                  <el-option label="已创建" value="created" />
                  <el-option label="进行中" value="started" />
                  <el-option label="已结束" value="ended" />
                </el-select>
                <el-button :icon="Refresh" @click="loadSessions">
                  刷新
                </el-button>
              </div>
            </div>
          </template>

          <div class="stats-row">
            <el-statistic title="会话总数" :value="total" />
          </div>
        </el-card>

        <el-card class="table-card">
          <el-table
            :data="sessions"
            stripe
            style="width: 100%"
            v-loading="loading"
            @row-click="handleRowClick"
            :row-style="{ cursor: 'pointer' }"
          >
            <el-table-column type="index" label="序号" width="60" />
            <el-table-column prop="session_no" label="会话编号" width="180" />
            <el-table-column label="医生" width="150">
              <template #default="{ row }">
                <div>{{ row.doctor_name }}</div>
                <el-tag size="small" type="info">{{ row.doctor_title }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="患者" width="150">
              <template #default="{ row }">
                <div>{{ row.patient_name }}</div>
                <el-tag size="small">{{ row.patient_gender }} {{ row.patient_age }}岁</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="status" label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="getStatusType(row.status)" size="small">
                  {{ getStatusText(row.status) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="transcript_count" label="对话轮次" width="100" />
            <el-table-column prop="started_at" label="开始时间" width="160">
              <template #default="{ row }">
                {{ formatDate(row.started_at) }}
              </template>
            </el-table-column>
            <el-table-column prop="ended_at" label="结束时间" width="180">
              <template #default="{ row }">
                {{ row.ended_at ? formatDate(row.ended_at) : '-' }}
              </template>
            </el-table-column>
            <el-table-column label="操作" width="150" fixed="right">
              <template #default="{ row }">
                <el-button
                  type="primary"
                  size="small"
                  link
                  @click.stop="handleViewTranscripts(row.id)"
                >
                  查看对话
                </el-button>
              </template>
            </el-table-column>
          </el-table>

          <div class="pagination">
            <el-pagination
              v-model:current-page="currentPage"
              v-model:page-size="pageSize"
              :page-sizes="[10, 20, 50, 100]"
              :total="total"
              layout="total, sizes, prev, pager, next, jumper"
              @size-change="loadSessions"
              @current-change="loadSessions"
            />
          </div>
        </el-card>
      </div>

      <!-- 转写记录对话框 -->
      <el-dialog
        v-model="dialogVisible"
        title="会话对话记录"
        width="800px"
        :close-on-click-modal="false"
      >
        <div v-loading="dialogLoading" class="transcript-dialog">
          <div v-if="currentSession" class="session-info">
            <el-descriptions :column="2" border>
              <el-descriptions-item label="会话编号">
                {{ currentSession.session_no }}
              </el-descriptions-item>
              <el-descriptions-item label="状态">
                <el-tag :type="getStatusType(currentSession.status)">
                  {{ getStatusText(currentSession.status) }}
                </el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="开始时间">
                {{ formatDate(currentSession.started_at) }}
              </el-descriptions-item>
              <el-descriptions-item label="结束时间">
                {{ currentSession.ended_at ? formatDate(currentSession.ended_at) : '-' }}
              </el-descriptions-item>
            </el-descriptions>
          </div>

          <el-divider />

          <div class="transcript-list">
            <div
              v-for="item in transcripts"
              :key="item.id"
              class="transcript-item"
              :class="item.speaker_role"
            >
              <div class="speaker-label">
                <el-tag
                  :type="item.speaker_role === 'doctor' ? 'primary' : 'success'"
                  size="small"
                >
                  {{ item.speaker_role === 'doctor' ? '医生' : '患者' }}
                </el-tag>
                <span class="time">{{ formatTime(item.created_at) }}</span>
              </div>
              <div class="transcript-text">
                {{ item.transcript_text || '[无转写文本]' }}
              </div>
            </div>
            <el-empty v-if="transcripts.length === 0" description="暂无对话记录" />
          </div>
        </div>
      </el-dialog>
    </el-container>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Notebook, House, Clock, Folder, Refresh } from '@element-plus/icons-vue'
import { getSessionList, getSessionWithTranscripts } from '@/api/session'
import { useWorkbenchStore } from '@/stores/workbench'

const router = useRouter()
const workbenchStore = useWorkbenchStore()
const activeMenu = ref('/sessions')

// 医生信息
const doctorInfo = computed(() => workbenchStore.doctorInfo)

// 会话列表数据
const sessions = ref([])
const loading = ref(false)
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)
const statusFilter = ref('')

// 对话框数据
const dialogVisible = ref(false)
const dialogLoading = ref(false)
const currentSession = ref(null)
const transcripts = ref([])

// 加载会话列表
const loadSessions = async () => {
  loading.value = true
  try {
    const response = await getSessionList({
      page: currentPage.value,
      page_size: pageSize.value,
      status: statusFilter.value || undefined
    })

    if (response.success) {
      sessions.value = response.data.sessions
      total.value = response.data.total
    } else {
      ElMessage.error(response.message || '加载会话列表失败')
    }
  } catch (error) {
    console.error('加载会话列表失败:', error)
    ElMessage.error('加载会话列表失败')
  } finally {
    loading.value = false
  }
}

// 查看转写记录
const handleViewTranscripts = async (sessionId) => {
  dialogVisible.value = true
  dialogLoading.value = true

  try {
    const response = await getSessionWithTranscripts(sessionId)

    if (response.success) {
      currentSession.value = response.data
      transcripts.value = response.data.transcripts
    } else {
      ElMessage.error(response.message || '加载对话记录失败')
    }
  } catch (error) {
    console.error('加载对话记录失败:', error)
    ElMessage.error('加载对话记录失败')
  } finally {
    dialogLoading.value = false
  }
}

// 行点击事件
const handleRowClick = (row) => {
  handleViewTranscripts(row.id)
}

// 菜单选择
const handleMenuSelect = (index) => {
  router.push(index)
}

// 状态类型
const getStatusType = (status) => {
  const types = {
    created: 'info',
    started: 'success',
    ended: 'info'
  }
  return types[status] || 'info'
}

// 状态文本
const getStatusText = (status) => {
  const texts = {
    created: '已创建',
    started: '进行中',
    ended: '已结束'
  }
  return texts[status] || status
}

// 格式化日期
const formatDate = (date) => {
  if (!date) return '-'
  return new Date(date).toLocaleString('zh-CN')
}

// 格式化时间
const formatTime = (date) => {
  if (!date) return ''
  return new Date(date).toLocaleTimeString('zh-CN')
}

// 组件挂载时加载数据
onMounted(() => {
  loadSessions()
})
</script>

<style scoped>
.session-history {
  width: 100%;
  height: 100vh;
  background: #f5f7fa;
  overflow: hidden;
}

.el-container {
  height: 100%;
  flex-direction: column;
}

/* 顶部标题栏 */
.header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  display: flex;
  align-items: center;
  padding: 0 30px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  z-index: 100;
}

.header-content {
  width: 100%;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 30px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 15px;
}

.header-left h1 {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 10px;
}

/* 医生信息 */
.doctor-info {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 14px;
}

.doctor-name {
  font-weight: 600;
  color: #fff;
}

.doctor-info .el-divider {
  height: 20px;
  background: rgba(255, 255, 255, 0.3);
}

.doctor-info .el-tag {
  background: rgba(255, 255, 255, 0.2);
  border: none;
  color: #fff;
}

.header-nav {
  flex: 1;
  display: flex;
  justify-content: center;
}

.header-nav :deep(.el-menu) {
  background: transparent;
  border: none;
}

.header-nav :deep(.el-menu-item) {
  color: rgba(255, 255, 255, 0.8);
  border-bottom: 2px solid transparent;
}

.header-nav :deep(.el-menu-item:hover),
.header-nav :deep(.el-menu-item.is-active) {
  color: white;
  background: rgba(255, 255, 255, 0.1);
  border-bottom-color: white;
}

.header-info {
  display: flex;
  gap: 10px;
  align-items: center;
}

/* 主体内容 */
.main-content {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
}

.header-card {
  margin-bottom: 20px;
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

.header-actions {
  display: flex;
  align-items: center;
}

.stats-row {
  display: flex;
  gap: 40px;
}

.table-card {
  margin-bottom: 20px;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

/* 对话框样式 */
.transcript-dialog {
  min-height: 300px;
}

.session-info {
  margin-bottom: 20px;
}

.transcript-list {
  max-height: 500px;
  overflow-y: auto;
}

.transcript-item {
  margin-bottom: 15px;
  padding: 12px;
  background: #f5f7fa;
  border-radius: 8px;
}

.transcript-item.doctor {
  background: #e3f2fd;
}

.transcript-item.patient {
  background: #e8f5e9;
}

.speaker-label {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 8px;
}

.time {
  font-size: 12px;
  color: #909399;
}

.transcript-text {
  font-size: 14px;
  line-height: 1.6;
  color: #303133;
}
</style>
