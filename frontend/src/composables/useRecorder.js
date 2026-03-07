/**
 * 录音功能 Composable（智能模式）
 * 优先使用 WebM（高效），fallback 到 WAV（兼容）
 */

import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { audioBufferToWav } from '@/utils/wavEncoder'

export function useRecorder() {
  const isRecording = ref(false)
  const recordingMode = ref('webm') // 'webm' 或 'wav'

  // WebM 模式的变量
  const mediaRecorder = ref(null)
  const audioChunks = ref([])

  // WAV 模式的变量
  const audioContext = ref(null)
  const mediaStreamSource = ref(null)
  const scriptProcessor = ref(null)
  const wavAudioChunks = ref([])
  const stream = ref(null)

  /**
   * 开始录音（智能选择模式）
   */
  const startRecording = async () => {
    try {
      // 请求麦克风权限
      stream.value = await navigator.mediaDevices.getUserMedia({
        audio: {
          channelCount: 1,  // 单声道
          sampleRate: 16000  // 16kHz 采样率（适合语音识别）
        }
      })

      // 尝试使用 MediaRecorder（WebM 模式）
      if (typeof MediaRecorder !== 'undefined' && MediaRecorder.isTypeSupported('audio/webm')) {
        return await startWebMRecording()
      } else {
        // Fallback 到 WAV 模式
        console.warn('浏览器不支持 WebM，使用 WAV 模式')
        return await startWavRecording()
      }
    } catch (error) {
      console.error('开始录音失败:', error)
      ElMessage.error('无法访问麦克风，请检查权限设置')
      return false
    }
  }

  /**
   * WebM 模式录音（优先）
   */
  const startWebMRecording = async () => {
    try {
      recordingMode.value = 'webm'

      // 创建 MediaRecorder 实例
      mediaRecorder.value = new MediaRecorder(stream.value, {
        mimeType: 'audio/webm;codecs=opus'
      })

      // 清空之前的音频数据
      audioChunks.value = []

      // 监听数据可用事件
      mediaRecorder.value.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunks.value.push(event.data)
        }
      }

      // 开始录音
      mediaRecorder.value.start()
      isRecording.value = true

      console.log('开始录音（WebM 模式 - 高效）')
      return true
    } catch (error) {
      console.error('WebM 录音失败，切换到 WAV 模式:', error)
      return await startWavRecording()
    }
  }

  /**
   * WAV 模式录音（Fallback）
   */
  const startWavRecording = async () => {
    try {
      recordingMode.value = 'wav'

      // 创建 AudioContext
      audioContext.value = new (window.AudioContext || window.webkitAudioContext)({
        sampleRate: 16000
      })

      // 创建音频源
      mediaStreamSource.value = audioContext.value.createMediaStreamSource(stream.value)

      // 创建 ScriptProcessor 用于捕获音频数据
      const bufferSize = 4096
      scriptProcessor.value = audioContext.value.createScriptProcessor(bufferSize, 1, 1)

      // 清空之前的音频数据
      wavAudioChunks.value = []

      // 监听音频数据
      scriptProcessor.value.onaudioprocess = (event) => {
        if (isRecording.value) {
          const inputData = event.inputBuffer.getChannelData(0)
          // 复制数据（避免引用问题）
          const chunk = new Float32Array(inputData)
          wavAudioChunks.value.push(chunk)
        }
      }

      // 连接音频节点
      mediaStreamSource.value.connect(scriptProcessor.value)
      scriptProcessor.value.connect(audioContext.value.destination)

      isRecording.value = true
      console.log('开始录音（WAV 模式 - Fallback）')

      return true
    } catch (error) {
      console.error('WAV 录音失败:', error)
      throw error
    }
  }

  /**
   * 停止录音
   * @returns {Promise<{blob: Blob, format: string}>} 音频 Blob 和格式
   */
  const stopRecording = async () => {
    if (!isRecording.value) {
      throw new Error('录音未开始')
    }

    if (recordingMode.value === 'webm') {
      return await stopWebMRecording()
    } else {
      return await stopWavRecording()
    }
  }

  /**
   * 停止 WebM 录音
   */
  const stopWebMRecording = () => {
    return new Promise((resolve, reject) => {
      if (!mediaRecorder.value) {
        reject(new Error('MediaRecorder 未初始化'))
        return
      }

      // 监听停止事件
      mediaRecorder.value.onstop = () => {
        // 创建音频 Blob
        const audioBlob = new Blob(audioChunks.value, { type: 'audio/webm' })

        console.log(`录音完成（WebM），大小: ${audioBlob.size} 字节`)

        // 停止所有音频轨道
        if (stream.value) {
          stream.value.getTracks().forEach(track => track.stop())
          stream.value = null
        }

        isRecording.value = false
        resolve({ blob: audioBlob, format: 'webm' })
      }

      // 停止录音
      mediaRecorder.value.stop()
    })
  }

  /**
   * 停止 WAV 录音
   */
  const stopWavRecording = async () => {
    return new Promise((resolve, reject) => {
      try {
        isRecording.value = false

        // 断开音频节点
        if (scriptProcessor.value) {
          scriptProcessor.value.disconnect()
          scriptProcessor.value = null
        }
        if (mediaStreamSource.value) {
          mediaStreamSource.value.disconnect()
          mediaStreamSource.value = null
        }

        // 停止所有音频轨道
        if (stream.value) {
          stream.value.getTracks().forEach(track => track.stop())
          stream.value = null
        }

        // 合并所有音频块
        const totalLength = wavAudioChunks.value.reduce((acc, chunk) => acc + chunk.length, 0)
        const audioData = new Float32Array(totalLength)
        let offset = 0
        for (const chunk of wavAudioChunks.value) {
          audioData.set(chunk, offset)
          offset += chunk.length
        }

        console.log(`录音完成（WAV），采样点数: ${audioData.length}`)

        // 创建 AudioBuffer
        const audioBuffer = audioContext.value.createBuffer(
          1, // 单声道
          audioData.length,
          audioContext.value.sampleRate
        )
        audioBuffer.getChannelData(0).set(audioData)

        // 转换为 WAV Blob
        const wavBlob = audioBufferToWav(audioBuffer, 16000)

        console.log(`生成 WAV 文件，大小: ${wavBlob.size} 字节`)

        // 关闭 AudioContext
        if (audioContext.value) {
          audioContext.value.close()
          audioContext.value = null
        }

        resolve({ blob: wavBlob, format: 'wav' })
      } catch (error) {
        console.error('停止 WAV 录音失败:', error)
        reject(error)
      }
    })
  }

  /**
   * 取消录音
   */
  const cancelRecording = () => {
    if (!isRecording.value) return

    isRecording.value = false

    if (recordingMode.value === 'webm') {
      // 取消 WebM 录音
      if (mediaRecorder.value) {
        if (mediaRecorder.value.state !== 'inactive') {
          mediaRecorder.value.stop()
        }
        mediaRecorder.value = null
      }
    } else {
      // 取消 WAV 录音
      if (scriptProcessor.value) {
        scriptProcessor.value.disconnect()
        scriptProcessor.value = null
      }
      if (mediaStreamSource.value) {
        mediaStreamSource.value.disconnect()
        mediaStreamSource.value = null
      }
      if (audioContext.value) {
        audioContext.value.close()
        audioContext.value = null
      }
    }

    // 停止所有音频轨道
    if (stream.value) {
      stream.value.getTracks().forEach(track => track.stop())
      stream.value = null
    }

    audioChunks.value = []
    wavAudioChunks.value = []
  }

  return {
    isRecording,
    recordingMode,
    startRecording,
    stopRecording,
    cancelRecording
  }
}
