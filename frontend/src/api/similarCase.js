/**
 * Similar Case API
 * 相似病历检索接口
 */

import http from './http'

/**
 * 重建索引
 * @returns {Promise}
 */
export function rebuildIndex() {
  return http.post('/index/rebuild')
}

/**
 * 检索相似病历
 * @param {number} sessionId - 会话ID
 * @param {number} topK - 返回结果数量
 * @returns {Promise}
 */
export function searchSimilarCases(sessionId, topK = 3) {
  return http.post(`/index/search-similar/${sessionId}`, null, {
    params: { top_k: topK }
  })
}

/**
 * 获取相似病历结果
 * @param {number} sessionId - 会话ID
 * @returns {Promise}
 */
export function getSimilarCases(sessionId) {
  return http.get(`/index/similar-cases/${sessionId}`)
}
