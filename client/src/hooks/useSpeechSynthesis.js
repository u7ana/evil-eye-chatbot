import { useCallback, useEffect, useRef, useState } from 'react'
import { isArabicText } from '../utils/detectLanguage'
import { speakArabic } from '../services/api'

const synth = typeof window !== 'undefined' ? window.speechSynthesis : null

/**
 * Speaks English via the browser's built-in voices (free, instant), and
 * Arabic via the backend's edge-tts endpoint (free, no API key, and a real
 * male Egyptian-Arabic neural voice - Windows only ships Hoda, female).
 */
export default function useSpeechSynthesis() {
  const [voices, setVoices] = useState([])
  const [speakingId, setSpeakingId] = useState(null)
  const audioRef = useRef(null)

  useEffect(() => {
    if (!synth) return

    const loadVoices = () => {
      const available = synth.getVoices()
      if (available.length) setVoices(available)
    }

    loadVoices()
    synth.addEventListener('voiceschanged', loadVoices)
    return () => synth.removeEventListener('voiceschanged', loadVoices)
  }, [])

  const stop = useCallback(() => {
    if (synth) synth.cancel()
    if (audioRef.current) {
      audioRef.current.pause()
      audioRef.current.src = ''
      audioRef.current = null
    }
    setSpeakingId(null)
  }, [])

  const speak = useCallback(
    async (id, text, { voiceURI, rate = 1, pitch = 1, volume = 0.8 } = {}) => {
      if (!text) return

      if (speakingId === id) {
        stop()
        return
      }

      stop()

      if (isArabicText(text)) {
        setSpeakingId(id)
        try {
          const blob = await speakArabic({ text })
          const url = URL.createObjectURL(blob)
          const audio = new Audio(url)
          audio.volume = volume
          audio.playbackRate = rate
          audio.onended = () => {
            setSpeakingId((current) => (current === id ? null : current))
            URL.revokeObjectURL(url)
          }
          audio.onerror = () => setSpeakingId((current) => (current === id ? null : current))
          audioRef.current = audio
          audio.play()
        } catch {
          setSpeakingId((current) => (current === id ? null : current))
        }
        return
      }

      if (!synth) return

      const utterance = new SpeechSynthesisUtterance(text)
      const voice = voices.find((v) => v.voiceURI === voiceURI)
      if (voice) {
        utterance.voice = voice
        utterance.lang = voice.lang
      }
      utterance.rate = rate
      utterance.pitch = pitch
      utterance.volume = volume
      utterance.onend = () => setSpeakingId((current) => (current === id ? null : current))
      utterance.onerror = () => setSpeakingId((current) => (current === id ? null : current))

      synth.speak(utterance)
      setSpeakingId(id)
    },
    [voices, speakingId, stop],
  )

  return {
    isSupported: Boolean(synth),
    voices,
    speakingId,
    speak,
    stop,
  }
}
