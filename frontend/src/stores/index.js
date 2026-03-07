import { defineStore } from 'pinia'
import { ref } from 'vue'

/**
 * 全局状态管理
 * 后续阶段将添加更多状态
 */
export const useAppStore = defineStore('app', () => {
  // 应用信息
  const appName = ref('WebMedic')
  const version = ref('0.1.0')
  const stage = ref('Stage 3 - Frontend Workbench')

  return {
    appName,
    version,
    stage
  }
})

// 导出所有 store
export * from './app'
export * from './workbench'
