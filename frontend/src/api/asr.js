/**
 * ASR API
 * 语音识别相关接口
 */

import http from './http'

/**
 * 转写音频
 * @param {FormData} formData - 包含 session_id, speaker_role, audio_file
 * @returns {Promise}
 */
export const transcribeAudio = (formData) => {
  return http.post('/asr/transcribe', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

/**
 * 获取会话的所有转写片段
 * @param {number} sessionId - 会话ID
 * @returns {Promise}
 */
export const getSessionSegments = (sessionId) => {
  return http.get(`/asr/segments/${sessionId}`)
}
