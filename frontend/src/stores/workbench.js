import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

/**
 * 工作站状态管理
 */
export const useWorkbenchStore = defineStore('workbench', () => {
  // 医生信息
  const doctorInfo = ref(null)

  // 患者信息
  const patientInfo = ref(null)

  // 会话信息
  const sessionInfo = ref(null)
  const sessionStatus = ref('idle') // idle, started, ended

  // 对话记录
  const dialogueList = ref([])

  // 结构化病历数据
  const structuredRecord = ref(null)

  // 病历草稿
  const draft = ref(null)

  // 相似病历列表
  const similarCases = ref([])

  // 临床提示列表
  const clinicalHints = ref([])

  // 追问建议列表
  const followupQuestions = ref([])

  // 当前激活的辅助标签页
  const activeAssistantTab = ref('questions')

  /**
   * 设置医生信息
   */
  const setDoctorInfo = (info) => {
    doctorInfo.value = info
  }

  /**
   * 设置患者信息
   */
  const setPatientInfo = (info) => {
    patientInfo.value = info
  }

  /**
   * 设置会话信息
   */
  const setSessionInfo = (info) => {
    sessionInfo.value = info
  }

  /**
   * 设置会话状态
   */
  const setSessionStatus = (status) => {
    sessionStatus.value = status
  }

  /**
   * 添加对话记录
   */
  const addDialogue = (dialogue) => {
    dialogueList.value.push(dialogue)
  }

  /**
   * 清空对话记录
   */
  const clearDialogues = () => {
    dialogueList.value = []
  }

  /**
   * 设置结构化病历
   */
  const setStructuredRecord = (record) => {
    structuredRecord.value = record
  }

  /**
   * 设置病历草稿
   */
  const setDraft = (draftData) => {
    draft.value = draftData
  }

  /**
   * 设置相似病历
   */
  const setSimilarCases = (cases) => {
    similarCases.value = cases
  }

  /**
   * 设置临床提示
   */
  const setClinicalHints = (hints) => {
    clinicalHints.value = hints
  }

  /**
   * 设置追问建议
   */
  const setFollowupQuestions = (questions) => {
    followupQuestions.value = questions
  }

  /**
   * 设置激活的辅助标签页
   */
  const setActiveAssistantTab = (tabName) => {
    console.log('Store: 设置激活标签页为', tabName)
    activeAssistantTab.value = tabName
  }

  /**
   * 重置工作站状态
   */
  const resetWorkbench = () => {
    sessionInfo.value = null
    sessionStatus.value = 'idle'
    dialogueList.value = []
    structuredRecord.value = null
    draft.value = null
    similarCases.value = []
    clinicalHints.value = []
    followupQuestions.value = []
  }

  // 计算属性：是否有会话
  const hasSession = computed(() => sessionInfo.value !== null)

  // 计算属性：会话是否进行中
  const isSessionActive = computed(() => sessionStatus.value === 'started')

  return {
    // 状态
    doctorInfo,
    patientInfo,
    sessionInfo,
    sessionStatus,
    dialogueList,
    structuredRecord,
    draft,
    similarCases,
    clinicalHints,
    followupQuestions,
    activeAssistantTab,

    // 方法
    setDoctorInfo,
    setPatientInfo,
    setSessionInfo,
    setSessionStatus,
    addDialogue,
    clearDialogues,
    setStructuredRecord,
    setDraft,
    setSimilarCases,
    setClinicalHints,
    setFollowupQuestions,
    setActiveAssistantTab,
    resetWorkbench,

    // 计算属性
    hasSession,
    isSessionActive
  }
})
