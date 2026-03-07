/**
 * Clinical Hints API
 * 临床提示接口
 */

import http from './http'

/**
 * 生成临床提示
 * @param {number} sessionId - 会话ID
 * @returns {Promise}
 */
export function generateClinicalHints(sessionId) {
  return http.post(`/clinical-hints/generate/${sessionId}`)
}
