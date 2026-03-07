/**
 * Extract API
 * 结构化抽取相关接口
 */

import http from './http'

/**
 * 抽取结构化病历
 * @param {number} sessionId - 会话ID
 * @returns {Promise}
 */
export const extractStructuredRecord = (sessionId) => {
  return http.post(`/extract/${sessionId}`)
}

/**
 * 获取结构化病历
 * @param {number} sessionId - 会话ID
 * @returns {Promise}
 */
export const getStructuredRecord = (sessionId) => {
  return http.get(`/extract/${sessionId}`)
}
