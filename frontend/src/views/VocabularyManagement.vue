<template>
  <div class="vocabulary-management">
    <!-- 顶部导航 -->
    <el-page-header @back="goBack" class="page-header">
      <template #content>
        <span class="page-title">医学词库维护</span>
      </template>
    </el-page-header>

    <!-- 筛选和操作栏 -->
    <el-card class="filter-card" shadow="never">
      <el-form :inline="true" :model="filterForm" class="filter-form">
        <el-form-item label="分类">
          <el-select v-model="filterForm.category" placeholder="全部分类" clearable style="width: 150px">
            <el-option label="身体部位" value="body_parts" />
            <el-option label="症状" value="symptoms" />
            <el-option label="疾病" value="diseases" />
            <el-option label="方位词" value="directions" />
          </el-select>
        </el-form-item>

        <el-form-item label="专科">
          <el-select v-model="filterForm.specialty" placeholder="全部专科" clearable style="width: 150px">
            <el-option label="骨科" value="骨科" />
            <el-option label="内科" value="内科" />
            <el-option label="外科" value="外科" />
            <el-option label="心内科" value="心内科" />
            <el-option label="消化科" value="消化科" />
            <el-option label="呼吸科" value="呼吸科" />
          </el-select>
        </el-form-item>

        <el-form-item label="关键词">
          <el-input
            v-model="filterForm.keyword"
            placeholder="搜索标准名称或关键词"
            clearable
            style="width: 200px"
            @keyup.enter="handleSearch"
          />
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="handleSearch" :icon="Search">搜索</el-button>
          <el-button @click="handleReset">重置</el-button>
          <el-button type="success" @click="handleAdd" :icon="Plus">新增词汇</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 数据表格 -->
    <el-card class="table-card" shadow="never">
      <el-table
        :data="tableData"
        v-loading="loading"
        stripe
        style="width: 100%"
      >
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="standard_name" label="标准名称" width="150" />
        <el-table-column prop="category" label="分类" width="120">
          <template #default="{ row }">
            <el-tag :type="getCategoryType(row.category)" size="small">
              {{ getCategoryLabel(row.category) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="specialty" label="专科" width="100">
          <template #default="{ row }">
            <el-tag v-if="row.specialty" type="info" size="small">
              {{ row.specialty }}
            </el-tag>
            <span v-else class="text-muted">-</span>
          </template>
        </el-table-column>
        <el-table-column prop="keywords" label="关键词" min-width="200">
          <template #default="{ row }">
            <el-tag
              v-for="(keyword, index) in row.keywords.slice(0, 3)"
              :key="index"
              size="small"
              style="margin-right: 5px"
            >
              {{ keyword }}
            </el-tag>
            <el-tag v-if="row.keywords.length > 3" size="small" type="info">
              +{{ row.keywords.length - 3 }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="row.status === 'active' ? 'success' : 'info'" size="small">
              {{ row.status === 'active' ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="handleEdit(row)">
              编辑
            </el-button>
            <el-button link type="danger" size="small" @click="handleDelete(row)">
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-container">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.page_size"
          :page-sizes="[10, 20, 50, 100]"
          :total="pagination.total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handlePageChange"
        />
      </div>
    </el-card>

    <!-- 新增/编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="600px"
      @close="handleDialogClose"
    >
      <el-form
        ref="formRef"
        :model="formData"
        :rules="formRules"
        label-width="100px"
      >
        <el-form-item label="分类" prop="category">
          <el-select v-model="formData.category" placeholder="请选择分类" style="width: 100%">
            <el-option label="身体部位" value="body_parts" />
            <el-option label="症状" value="symptoms" />
            <el-option label="疾病" value="diseases" />
            <el-option label="方位词" value="directions" />
          </el-select>
        </el-form-item>

        <el-form-item label="专科" prop="specialty">
          <el-select v-model="formData.specialty" placeholder="请选择专科（可选）" clearable style="width: 100%">
            <el-option label="骨科" value="骨科" />
            <el-option label="内科" value="内科" />
            <el-option label="外科" value="外科" />
            <el-option label="心内科" value="心内科" />
            <el-option label="消化科" value="消化科" />
            <el-option label="呼吸科" value="呼吸科" />
          </el-select>
        </el-form-item>

        <el-form-item label="标准名称" prop="standard_name">
          <el-input
            v-model="formData.standard_name"
            placeholder="请输入标准名称"
            @blur="handleCheckSimilar"
          />
          <div v-if="similarItems.length > 0" class="similar-warning">
            <el-alert
              title="发现相似词汇"
              type="warning"
              :closable="false"
              show-icon
            >
              <template #default>
                <div v-for="item in similarItems" :key="item.id" class="similar-item">
                  {{ item.standard_name }} (相似度: {{ (item.similarity * 100).toFixed(0) }}%)
                </div>
              </template>
            </el-alert>
          </div>
        </el-form-item>

        <el-form-item label="关键词" prop="keywords">
          <div class="keywords-input">
            <el-tag
              v-for="(keyword, index) in formData.keywords"
              :key="index"
              closable
              @close="handleRemoveKeyword(index)"
              style="margin-right: 5px; margin-bottom: 5px"
            >
              {{ keyword }}
            </el-tag>
            <el-input
              v-if="keywordInputVisible"
              ref="keywordInputRef"
              v-model="keywordInputValue"
              size="small"
              style="width: 100px"
              @keyup.enter="handleAddKeyword"
              @blur="handleAddKeyword"
            />
            <el-button
              v-else
              size="small"
              @click="showKeywordInput"
            >
              + 添加关键词
            </el-button>
          </div>
        </el-form-item>

        <el-form-item label="描述" prop="description">
          <el-input
            v-model="formData.description"
            type="textarea"
            :rows="3"
            placeholder="请输入描述（可选）"
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">
          保存
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Plus } from '@element-plus/icons-vue'
import {
  getVocabularyList,
  checkSimilarVocabulary,
  createVocabulary,
  updateVocabulary,
  deleteVocabulary
} from '@/api/vocabulary'

const router = useRouter()

// 返回上一页
const goBack = () => {
  router.push('/')
}

// 筛选表单
const filterForm = reactive({
  category: '',
  specialty: '',
  keyword: ''
})

// 表格数据
const tableData = ref([])
const loading = ref(false)

// 分页
const pagination = reactive({
  page: 1,
  page_size: 20,
  total: 0
})

// 对话框
const dialogVisible = ref(false)
const dialogTitle = ref('新增词汇')
const formRef = ref(null)
const formData = reactive({
  id: null,
  category: '',
  specialty: '',
  standard_name: '',
  keywords: [],
  description: ''
})

// 表单验证规则
const formRules = {
  category: [{ required: true, message: '请选择分类', trigger: 'change' }],
  standard_name: [{ required: true, message: '请输入标准名称', trigger: 'blur' }],
  keywords: [
    { required: true, message: '请至少添加一个关键词', trigger: 'change' },
    { type: 'array', min: 1, message: '请至少添加一个关键词', trigger: 'change' }
  ]
}

// 相似词
const similarItems = ref([])

// 关键词输入
const keywordInputVisible = ref(false)
const keywordInputValue = ref('')
const keywordInputRef = ref(null)

// 提交状态
const submitting = ref(false)

// 获取分类标签
const getCategoryLabel = (category) => {
  const labels = {
    body_parts: '身体部位',
    symptoms: '症状',
    diseases: '疾病',
    directions: '方位词'
  }
  return labels[category] || category
}

// 获取分类类型
const getCategoryType = (category) => {
  const types = {
    body_parts: 'primary',
    symptoms: 'warning',
    diseases: 'danger',
    directions: 'info'
  }
  return types[category] || ''
}

// 加载数据
const loadData = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.page_size,
      category: filterForm.category || undefined,
      specialty: filterForm.specialty || undefined,
      keyword: filterForm.keyword || undefined,
      status: 'active'
    }

    const res = await getVocabularyList(params)
    if (res.success) {
      tableData.value = res.data.items
      pagination.total = res.data.total
    }
  } catch (error) {
    ElMessage.error('加载数据失败: ' + error.message)
  } finally {
    loading.value = false
  }
}

// 搜索
const handleSearch = () => {
  pagination.page = 1
  loadData()
}

// 重置
const handleReset = () => {
  filterForm.category = ''
  filterForm.specialty = ''
  filterForm.keyword = ''
  pagination.page = 1
  loadData()
}

// 分页变化
const handleSizeChange = () => {
  pagination.page = 1
  loadData()
}

const handlePageChange = () => {
  loadData()
}

// 新增
const handleAdd = () => {
  dialogTitle.value = '新增词汇'
  resetForm()
  dialogVisible.value = true
}

// 编辑
const handleEdit = (row) => {
  dialogTitle.value = '编辑词汇'
  formData.id = row.id
  formData.category = row.category
  formData.specialty = row.specialty || ''
  formData.standard_name = row.standard_name
  formData.keywords = [...row.keywords]
  formData.description = row.description || ''
  dialogVisible.value = true
}

// 删除
const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除词汇"${row.standard_name}"吗？`,
      '提示',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    const res = await deleteVocabulary(row.id)
    if (res.success) {
      ElMessage.success('删除成功')
      loadData()
    }
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败: ' + error.message)
    }
  }
}

// 检查相似词
const handleCheckSimilar = async () => {
  if (!formData.standard_name || formData.id) {
    similarItems.value = []
    return
  }

  try {
    const res = await checkSimilarVocabulary({
      text: formData.standard_name,
      category: formData.category || undefined
    })

    if (res.success && res.data.has_similar) {
      similarItems.value = res.data.similar_items
    } else {
      similarItems.value = []
    }
  } catch (error) {
    console.error('检查相似词失败:', error)
  }
}

// 显示关键词输入框
const showKeywordInput = () => {
  keywordInputVisible.value = true
  nextTick(() => {
    keywordInputRef.value?.focus()
  })
}

// 添加关键词
const handleAddKeyword = () => {
  const value = keywordInputValue.value.trim()
  if (value && !formData.keywords.includes(value)) {
    formData.keywords.push(value)
  }
  keywordInputValue.value = ''
  keywordInputVisible.value = false
}

// 移除关键词
const handleRemoveKeyword = (index) => {
  formData.keywords.splice(index, 1)
}

// 提交表单
const handleSubmit = async () => {
  try {
    await formRef.value.validate()

    // 检查相似词
    if (similarItems.value.length > 0 && !formData.id) {
      await ElMessageBox.confirm(
        '存在相似词汇，确定要继续添加吗？',
        '提示',
        {
          confirmButtonText: '继续添加',
          cancelButtonText: '取消',
          type: 'warning'
        }
      )
    }

    submitting.value = true

    const data = {
      category: formData.category,
      specialty: formData.specialty || undefined,
      standard_name: formData.standard_name,
      keywords: formData.keywords,
      description: formData.description || undefined
    }

    let res
    if (formData.id) {
      res = await updateVocabulary(formData.id, data)
    } else {
      res = await createVocabulary(data)
    }

    if (res.success) {
      ElMessage.success(formData.id ? '更新成功' : '创建成功')
      dialogVisible.value = false
      loadData()
    }
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('操作失败: ' + error.message)
    }
  } finally {
    submitting.value = false
  }
}

// 重置表单
const resetForm = () => {
  formData.id = null
  formData.category = ''
  formData.specialty = ''
  formData.standard_name = ''
  formData.keywords = []
  formData.description = ''
  similarItems.value = []
  formRef.value?.clearValidate()
}

// 对话框关闭
const handleDialogClose = () => {
  resetForm()
}

// 初始化
onMounted(() => {
  loadData()
})
</script>

<style scoped>
.vocabulary-management {
  padding: 20px;
  background: #f5f7fa;
  min-height: 100vh;
}

.page-header {
  background: white;
  padding: 20px;
  margin-bottom: 20px;
  border-radius: 4px;
}

.page-title {
  font-size: 18px;
  font-weight: 600;
}

.filter-card {
  margin-bottom: 20px;
}

.filter-form {
  margin-bottom: 0;
}

.table-card {
  margin-bottom: 20px;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.text-muted {
  color: #909399;
}

.similar-warning {
  margin-top: 10px;
}

.similar-item {
  margin: 5px 0;
  font-size: 13px;
}

.keywords-input {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
}
</style>
