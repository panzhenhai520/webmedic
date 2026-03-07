<template>
  <el-card class="control-panel" shadow="hover">
    <template #header>
      <div class="card-header">
        <span class="header-title">
          <el-icon><Setting /></el-icon>
          问诊控制
        </span>
        <el-tag :type="sessionStatusType" size="small">
          {{ sessionStatusText }}
        </el-tag>
      </div>
    </template>

    <div class="control-content">
      <!-- 会话控制 -->
      <div class="control-section">
        <div class="section-title">会话管理</div>
        <div class="button-group">
          <el-button
            type="primary"
            :icon="VideoPlay"
            :disabled="isSessionActive"
            @click="handleStartSession"
            class="control-button"
          >
            开始问诊
          </el-button>
          <el-button
            type="danger"
            :icon="VideoPause"
            :disabled="!isSessionActive"
            @click="handleEndSession"
            class="control-button"
          >
            结束问诊
          </el-button>
        </div>
      </div>

      <el-divider />

      <!-- 录音控制 -->
      <div class="control-section">
        <div class="section-title">
          <span>语音采集</span>
          <el-switch
            v-model="useRealRecording"
            active-text="录音"
            inactive-text="模拟"
            style="margin-left: 10px"
            @change="handleRecordingModeChange"
          />
        </div>
        <div class="button-group">
          <el-button
            type="success"
            :icon="Microphone"
            :disabled="!isSessionActive || (isRecording && currentSpeakerRole !== 'doctor')"
            @click="handleDoctorSpeak"
            class="control-button"
          >
            {{ isRecording && currentSpeakerRole === 'doctor' ? '停止录音' : '医生说话' }}
          </el-button>
          <el-button
            type="warning"
            :icon="Microphone"
            :disabled="!isSessionActive || (isRecording && currentSpeakerRole !== 'patient')"
            @click="handlePatientSpeak"
            class="control-button"
          >
            {{ isRecording && currentSpeakerRole === 'patient' ? '停止录音' : '患者说话' }}
          </el-button>
        </div>
        <div v-if="isRecording" class="recording-indicator">
          <el-icon class="is-loading"><Loading /></el-icon>
          <span>录音中... 点击按钮停止</span>
        </div>
        <div v-if="useRealRecording && systemInfo" class="asr-engine-info">
          <el-select
            v-model="currentAsrEngine"
            size="small"
            @change="handleSwitchAsrEngine"
            style="width: 100%"
          >
            <el-option label="🎤 Whisper 引擎" value="whisper" />
            <el-option label="🎤 Dolphin 引擎" value="dolphin" />
            <el-option label="🔧 Mock 模式" value="mock" />
          </el-select>
        </div>
      </div>

      <el-divider />

      <!-- 数据处理 -->
      <div class="control-section">
        <div class="section-title">数据处理</div>
        <!-- 抽取器选择 -->
        <div class="extractor-selector" style="margin-bottom: 10px;">
          <el-select
            v-model="selectedExtractor"
            size="small"
            placeholder="选择抽取器"
            style="width: 100%"
          >
            <el-option label="📝 Instructor" value="instructor" />
            <el-option label="🔍 LangExtract" value="langextract" />
          </el-select>
        </div>
        <div class="button-group vertical">
          <el-button
            :icon="DocumentCopy"
            :disabled="!hasDialogues || isExtracting"
            :loading="isExtracting"
            @click="handleExtract"
            class="control-button"
          >
            {{ isExtracting ? '抽取中...' : '重新抽取' }}
          </el-button>
          <el-button
            :icon="Search"
            :disabled="!hasDialogues"
            @click="handleSearchSimilar"
            class="control-button"
          >
            检索相似病历
          </el-button>
          <el-button
            :icon="Document"
            :disabled="!hasDialogues"
            @click="handleGenerateDraft"
            class="control-button"
          >
            生成病历草稿
          </el-button>
          <el-button
            :icon="Warning"
            :disabled="!hasDialogues"
            @click="handleGenerateHints"
            class="control-button"
          >
            生成临床提示
          </el-button>
        </div>
        <!-- LLM 模式显示 -->
        <div v-if="llmInfo" class="llm-info">
          <el-select
            v-model="currentLlmModel"
            size="small"
            @change="handleSwitchLlmModel"
            style="width: 100%"
          >
            <el-option label="🤖 deepseek-chat" value="deepseek-chat" />
            <el-option label="🧠 deepseek-reasoner" value="deepseek-reasoner" />
          </el-select>
        </div>
      </div>
    </div>
  </el-card>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import {
  VideoPlay,
  VideoPause,
  Microphone,
  DocumentCopy,
  Search,
  Document,
  Warning,
  Loading,
  InfoFilled
} from '@element-plus/icons-vue'
import { useWorkbenchStore } from '@/stores/workbench'
import { createSession, finishSession, transcribeAudio, extractStructuredRecord, searchSimilarCases, generateDraft, generateClinicalHints, api } from '@/api'
import { useRecorder } from '@/composables/useRecorder'

