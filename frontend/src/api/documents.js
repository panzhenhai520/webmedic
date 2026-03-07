/**
 * Documents API
 * 病历文档管理接口
 */

import http from './http'

/**
 * 扫描本地病历目录
 * @param {string} directory - 目录路径
 * @returns {Promise}
 */
export function scanLocalDirectory(directory) {
  return http.post('/documents/scan-local', { directory })
}

/**
 * 获取文档列表
 * @returns {Promise}
 */
export function getDocumentList() {
  return http.get('/documents/list')
}
