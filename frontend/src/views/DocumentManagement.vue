<template>
  <div class="document-management">
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
            <el-icon><Folder /></el-icon>
            病历文档管理
          </span>
          <div class="header-actions">
            <el-button type="primary" :icon="Upload" @click="handleUpload">
              上传病历
            </el-button>
            <el-button type="success" :icon="FolderOpened" @click="handleScanLocal">
              扫描本地目录
            </el-button>
            <el-button :icon="Refresh" @click="handleRebuildIndex">
              重建索引
            </el-button>
          </div>
        </div>
      </template>

      <div class="stats-row">
        <el-statistic title="文档总数" :value="totalDocuments" />
        <el-statistic title="已索引" :value="indexedDocuments" />
        <el-statistic title="待索引" :value="pendingDocuments" />
      </div>
    </el-card>

    <el-card class="table-card">
      <el-table
        :data="documents"
        stripe
        style="width: 100%"
        v-loading="loading"
        @row-click="handleViewDocument"
        :row-style="{ cursor: 'pointer' }"
      >
        <el-table-column type="index" label="序号" width="60" />
        <el-table-column prop="file_name" label="文件名" min-width="200" />
        <el-table-column prop="source_type" label="类型" width="80">
          <template #default="{ row }">
            <el-tag size="small">{{ row.source_type.toUpperCase() }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="parse_status" label="解析状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.parse_status)" size="small">
              {{ getStatusText(row.parse_status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="index_status" label="索引状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.index_status)" size="small">
              {{ getStatusText(row.index_status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button
              type="primary"
              size="small"
              link
              @click.stop="handleViewDocument(row)"
            >
              查看
            </el-button>
            <el-button
              type="primary"
              size="small"
              link
              v-if="row.index_status !== 'done'"
              @click.stop="handleIndexDocument(row.id)"
            >
              索引
            </el-button>
            <el-button type="danger" size="small" link @click.stop="handleDelete(row.id)">
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 上传对话框 -->
    <el-dialog v-model="uploadDialogVisible" title="上传病历文件" width="500px" @close="handleUploadDialogClose">
      <el-upload
        ref="uploadRef"
        :auto-upload="false"
        :on-change="handleFileChange"
        :on-remove="handleFileRemove"
        :file-list="fileList"
        accept=".pdf"
        multiple
        drag
      >
        <el-icon class="el-icon--upload"><upload-filled /></el-icon>
        <div class="el-upload__text">
          将 PDF 文件拖到此处，或<em>点击上传</em>
        </div>
        <template #tip>
          <div class="el-upload__tip">支持选择多个 PDF 文件批量上传</div>
        </template>
      </el-upload>
      <template #footer>
        <el-button @click="uploadDialogVisible = false">取消</el-button>
        <el-button
          type="primary"
          @click="handleConfirmUpload"
          :loading="uploading"
          :disabled="fileList.length === 0"
        >
          {{ uploading ? `上传中 (${uploadProgress}/${fileList.length})...` : `确定上传 (${fileList.length}个文件)` }}
        </el-button>
      </template>
    </el-dialog>

    <!-- 扫描对话框 -->
    <el-dialog v-model="scanDialogVisible" title="扫描本地目录" width="500px">
      <el-form :model="scanForm" label-width="100px">
        <el-form-item label="目录路径">
          <el-input
            v-model="scanForm.directory"
            placeholder="D:\webmedic\medical_records"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="scanDialogVisible = false">取消</el-button>
        <el-button
          type="primary"
          @click="handleConfirmScan"
          :loading="scanning"
        >
          {{ scanning ? '扫描中...' : '开始扫描' }}
        </el-button>
      </template>
    </el-dialog>

    <!-- PDF 查看对话框 -->
    <el-dialog
      v-model="pdfDialogVisible"
      :title="currentDocument?.file_name || '查看病历'"
      width="80%"
      :close-on-click-modal="false"
      class="pdf-dialog"
    >
      <div class="pdf-viewer">
        <iframe
          v-if="pdfUrl"
          :src="pdfUrl"
          width="100%"
          height="700px"
          frameborder="0"
        ></iframe>
        <el-empty v-else description="无法加载PDF文件" />
      </div>
    </el-dialog>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Folder,
  Upload,
  FolderOpened,
  Refresh,
  UploadFilled,
  Notebook,
  House,
  Clock
} from '@element-plus/icons-vue'
import {
  getDocumentList,
  scanLocalDirectory,
  rebuildIndex
} from '@/api'
import http from '@/api/http'
import { useWorkbenchStore } from '@/stores/workbench'

const router = useRouter()
const route = useRoute()
const workbenchStore = useWorkbenchStore()

// 医生信息
const doctorInfo = computed(() => workbenchStore.doctorInfo)

// 当前激活的菜单
const activeMenu = computed(() => route.path)

// 菜单选择
const handleMenuSelect = (index) => {
  router.push(index)
}

// 文档列表
const documents = ref([])
const loading = ref(false)

// 上传相关
const uploadDialogVisible = ref(false)
const uploading = ref(false)
const selectedFile = ref(null)
const uploadRef = ref(null)
const fileList = ref([])
const uploadProgress = ref(0)

// 扫描相关
const scanDialogVisible = ref(false)
const scanning = ref(false)
const scanForm = ref({
  directory: 'D:\\\\webmedic\\\\backend\\\\medical_records'
})

// PDF 查看相关
const pdfDialogVisible = ref(false)
const currentDocument = ref(null)
const pdfUrl = ref('')

// 统计数据
const totalDocuments = computed(() => documents.value.length)
const indexedDocuments = computed(
  () => documents.value.filter((doc) => doc.index_status === 'done').length
)
const pendingDocuments = computed(
  () => documents.value.filter((doc) => doc.index_status === 'pending').length
)

// 获取文档列表
const fetchDocuments = async () => {
  try {
    loading.value = true
    const response = await getDocumentList()
    documents.value = response.data.documents
  } catch (error) {
    console.error('获取文档列表失败:', error)
    ElMessage.error('获取文档列表失败')
  } finally {
    loading.value = false
  }
}

// 上传病历
const handleUpload = () => {
  uploadDialogVisible.value = true
  fileList.value = []
  uploadProgress.value = 0
}

// 文件选择
const handleFileChange = (file, files) => {
  fileList.value = files
}

// 文件移除
const handleFileRemove = (file, files) => {
  fileList.value = files
}

// 对话框关闭时清空文件列表
const handleUploadDialogClose = () => {
  fileList.value = []
  uploadProgress.value = 0
  if (uploadRef.value) {
    uploadRef.value.clearFiles()
  }
}

// 确认上传
const handleConfirmUpload = async () => {
  if (fileList.value.length === 0) {
    ElMessage.warning('请选择文件')
    return
  }

  try {
    uploading.value = true
    uploadProgress.value = 0

    let successCount = 0
    let failCount = 0

    // 逐个上传文件
    for (let i = 0; i < fileList.value.length; i++) {
      const file = fileList.value[i]
      uploadProgress.value = i + 1

      try {
        const formData = new FormData()
        formData.append('file', file.raw)

        await http.post('/documents/upload', formData, {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        })

        successCount++
      } catch (error) {
        console.error(`上传文件 ${file.name} 失败:`, error)
        failCount++
      }
    }

    // 显示结果
    if (failCount === 0) {
      ElMessage.success(`成功上传 ${successCount} 个文件并已自动索引`)
    } else {
      ElMessage.warning(`上传完成：成功 ${successCount} 个，失败 ${failCount} 个`)
    }

    uploadDialogVisible.value = false

    // 清空文件选择
    fileList.value = []
    uploadProgress.value = 0
    if (uploadRef.value) {
      uploadRef.value.clearFiles()
    }

    // 刷新列表
    await fetchDocuments()
  } catch (error) {
    console.error('上传失败:', error)
    ElMessage.error('上传失败')
  } finally {
    uploading.value = false
  }
}

// 扫描本地目录
const handleScanLocal = () => {
  scanDialogVisible.value = true
}

// 确认扫描
const handleConfirmScan = async () => {
  try {
    scanning.value = true
    const response = await scanLocalDirectory(scanForm.value.directory)

    ElMessage.success(response.message || '扫描完成并已自动索引')
    scanDialogVisible.value = false

    // 刷新列表
    await fetchDocuments()
  } catch (error) {
    console.error('扫描失败:', error)
    ElMessage.error(error.response?.data?.message || '扫描失败')
  } finally {
    scanning.value = false
  }
}

// 重建索引
const handleRebuildIndex = async () => {
  try {
    await ElMessageBox.confirm('确定要重建所有文档的索引吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    const response = await rebuildIndex()
    ElMessage.success(response.message || '索引重建完成')

    // 刷新列表
    await fetchDocuments()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('重建索引失败:', error)
      ElMessage.error(error.response?.data?.message || '重建索引失败')
    }
  }
}

// 索引单个文档
const handleIndexDocument = async (documentId) => {
  try {
    await http.post(`/index/index-document/${documentId}`)
    ElMessage.success('索引成功')
    await fetchDocuments()
  } catch (error) {
    console.error('索引失败:', error)
    ElMessage.error('索引失败')
  }
}

// 删除文档
const handleDelete = async (documentId) => {
  try {
    await ElMessageBox.confirm('确定要删除这个文档吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    await http.delete(`/documents/${documentId}`)
    ElMessage.success('删除成功')
    await fetchDocuments()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除失败:', error)
      ElMessage.error('删除失败')
    }
  }
}

// 查看文档
const handleViewDocument = (row) => {
  currentDocument.value = row
  // 构建PDF URL（通过后端代理访问）
  pdfUrl.value = `http://localhost:8001/api/v1/documents/${row.id}/view`
  pdfDialogVisible.value = true
}

// 获取状态类型
const getStatusType = (status) => {
  switch (status) {
    case 'done':
      return 'success'
    case 'pending':
      return 'info'
    case 'failed':
      return 'danger'
    default:
      return 'info'
  }
}

// 获取状态文本
const getStatusText = (status) => {
  switch (status) {
    case 'done':
      return '完成'
    case 'pending':
      return '待处理'
    case 'failed':
      return '失败'
    default:
      return status
  }
}

// 格式化日期
const formatDate = (dateString) => {
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN')
}

// 组件挂载时获取文档列表
onMounted(() => {
  fetchDocuments()
})
</script>

<style scoped>
.document-management {
  width: 100%;
  height: 100vh;
  background: #f5f7fa;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

/* 顶部导航栏 */
.header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  display: flex;
  align-items: center;
  padding: 0 30px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  z-index: 100;
  height: 60px;
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
  white-space: nowrap;
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

.header-nav :deep(.el-menu-item:hover) {
  background: rgba(255, 255, 255, 0.1);
  color: white;
}

.header-nav :deep(.el-menu-item.is-active) {
  color: white;
  border-bottom-color: white;
  background: rgba(255, 255, 255, 0.1);
}

.header-info {
  display: flex;
  gap: 10px;
  align-items: center;
}

/* 主体内容 */
.main-content {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
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
  font-size: 18px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 8px;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.stats-row {
  display: flex;
  gap: 40px;
  padding: 20px 0;
}

.table-card {
  min-height: 500px;
}

/* PDF 查看对话框 */
.pdf-dialog :deep(.el-dialog__body) {
  padding: 10px;
}

.pdf-viewer {
  width: 100%;
  min-height: 700px;
  display: flex;
  justify-content: center;
  align-items: center;
}
</style>
