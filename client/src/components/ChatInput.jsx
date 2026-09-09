import { useCallback, useRef, useState } from 'react'
import { FiPlus, FiMic, FiArrowUp } from 'react-icons/fi'
import { HiOutlineSpeakerWave } from 'react-icons/hi2'
import useWhisperRecording from '../hooks/useWhisperRecording'

const MIC_LANGUAGES = [
  { code: 'en', label: 'EN', name: 'English' },
  { code: 'ar', label: 'ع', name: 'Arabic' },
]

export default function ChatInput({ onSend, disabled, voiceReplyEnabled, onToggleVoiceReply }) {
  const [value, setValue] = useState('')
  const [micLangIndex, setMicLangIndex] = useState(0)
  const textareaRef = useRef(null)
  const micLang = MIC_LANGUAGES[micLangIndex]

  const handleSpeechResult = useCallback((transcript) => {
    setValue((prev) => (prev ? `${prev} ${transcript}` : transcript))
  }, [])

  const { isRecording, isTranscribing, isSupported, error: micError, toggleRecording } = useWhisperRecording({
    onResult: handleSpeechResult,
    language: micLang.code,
  })

  const submit = () => {
    if (!value.trim() || disabled) return
    onSend(value)
    setValue('')
    if (textareaRef.current) textareaRef.current.style.height = 'auto'
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      submit()
    }
  }

  const handleChange = (e) => {
    setValue(e.target.value)
    const el = textareaRef.current
    if (el) {
      el.style.height = 'auto'
      el.style.height = `${Math.min(el.scrollHeight, 160)}px`
    }
  }

  return (
    <div className="px-6 pb-5 pt-2">
      <div className="max-w-3xl mx-auto">
        <div className="flex items-end gap-2 rounded-[28px] border-2 border-pine/25 bg-card px-3 py-2 focus-within:border-moss transition-colors shadow-[0_10px_30px_rgba(30,81,40,0.12)]">
          <button
            className="w-9 h-9 shrink-0 rounded-full flex items-center justify-center text-dim hover:bg-sage/20 hover:text-body transition-colors"
            aria-label="Attach a file"
          >
            <FiPlus size={18} />
          </button>

          <div className="relative shrink-0">
            <button
              onClick={toggleRecording}
              disabled={!isSupported || isTranscribing}
              className={`w-9 h-9 rounded-full flex items-center justify-center transition-colors ${
                isRecording
                  ? 'bg-red-600 text-white animate-pulse'
                  : 'text-dim hover:bg-sage/20 hover:text-body'
              } ${!isSupported || isTranscribing ? 'opacity-30 cursor-not-allowed' : ''}`}
              aria-label={
                isRecording
                  ? 'Stop recording'
                  : isTranscribing
                    ? 'Transcribing…'
                    : `Speak your message in ${micLang.name}`
              }
              title={
                isSupported
                  ? isTranscribing
                    ? 'Transcribing…'
                    : `Speak your message in ${micLang.name}`
                  : 'Microphone recording is not supported in this browser'
              }
            >
              <FiMic size={17} />
            </button>
            {isSupported && (
              <button
                onClick={() => setMicLangIndex((i) => (i + 1) % MIC_LANGUAGES.length)}
                disabled={isRecording || isTranscribing}
                className="absolute -bottom-1 -right-1 w-4 h-4 rounded-full bg-pine text-cream text-[8px] font-bold flex items-center justify-center leading-none disabled:opacity-40"
                aria-label={`Microphone language: ${micLang.name}. Click to switch.`}
                title={`Microphone language: ${micLang.name}`}
              >
                {micLang.label}
              </button>
            )}
          </div>

          <textarea
            ref={textareaRef}
            rows={1}
            dir="auto"
            value={value}
            onChange={handleChange}
            onKeyDown={handleKeyDown}
            placeholder="اكتب رسالتك لـ EE…"
            className="flex-1 resize-none bg-transparent outline-none text-[15px] text-body placeholder:text-dim py-1.5 max-h-40"
          />

          <button
            onClick={onToggleVoiceReply}
            className={`w-9 h-9 shrink-0 rounded-full flex items-center justify-center transition-colors ${
              voiceReplyEnabled
                ? 'bg-sage/25 text-pine dark:text-sage'
                : 'text-dim hover:bg-sage/20 hover:text-body'
            }`}
            aria-label={voiceReplyEnabled ? 'Turn off spoken replies' : 'Turn on spoken replies'}
            title={voiceReplyEnabled ? 'Spoken replies on' : 'Spoken replies off'}
          >
            <HiOutlineSpeakerWave size={17} />
          </button>

          <button
            onClick={submit}
            disabled={!value.trim() || disabled}
            className="w-9 h-9 shrink-0 rounded-full flex items-center justify-center bg-pine text-cream disabled:opacity-40 disabled:cursor-not-allowed hover:bg-moss transition-colors"
            aria-label="Send message"
          >
            <FiArrowUp size={18} />
          </button>
        </div>

        {micError ? (
          <p className="text-center text-[13px] text-red-500 mt-2.5">{micError}</p>
        ) : (
          <p dir="auto" className="text-center text-[13px] text-dim mt-2.5">
            {isTranscribing
              ? 'Transcribing…'
              : 'أنا اللي أقدر أديك كل المعرفة اللي انت عايزها وكل معلومة تتمناها'}
          </p>
        )}
      </div>
    </div>
  )
}
