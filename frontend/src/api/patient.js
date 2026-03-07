import http from './http'

/**
 * 患者相关 API
 */

/**
 * 获取患者信息
 * @param {number} patientId - 患者ID
 */
export const getPatientInfo = (patientId) => {
  return http.get(`/patients/${patientId}`)
}

/**
 * 获取患者列表
 */
export const getPatientList = () => {
  return http.get('/patients')
}

/**
 * Mock: 获取固定患者信息（张三）
 * 阶段3使用 mock 数据，后续阶段接入真实API
 */
export const getMockPatientInfo = () => {
  return Promise.resolve({
    success: true,
    data: {
      id: 1,
      patient_name: '张三',
      gender: '男',
      age: 29,
      phone: '13800138000',
      birthday: '1995-01-01'
    },
    message: '获取成功'
  })
}