const workbenchStore = useWorkbenchStore()

// 录音功能
const { isRecording, startRecording, stopRecording } = useRecorder()

// 当前录音角色
const currentSpeakerRole = ref(null)

// 录音模式：true=真实录音，false=模拟对话
const useRealRecording = ref(false)

// 抽取状态
const isExtracting = ref(false)

// LLM 信息
const llmInfo = ref(null)

// 系统信息
const systemInfo = ref(null)

// 当前 ASR 引擎
const currentAsrEngine = ref('whisper')

// 当前 LLM 模型
const currentLlmModel = ref('deepseek-chat')
// 当前抽取器
const selectedExtractor = ref('instructor')

// 自动处理的防抖定时器
let autoProcessTimer = null

// 计算属性
const isSessionActive = computed(() => workbenchStore.isSessionActive)
const hasDialogues = computed(() => workbenchStore.dialogueList.length > 0)

const sessionStatusType = computed(() => {
  switch (workbenchStore.sessionStatus) {
    case 'started':
      return 'success'
    case 'ended':
      return 'info'
    default:
      return 'info'
  }
})

const sessionStatusText = computed(() => {
  switch (workbenchStore.sessionStatus) {
    case 'started':
      return '进行中'
    case 'ended':
      return '已结束'
    default:
      return '未开始'
  }
})

// 开始问诊
const handleStartSession = async () => {
  try {
    // 检查医生和患者信息是否已加载
    if (!workbenchStore.doctorInfo || !workbenchStore.patientInfo) {
      ElMessage.error('医生或患者信息未加载')
      return
    }

    // 调用API创建会话
    const response = await createSession({
      doctor_id: workbenchStore.doctorInfo.id,
      patient_id: workbenchStore.patientInfo.id
    })

    // 更新store状态
    workbenchStore.setSessionInfo(response.data)
    workbenchStore.setSessionStatus('started')

    ElMessage.success(`问诊已开始 - 会话编号: ${response.data.session_no}`)
  } catch (error) {
    console.error('创建会话失败:', error)
    ElMessage.error('创建会话失败，请重试')
  }
}

// 结束问诊
const handleEndSession = async () => {
  try {
    // 检查会话信息是否存在
    if (!workbenchStore.sessionInfo || !workbenchStore.sessionInfo.id) {
      ElMessage.error('会话信息不存在')
      return
    }

    // 调用API结束会话
    await finishSession(workbenchStore.sessionInfo.id)

    // 更新store状态
    workbenchStore.setSessionStatus('ended')

    ElMessage.info('问诊已结束')
  } catch (error) {
    console.error('结束会话失败:', error)
    ElMessage.error('结束会话失败，请重试')
  }
}

// 录音模式切换
const handleRecordingModeChange = (value) => {
  if (value) {
    ElMessage.info('已切换到录音模式')
  } else {
    ElMessage.info('已切换到模拟模式')
  }
}

