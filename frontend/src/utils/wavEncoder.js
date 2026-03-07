/**
 * WAV 音频编码器
 * 将 AudioBuffer 编码为 WAV 格式
 * 用于在浏览器中直接生成 WAV 文件，无需后端转换
 */

/**
 * 将 AudioBuffer 转换为 WAV Blob
 * @param {AudioBuffer} audioBuffer - Web Audio API 的 AudioBuffer
 * @param {number} sampleRate - 目标采样率（默认 16000）
 * @returns {Blob} WAV 格式的 Blob
 */
export function audioBufferToWav(audioBuffer, sampleRate = 16000) {
  // 获取音频数据（单声道）
  let audioData
  if (audioBuffer.numberOfChannels === 1) {
    audioData = audioBuffer.getChannelData(0)
  } else {
    // 多声道转单声道（取平均值）
    const left = audioBuffer.getChannelData(0)
    const right = audioBuffer.getChannelData(1)
    audioData = new Float32Array(left.length)
    for (let i = 0; i < left.length; i++) {
      audioData[i] = (left[i] + right[i]) / 2
    }
  }

  // 重采样到目标采样率
  if (audioBuffer.sampleRate !== sampleRate) {
    audioData = resample(audioData, audioBuffer.sampleRate, sampleRate)
  }

  // 转换为 16-bit PCM
  const pcmData = floatTo16BitPCM(audioData)

  // 创建 WAV 文件
  const wavBuffer = createWavFile(pcmData, sampleRate)

  return new Blob([wavBuffer], { type: 'audio/wav' })
}

/**
 * 重采样音频数据
 * @param {Float32Array} audioData - 原始音频数据
 * @param {number} fromSampleRate - 原始采样率
 * @param {number} toSampleRate - 目标采样率
 * @returns {Float32Array} 重采样后的音频数据
 */
function resample(audioData, fromSampleRate, toSampleRate) {
  const ratio = fromSampleRate / toSampleRate
  const newLength = Math.round(audioData.length / ratio)
  const result = new Float32Array(newLength)

  for (let i = 0; i < newLength; i++) {
    const srcIndex = i * ratio
    const srcIndexFloor = Math.floor(srcIndex)
    const srcIndexCeil = Math.min(srcIndexFloor + 1, audioData.length - 1)
    const t = srcIndex - srcIndexFloor

    // 线性插值
    result[i] = audioData[srcIndexFloor] * (1 - t) + audioData[srcIndexCeil] * t
  }

  return result
}

/**
 * 将 Float32Array 转换为 16-bit PCM
 * @param {Float32Array} floatData - 浮点音频数据（-1.0 到 1.0）
 * @returns {Int16Array} 16-bit PCM 数据
 */
function floatTo16BitPCM(floatData) {
  const pcmData = new Int16Array(floatData.length)
  for (let i = 0; i < floatData.length; i++) {
    // 限制在 -1.0 到 1.0 范围内
    const s = Math.max(-1, Math.min(1, floatData[i]))
    // 转换为 16-bit 整数
    pcmData[i] = s < 0 ? s * 0x8000 : s * 0x7FFF
  }
  return pcmData
}

/**
 * 创建 WAV 文件
 * @param {Int16Array} pcmData - PCM 音频数据
 * @param {number} sampleRate - 采样率
 * @returns {ArrayBuffer} WAV 文件的 ArrayBuffer
 */
function createWavFile(pcmData, sampleRate) {
  const numChannels = 1 // 单声道
  const bitsPerSample = 16
  const byteRate = sampleRate * numChannels * bitsPerSample / 8
  const blockAlign = numChannels * bitsPerSample / 8
  const dataSize = pcmData.length * 2 // 16-bit = 2 bytes per sample

  // WAV 文件头 + 数据
  const buffer = new ArrayBuffer(44 + dataSize)
  const view = new DataView(buffer)

  // RIFF chunk descriptor
  writeString(view, 0, 'RIFF')
  view.setUint32(4, 36 + dataSize, true) // 文件大小 - 8
  writeString(view, 8, 'WAVE')

  // fmt sub-chunk
  writeString(view, 12, 'fmt ')
  view.setUint32(16, 16, true) // fmt chunk size
  view.setUint16(20, 1, true) // audio format (1 = PCM)
  view.setUint16(22, numChannels, true) // number of channels
  view.setUint32(24, sampleRate, true) // sample rate
  view.setUint32(28, byteRate, true) // byte rate
  view.setUint16(32, blockAlign, true) // block align
  view.setUint16(34, bitsPerSample, true) // bits per sample

  // data sub-chunk
  writeString(view, 36, 'data')
  view.setUint32(40, dataSize, true) // data size

  // 写入 PCM 数据
  const offset = 44
  for (let i = 0; i < pcmData.length; i++) {
    view.setInt16(offset + i * 2, pcmData[i], true)
  }

  return buffer
}

/**
 * 在 DataView 中写入字符串
 * @param {DataView} view - DataView 对象
 * @param {number} offset - 偏移量
 * @param {string} string - 要写入的字符串
 */
function writeString(view, offset, string) {
  for (let i = 0; i < string.length; i++) {
    view.setUint8(offset + i, string.charCodeAt(i))
  }
}
