<template>
  <el-card class="dialogue-area" shadow="hover">
    <template #header>
      <div class="card-header">
        <span class="header-title">
          <el-icon><ChatDotRound /></el-icon>
          医患对话
        </span>
        <el-button
          size="small"
          :icon="Delete"
          @click="handleClearDialogues"
          :disabled="dialogueList.length === 0"
        >
          清空
        </el-button>
      </div>
    </template>

    <div class="dialogue-content" ref="dialogueContentRef">
      <!-- 聊天式对话列表 -->
      <div v-if="dialogueList.length > 0" class="chat-list">
        <div
          v-for="(item, index) in sortedDialogues"
          :key="index"
          :class="['chat-message', `chat-${item.speaker}`]"
        >
          <!-- 医生消息（左侧） -->
          <div v-if="item.speaker === 'doctor'" class="message-wrapper">
            <div class="message-avatar">
              <el-icon class="avatar-icon doctor-icon"><Avatar /></el-icon>
            </div>
            <div class="message-content">
              <div class="message-header">
                <span class="speaker-name">医生</span>
                <span class="message-time">{{ formatTime(item.timestamp) }}</span>
              </div>
              <div class="message-bubble doctor-bubble">
                {{ item.text }}
              </div>
            </div>
          </div>

          <!-- 患者消息（右侧） -->
          <div v-else class="message-wrapper">
            <div class="message-content">
              <div class="message-header right">
                <span class="message-time">{{ formatTime(item.timestamp) }}</span>
                <span class="speaker-name">患者</span>
              </div>
              <div class="message-bubble patient-bubble">
                {{ item.text }}
              </div>
            </div>
            <div class="message-avatar">
              <el-icon class="avatar-icon patient-icon"><User /></el-icon>
            </div>
          </div>
        </div>
      </div>

      <!-- 空状态 -->
      <div v-else class="empty-state">
        <el-empty description="暂无对话记录" :image-size="120">
          <template #description>
            <p>点击"医生说话"或"患者说话"开始录音</p>
          </template>
        </el-empty>
      </div>
    </div>
  </el-card>
</template>

<script setup>
import { ref, computed, watch, nextTick } from 'vue'
import { ElMessageBox } from 'element-plus'
import { ChatDotRound, Delete, Avatar, User } from '@element-plus/icons-vue'
import { useWorkbenchStore } from '@/stores/workbench'

const workbenchStore = useWorkbenchStore()

// 对话内容容器引用
const dialogueContentRef = ref(null)

// 对话列表
const dialogueList = computed(() => workbenchStore.dialogueList)

// 按时间排序的对话列表
const sortedDialogues = computed(() => {
  return [...dialogueList.value].sort((a, b) => {
    return new Date(a.timestamp) - new Date(b.timestamp)
  })
})

// 格式化时间
const formatTime = (timestamp) => {
  if (!timestamp) return ''
  const date = new Date(timestamp)
  return date.toLocaleTimeString('zh-CN', {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}

// 清空对话
const handleClearDialogues = () => {
  ElMessageBox.confirm('确定要清空所有对话记录吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  })
    .then(() => {
      workbenchStore.clearDialogues()
    })
    .catch(() => {
      // 取消操作
    })
}

// 监听对话列表变化，自动滚动到底部
watch(
  dialogueList,
  () => {
    nextTick(() => {
      if (dialogueContentRef.value) {
        dialogueContentRef.value.scrollTop = dialogueContentRef.value.scrollHeight
      }
    })
  },
  { deep: true }
)
</script>

<style scoped>
.dialogue-area {
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

.dialogue-content {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  max-height: calc(100vh - 300px);
  background: #f5f7fa;
}

/* 聊天列表 */
.chat-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

/* 聊天消息 */
.chat-message {
  display: flex;
  animation: fadeIn 0.3s ease-in;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 医生消息 - 左对齐 */
.chat-doctor {
  justify-content: flex-start;
}

/* 患者消息 - 右对齐 */
.chat-patient {
  justify-content: flex-end;
}

/* 消息包装器 */
.message-wrapper {
  display: flex;
  gap: 10px;
  max-width: 75%;
  align-items: flex-start;
}

/* 头像 */
.message-avatar {
  flex-shrink: 0;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #fff;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.avatar-icon {
  font-size: 20px;
}

.doctor-icon {
  color: #409eff;
}

.patient-icon {
  color: #67c23a;
}

/* 消息内容 */
.message-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

/* 消息头部 */
.message-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  color: #909399;
}

.message-header.right {
  justify-content: flex-end;
}

.speaker-name {
  font-weight: 600;
  color: #606266;
}

.message-time {
  color: #909399;
}

/* 消息气泡 */
.message-bubble {
  padding: 10px 14px;
  border-radius: 12px;
  font-size: 14px;
  line-height: 1.6;
  color: #303133;
  word-wrap: break-word;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.08);
  position: relative;
}

/* 医生气泡 - 蓝色 */
.doctor-bubble {
  background: #e3f2fd;
  border-radius: 12px 12px 12px 4px;
  border: 1px solid #bbdefb;
}

/* 患者气泡 - 绿色 */
.patient-bubble {
  background: #e8f5e9;
  border-radius: 12px 12px 4px 12px;
  border: 1px solid #c8e6c9;
}

/* 空状态 */
.empty-state {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  min-height: 300px;
}

.empty-state p {
  color: #909399;
  font-size: 13px;
  margin-top: 8px;
}

/* 滚动条样式 */
.dialogue-content::-webkit-scrollbar {
  width: 6px;
}

.dialogue-content::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.dialogue-content::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

.dialogue-content::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}
</style>