// 医生说话
const handleDoctorSpeak = async () => {
  if (useRealRecording.value) {
    // 真实录音模式
    if (isRecording.value) {
      // 停止录音
      await handleStopRecording()
    } else {
      // 开始录音
      currentSpeakerRole.value = 'doctor'
      const success = await startRecording()
      if (success) {
        ElMessage.success('医生录音中...')
      }
    }
  } else {
    // 模拟对话模式
    await handleMockSpeak('doctor')
  }
}

// 患者说话
const handlePatientSpeak = async () => {
  if (useRealRecording.value) {
    // 真实录音模式
    if (isRecording.value) {
      // 停止录音
      await handleStopRecording()
    } else {
      // 开始录音
      currentSpeakerRole.value = 'patient'
      const success = await startRecording()
      if (success) {
        ElMessage.success('患者录音中...')
      }
    }
  } else {
    // 模拟对话模式
    await handleMockSpeak('patient')
  }
}

// 模拟对话
const handleMockSpeak = async (role) => {
  try {
    // 创建一个空的音频 Blob（模拟）
    const emptyBlob = new Blob([], { type: 'audio/webm' })

    // 创建 FormData
    const formData = new FormData()
    formData.append('session_id', workbenchStore.sessionInfo.id)
    formData.append('speaker_role', role)
    formData.append('audio_file', emptyBlob, 'mock.webm')

    // 调用转写接口（后端会返回 Mock 文本）
    const response = await transcribeAudio(formData)

    // 添加对话到列表
    workbenchStore.addDialogue({
      speaker: role,
      text: response.data.transcript_text,
      timestamp: new Date().toISOString()
    })

    ElMessage.success('对话添加成功')

    // 自动触发抽取和生成追问建议（后台异步执行，不阻塞用户操作）
    autoProcessDialogue()
  } catch (error) {
    console.error('模拟对话失败:', error)
    ElMessage.error('模拟对话失败，请重试')
  }
}

// 停止录音并上传
const handleStopRecording = async () => {
  try {
    // 停止录音获取音频数据
    const result = await stopRecording()
    const audioBlob = result.blob
    const format = result.format

    // 根据格式设置文件名
    const filename = format === 'webm' ? 'recording.webm' : 'recording.wav'
    console.log(`上传音频文件: ${filename}, 大小: ${audioBlob.size} 字节`)

    // 创建 FormData
    const formData = new FormData()
    formData.append('session_id', workbenchStore.sessionInfo.id)
    formData.append('speaker_role', currentSpeakerRole.value)
    formData.append('audio_file', audioBlob, filename)

    // 上传并转写
    const response = await transcribeAudio(formData)

    // 添加对话到列表
    workbenchStore.addDialogue({
      speaker: currentSpeakerRole.value,
      text: response.data.transcript_text,
      timestamp: new Date().toISOString()
    })

    ElMessage.success('转写成功')

    // 自动触发抽取和生成追问建议（后台异步执行，不阻塞用户操作）
    autoProcessDialogue()
  } catch (error) {
    console.error('录音上传失败:', error)
    ElMessage.error('录音上传失败，请重试')
  } finally {
    currentSpeakerRole.value = null
  }
}

// 重新抽取
const handleExtract = async () => {
  try {
    // 检查会话信息是否存在
    if (!workbenchStore.sessionInfo || !workbenchStore.sessionInfo.id) {
      ElMessage.error('会话信息不存在')
      return
    }

    // 检查是否有对话记录
    if (workbenchStore.dialogueList.length === 0) {
      ElMessage.warning('请先进行问诊对话')
      return
    }

    isExtracting.value = true
    ElMessage.info('正在抽取结构化病历...')

    // 调用抽取接口
    const response = await extractStructuredRecord(workbenchStore.sessionInfo.id, selectedExtractor.value)

    // 更新 store 中的结构化病历数据
    workbenchStore.setStructuredRecord(response.data.structured_record)

    // 自动切换到结构化病历标签页
    console.log('切换到结构化病历标签页')
    workbenchStore.setActiveAssistantTab('structured')

    ElMessage.success('结构化抽取成功')
  } catch (error) {
    console.error('结构化抽取失败:', error)
    ElMessage.error('结构化抽取失败，请重试')
  } finally {
    isExtracting.value = false
  }
}

