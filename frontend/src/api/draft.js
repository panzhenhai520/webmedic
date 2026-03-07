/**
 * Draft API
 * 病历草稿接口
 */

import http from './http'

/**
 * 生成病历草稿
 * @param {number} sessionId - 会话ID
 * @returns {Promise}
 */
export function generateDraft(sessionId) {
  return http.post(`/draft/generate/${sessionId}`)
}

/**
 * 应用相似病历的检查治疗方案
 * @param {number} sessionId - 会话ID
 * @param {number} sourceDocumentId - 来源文档ID
 * @returns {Promise}
 */
export function applySimilarPlan(sessionId, sourceDocumentId) {
  return http.post(`/draft/apply-similar-plan/${sessionId}`, {
    source_document_id: sourceDocumentId
  })
}
