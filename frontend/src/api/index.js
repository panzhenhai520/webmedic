import http from './http'
import { ElMessage } from 'element-plus'

/**
 * API 接口定义
 */
export const api = {
  // 健康检查
  ping: () => http.get('/ping'),

  // 获取系统信息
  getInfo: () => http.get('/info'),

  // 获取数据库统计
  getDatabaseStats: () => http.get('/system/database/stats'),

  // 切换 ASR 引擎
  switchAsrEngine: (engine) => http.post(`/system/asr/switch?engine=${engine}`),

  // 切换 LLM 模型
  switchLlmModel: (model) => http.post(`/system/llm/switch?model=${model}`)
}

// 导出医生和患者相关API
export * from './doctor'
export * from './patient'

// 导出会话相关API
export * from './session'

// 导出基础数据API
export * from './masterData'

// 导出ASR相关API
export * from './asr'

// 导出结构化抽取API
export * from './extract'

// 导出病历文档API
export * from './documents'

// 导出相似病历API
export * from './similarCase'

// 导出病历草稿API
export * from './draft'

// 导出临床提示API
export * from './clinicalHints'

export default http