// 获取系统信息（包含 LLM 和 ASR 信息）
const fetchSystemInfo = async () => {
  try {
    const response = await api.getInfo()
    systemInfo.value = response.data
    llmInfo.value = {
      mode: response.data.llm_mode,
      model: response.data.llm_model
    }
    // 设置当前 LLM 模型
    if (response.data.llm_model && response.data.llm_model !== 'Mock') {
      currentLlmModel.value = response.data.llm_model
    }
    // 设置当前 ASR 引擎
    if (response.data.asr_mode === 'Mock') {
      currentAsrEngine.value = 'mock'
    } else if (response.data.asr_engine) {
      currentAsrEngine.value = response.data.asr_engine.toLowerCase()
    } else {
      currentAsrEngine.value = 'dolphin' // 默认值
    }
  } catch (error) {
    console.error('获取系统信息失败:', error)
  }
}

// 切换 ASR 引擎
const handleSwitchAsrEngine = async (engine) => {
  try {
    const response = await api.switchAsrEngine(engine)
    ElMessage.success(response.message)
    // 刷新系统信息
    await fetchSystemInfo()
  } catch (error) {
    console.error('切换 ASR 引擎失败:', error)
    ElMessage.error('切换 ASR 引擎失败，请重试')
    // 恢复原值
    await fetchSystemInfo()
  }
}

// 切换 LLM 模型
const handleSwitchLlmModel = async (model) => {
  try {
    const response = await api.switchLlmModel(model)
    ElMessage.success(response.message)
    // 刷新系统信息
    await fetchSystemInfo()
  } catch (error) {
    console.error('切换 LLM 模型失败:', error)
    ElMessage.error('切换 LLM 模型失败，请重试')
    // 恢复原值
    await fetchSystemInfo()
  }
}

// 自动处理对话：抽取结构化信息并生成追问建议
const autoProcessDialogue = async () => {
  // 清除之前的定时器
  if (autoProcessTimer) {
    clearTimeout(autoProcessTimer)
  }

  // 设置防抖：2秒后执行，避免频繁调用
  autoProcessTimer = setTimeout(async () => {
    try {
      // 1. 自动抽取结构化信息
      console.log('自动抽取结构化信息...')
      const extractResponse = await extractStructuredRecord(workbenchStore.sessionInfo.id, selectedExtractor.value)
      workbenchStore.setStructuredRecord(extractResponse.data.structured_record)

      // 2. 自动生成追问建议
      console.log('自动生成追问建议...')
      const hintsResponse = await generateClinicalHints(workbenchStore.sessionInfo.id)
      workbenchStore.setClinicalHints(hintsResponse.data.warnings)
      workbenchStore.setFollowupQuestions(hintsResponse.data.followup_questions)

      // 3. 自动切换到追问建议标签页
      workbenchStore.setActiveAssistantTab('questions')

      console.log('自动处理完成')
    } catch (error) {
      console.error('自动处理失败:', error)
      // 静默失败，不打断用户操作
    }
  }, 2000)
}

// 组件挂载时获取系统信息
onMounted(() => {
  fetchSystemInfo()
})

// 检索相似病历
const handleSearchSimilar = async () => {
  try {
    // 检查会话信息是否存在
    if (!workbenchStore.sessionInfo || !workbenchStore.sessionInfo.id) {
      ElMessage.error('会话信息不存在')
      return
    }

    // 检查是否有结构化记录
    if (!workbenchStore.structuredRecord) {
      ElMessage.warning('请先执行结构化抽取')
      return
    }

    ElMessage.info('正在检索相似病历...')

    // 调用检索接口
    const response = await searchSimilarCases(workbenchStore.sessionInfo.id, 3)

    // 更新 store 中的相似病历数据
    workbenchStore.setSimilarCases(response.data.matches)

    // 自动切换到相似病历标签页
    console.log('切换到相似病历标签页')
    workbenchStore.setActiveAssistantTab('similar')

    ElMessage.success(`检索完成，找到 ${response.data.total_count} 条相似病历`)
  } catch (error) {
    console.error('检索相似病历失败:', error)
    ElMessage.error(error.response?.data?.message || '检索相似病历失败，请重试')
  }
}

