import http from './http'

/**
 * 会话相关 API
 */

/**
 * 创建问诊会话
 * @param {Object} data - 创建会话参数
 * @param {number} data.doctor_id - 医生ID
 * @param {number} data.patient_id - 患者ID
 */
export const createSession = (data) => {
  return http.post('/sessions/create', data)
}

/**
 * 结束问诊会话
 * @param {number} sessionId - 会话ID
 */
export const finishSession = (sessionId) => {
  return http.post(`/sessions/${sessionId}/finish`)
}

/**
 * 获取会话详情
 * @param {number} sessionId - 会话ID
 */
export const getSession = (sessionId) => {
  return http.get(`/sessions/${sessionId}`)
}

/**
 * 获取会话列表
 * @param {Object} params - 查询参数
 * @param {number} params.page - 页码
 * @param {number} params.page_size - 每页数量
 * @param {string} params.status - 状态过滤
 */
export const getSessionList = (params) => {
  return http.get('/sessions/list', { params })
}

/**
 * 获取会话详情（含转写记录）
 * @param {number} sessionId - 会话ID
 */
export const getSessionWithTranscripts = (sessionId) => {
  return http.get(`/sessions/${sessionId}/transcripts`)
}
