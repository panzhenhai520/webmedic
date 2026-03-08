/**
 * 词库管理 API
 */
import http from './http'

// ============ 医学词汇 ============

/**
 * 获取医学词汇列表
 * @param {Object} params - 查询参数
 * @param {number} params.page - 页码
 * @param {number} params.page_size - 每页数量
 * @param {string} params.category - 分类筛选
 * @param {string} params.specialty - 专科筛选
 * @param {string} params.keyword - 关键词搜索
 * @param {string} params.status - 状态筛选
 */
export const getVocabularyList = (params) => {
  return http.post('/vocabulary/vocabulary/list', params)
}

/**
 * 获取单个医学词汇
 * @param {number} id - 词汇ID
 */
export const getVocabulary = (id) => {
  return http.get(`/vocabulary/vocabulary/${id}`)
}

/**
 * 检查相似词汇
 * @param {Object} params - 检查参数
 * @param {string} params.text - 待检查文本
 * @param {string} params.category - 限定分类
 */
export const checkSimilarVocabulary = (params) => {
  return http.post('/vocabulary/vocabulary/check-similar', params)
}

/**
 * 创建医学词汇
 * @param {Object} data - 词汇数据
 */
export const createVocabulary = (data) => {
  return http.post('/vocabulary/vocabulary', data)
}

/**
 * 更新医学词汇
 * @param {number} id - 词汇ID
 * @param {Object} data - 更新数据
 */
export const updateVocabulary = (id, data) => {
  return http.put(`/vocabulary/vocabulary/${id}`, data)
}

/**
 * 删除医学词汇
 * @param {number} id - 词汇ID
 */
export const deleteVocabulary = (id) => {
  return http.delete(`/vocabulary/vocabulary/${id}`)
}

// ============ ICD编码 ============
// TODO: 后续实现

// ============ 手术编码 ============
// TODO: 后续实现