// 生成病历草稿
const handleGenerateDraft = async () => {
  try {
    // 检查会话信息是否存在
    if (!workbenchStore.sessionInfo || !workbenchStore.sessionInfo.id) {
      ElMessage.error('会话信息不存在')
      return
    }

    // 检查是否有结构化记录
    if (!workbenchStore.structuredRecord) {
      ElMessage.warning('请先执行结构化抽取')
      return
    }

    ElMessage.info('正在生成病历草稿...')

    // 调用生成接口
    const response = await generateDraft(workbenchStore.sessionInfo.id)

    // 更新 store 中的草稿数据
    workbenchStore.setDraft(response.data.content)

    // 自动切换到病历草稿标签页
    console.log('切换到病历草稿标签页')
    workbenchStore.setActiveAssistantTab('draft')

    ElMessage.success('病历草稿生成成功')
  } catch (error) {
    console.error('生成病历草稿失败:', error)
    ElMessage.error(error.response?.data?.message || '生成病历草稿失败，请重试')
  }
}

// 生成提示
const handleGenerateHints = async () => {
  try {
    // 检查会话信息是否存在
    if (!workbenchStore.sessionInfo || !workbenchStore.sessionInfo.id) {
      ElMessage.error('会话信息不存在')
      return
    }

    // 检查是否有结构化记录
    if (!workbenchStore.structuredRecord) {
      ElMessage.warning('请先执行结构化抽取')
      return
    }

    ElMessage.info('正在生成临床提示...')

    // 调用生成接口
    const response = await generateClinicalHints(workbenchStore.sessionInfo.id)

    // 更新 store 中的提示数据
    workbenchStore.setClinicalHints(response.data.warnings)
    workbenchStore.setFollowupQuestions(response.data.followup_questions)

    // 自动切换到风险提示标签页
    console.log('切换到风险提示标签页')
    workbenchStore.setActiveAssistantTab('warnings')

    ElMessage.success('临床提示生成成功')
  } catch (error) {
    console.error('生成临床提示失败:', error)
    ElMessage.error(error.response?.data?.message || '生成临床提示失败，请重试')
  }
}
</script>

<style scoped>
.control-panel {
  height: 100%;
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

.control-content {
  padding: 5px 0;
}

.control-section {
  margin-bottom: 8px;
}

.section-title {
  font-size: 13px;
  font-weight: 600;
  color: #606266;
  margin-bottom: 10px;
  padding-left: 8px;
  border-left: 3px solid #67c23a;
}

.button-group {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.button-group.vertical {
  flex-direction: column;
  gap: 8px;
}

.control-button {
  flex: 1;
  min-width: 120px;
}

.button-group.vertical .control-button {
  width: 100%;
}

.recording-indicator {
  margin-top: 10px;
  padding: 8px;
  background: #f0f9ff;
  border: 1px solid #409eff;
  border-radius: 4px;
  display: flex;
  align-items: center;
  gap: 8px;
  color: #409eff;
  font-size: 13px;
  font-weight: 500;
}

.mock-mode-tip {
  margin-top: 10px;
  padding: 8px;
  background: #fef0f0;
  border: 1px solid #f56c6c;
  border-radius: 4px;
  display: flex;
  align-items: center;
  gap: 8px;
  color: #f56c6c;
  font-size: 12px;
}

.section-title {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.asr-engine-info {
  margin-top: 10px;
  text-align: center;
}

.el-divider {
  margin: 12px 0;
}

.llm-info {
  margin-top: 12px;
  padding: 8px;
  background: #f5f7fa;
  border-radius: 4px;
  text-align: center;
}
</style>
