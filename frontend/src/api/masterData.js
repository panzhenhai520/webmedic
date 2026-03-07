import http from './http'

/**
 * 基础数据相关 API
 */

/**
 * 获取默认医生（Doctor Panython）
 */
export const getDefaultDoctor = () => {
  return http.get('/master-data/doctor/default')
}

/**
 * 获取默认患者（张三）
 */
export const getDefaultPatient = () => {
  return http.get('/master-data/patient/default')
}
