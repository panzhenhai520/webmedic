<template>
  <div class="doctor-workbench">
    <el-container>
      <!-- 顶部标题栏 -->
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

      <!-- 主体内容区 - 三栏布局 -->
      <el-container class="main-container">
        <!-- 左侧：患者信息与控制区 -->
        <el-aside width="300px" class="left-aside">
          <div class="aside-content">
            <!-- 患者信息卡片 -->
            <div class="info-section">
              <PatientInfoCard />
            </div>

            <!-- 控制面板 -->
            <div class="control-section">
              <ControlPanel />
            </div>
          </div>
        </el-aside>

        <!-- 中间：医患对话区（可折叠） -->
        <transition name="slide">
          <el-main
            v-show="!dialogueCollapsed"
            class="center-main"
            style="max-width: 500px; flex: 0 0 500px; padding: 20px; position: relative;"
          >
            <!-- 折叠按钮 -->
            <el-button
              class="collapse-button"
              :icon="ArrowLeft"
              circle
              size="small"
              @click="toggleDialogue"
              title="折叠对话区"
            />
            <DialogueArea />
          </el-main>
        </transition>

        <!-- 展开按钮（对话区折叠时显示） -->
        <div v-if="dialogueCollapsed" class="expand-trigger" @click="toggleDialogue">
          <el-button :icon="ArrowRight" circle size="small" title="展开对话区" />
        </div>

        <!-- 右侧：智能辅助区 -->
        <el-aside
          class="right-aside"
          :style="{
            width: 'auto',
            flex: 1,
            minWidth: dialogueCollapsed ? '700px' : '500px'
          }"
        >
          <AssistantTabs />
        </el-aside>
      </el-container>
    </el-container>
  </div>
</template>

<script setup>
import { onMounted, ref, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Notebook, House, Clock, Folder, ArrowLeft, ArrowRight } from '@element-plus/icons-vue'
import { useWorkbenchStore } from '@/stores/workbench'
import { getDefaultDoctor, getDefaultPatient } from '@/api'
import PatientInfoCard from '@/components/workbench/PatientInfoCard.vue'
import ControlPanel from '@/components/workbench/ControlPanel.vue'
import DialogueArea from '@/components/workbench/DialogueArea.vue'
import AssistantTabs from '@/components/workbench/AssistantTabs.vue'

const router = useRouter()
const route = useRoute()
const workbenchStore = useWorkbenchStore()

// 对话区折叠状态
const dialogueCollapsed = ref(false)

// 切换对话区折叠状态
const toggleDialogue = () => {
  dialogueCollapsed.value = !dialogueCollapsed.value
}

// 当前激活的菜单
const activeMenu = computed(() => route.path)

// 医生信息
const doctorInfo = computed(() => workbenchStore.doctorInfo)

// 菜单选择
const handleMenuSelect = (index) => {
  router.push(index)
}

// 初始化数据
const initData = async () => {
  try {
    // 获取默认医生（从真实API）
    const doctorRes = await getDefaultDoctor()
    if (doctorRes.success) {
      workbenchStore.setDoctorInfo(doctorRes.data)
      console.log('医生信息加载成功:', doctorRes.data)
    }

    // 获取默认患者（从真实API）
    const patientRes = await getDefaultPatient()
    if (patientRes.success) {
      workbenchStore.setPatientInfo(patientRes.data)
      console.log('患者信息加载成功:', patientRes.data)
    }

    // 移除成功提示，避免页面切换时的干扰
  } catch (error) {
    console.error('初始化失败:', error)
    ElMessage.error('工作站初始化失败，请检查后端服务')
  }
}

// 组件挂载时初始化
onMounted(() => {
  initData()
})
</script>

<style scoped>
.doctor-workbench {
  width: 100%;
  height: 100vh;
  background: #f5f7fa;
  overflow: hidden;
}

.el-container {
  height: 100%;
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

/* 主体内容区 */
.main-container {
  height: calc(100vh - 60px);
  position: relative;
}

/* 左侧 */
.left-aside {
  background: white;
  border-right: 1px solid #e4e7ed;
  overflow-y: auto;
}

.aside-content {
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

/* 中间对话区 */
.center-main {
  background: white;
  border-right: 1px solid #e4e7ed;
  overflow: hidden;
}

/* 折叠按钮 */
.collapse-button {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  right: 10px;
  z-index: 10;
  background: white;
  border: 1px solid #dcdfe6;
}

.collapse-button:hover {
  background: #f5f7fa;
  border-color: #409eff;
  color: #409eff;
}

/* 展开触发器 */
.expand-trigger {
  width: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: white;
  border-right: 1px solid #e4e7ed;
  cursor: pointer;
  transition: all 0.3s;
}

.expand-trigger:hover {
  background: #f5f7fa;
}

.expand-trigger .el-button {
  background: white;
  border: 1px solid #dcdfe6;
}

.expand-trigger:hover .el-button {
  border-color: #409eff;
  color: #409eff;
}

/* 右侧 */
.right-aside {
  background: white;
  overflow-y: auto;
  transition: all 0.3s ease;
}

/* 滑动动画 */
.slide-enter-active,
.slide-leave-active {
  transition: all 0.3s ease;
}

.slide-enter-from {
  transform: translateX(-100%);
  opacity: 0;
}

.slide-leave-to {
  transform: translateX(-100%);
  opacity: 0;
}

/* 滚动条样式 */
.left-aside::-webkit-scrollbar,
.right-aside::-webkit-scrollbar {
  width: 6px;
}

.left-aside::-webkit-scrollbar-track,
.right-aside::-webkit-scrollbar-track {
  background: #f1f1f1;
}

.left-aside::-webkit-scrollbar-thumb,
.right-aside::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

.left-aside::-webkit-scrollbar-thumb:hover,
.right-aside::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}
</style>
