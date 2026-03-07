import { defineStore } from 'pinia'
import { ref } from 'vue'

/**
 * 应用全局状态管理
 */
export const useAppStore = defineStore('app', () => {
  // 应用信息
  const appName = ref('WebMedic')
  const version = ref('0.1.0')
  const stage = ref('Stage 3 - Frontend Workbench')

  // 系统状态
  const loading = ref(false)
  const systemInfo = ref(null)

  /**
   * 设置加载状态
   */
  const setLoading = (status) => {
    loading.value = status
  }

  /**
   * 设置系统信息
   */
  const setSystemInfo = (info) => {
    systemInfo.value = info
  }

  return {
    appName,
    version,
    stage,
    loading,
    systemInfo,
    setLoading,
    setSystemInfo
  }
})
