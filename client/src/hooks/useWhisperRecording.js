import { useCallback, useRef, useState } from 'react'
import { transcribeAudio } from '../services/api'

const isSupported =
  typeof navigator !== 'undefined' && Boolean(navigator.mediaDevices?.getUserMedia)

/**
 * Records mic audio in the browser, then sends it to the backend's local
 * Whisper model for transcription (instead of the browser's built-in,
 * far less accurate-for-Arabic speech recognition).
 */
export default function useWhisperRecording({ onResult, language }) {
  const [isRecording, setIsRecording] = useState(false)
  const [isTranscribing, setIsTranscribing] = useState(false)
  const [error, setError] = useState(null)
  const recorderRef = useRef(null)
  const chunksRef = useRef([])

  const startRecording = useCallback(async () => {
    setError(null)
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      const recorder = new MediaRecorder(stream)
      chunksRef.current = []

      recorder.ondataavailable = (e) => {
        if (e.data.size > 0) chunksRef.current.push(e.data)
      }

      recorder.onstop = async () => {
        stream.getTracks().forEach((track) => track.stop())
        const blob = new Blob(chunksRef.current, { type: 'audio/webm' })
        setIsTranscribing(true)
        try {
          const { text } = await transcribeAudio({ blob, language })
          if (text) onResult(text)
        } catch (err) {
          setError(
            err?.response?.data?.detail || 'Could not transcribe that recording.',
          )
        } finally {
          setIsTranscribing(false)
        }
      }

      recorderRef.current = recorder
      recorder.start()
      setIsRecording(true)
    } catch {
      setError('Microphone access was denied or is unavailable.')
    }
  }, [onResult, language])

  const stopRecording = useCallback(() => {
    recorderRef.current?.stop()
    setIsRecording(false)
  }, [])

  const toggleRecording = useCallback(() => {
    if (isRecording) {
      stopRecording()
    } else {
      startRecording()
    }
  }, [isRecording, startRecording, stopRecording])

  return {
    isSupported,
    isRecording,
    isTranscribing,
    error,
    toggleRecording,
  }
}
