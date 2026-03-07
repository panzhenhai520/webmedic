import http from './http'

/**
 * 医生相关 API
 */

/**
 * 获取医生信息
 * @param {number} doctorId - 医生ID
 */
export const getDoctorInfo = (doctorId) => {
  return http.get(`/doctors/${doctorId}`)
}

/**
 * 获取医生列表
 */
export const getDoctorList = () => {
  return http.get('/doctors')
}

/**
 * Mock: 获取固定医生信息（Doctor Panython）
 * 阶段3使用 mock 数据，后续阶段接入真实API
 */
export const getMockDoctorInfo = () => {
  return Promise.resolve({
    success: true,
    data: {
      id: 1,
      doctor_name: 'Doctor Panython',
      title: '主治医师',
      department: '全科',
      avatar: null
    },
    message: '获取成功'
  })
}
