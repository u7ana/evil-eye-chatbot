import { FiPlay, FiPause } from 'react-icons/fi'
import { HiOutlineSpeakerWave } from 'react-icons/hi2'

function Waveform({ active }) {
  const heights = [6, 12, 8, 16, 5]
  return (
    <div className="flex items-end gap-0.5 h-4">
      {heights.map((h, i) => (
        <span
          key={i}
          className={`w-0.5 rounded-full ${active ? 'bg-moss' : 'bg-line'}`}
          style={{ height: h }}
        />
      ))}
    </div>
  )
}

function VoiceRow({ language, code, nativeName, voiceName, available, previewing, onPreview }) {
  return (
    <div className="flex items-center gap-3 rounded-xl border border-line px-3 py-3">
      <button
        onClick={() => available && onPreview(code)}
        disabled={!available}
        className={`w-9 h-9 shrink-0 rounded-full flex items-center justify-center transition-colors ${
          available
            ? 'bg-pine text-cream hover:bg-moss'
            : 'bg-line text-dim cursor-not-allowed'
        }`}
        aria-label={
          available
            ? previewing
              ? `Stop ${language} preview`
              : `Preview the ${language} voice`
            : `No ${language} voice available`
        }
      >
        {previewing ? <FiPause size={14} /> : <FiPlay size={14} className="ml-0.5" />}
      </button>
      <span className="flex-1 min-w-0 text-left">
        <span className="flex items-baseline gap-2">
          <span className="font-display text-[15px] font-semibold text-body">{language}</span>
          <span className="text-xs text-dim">{nativeName}</span>
        </span>
        <span className="block text-[11px] text-dim truncate">
          {voiceName || 'Not installed on this device'}
        </span>
      </span>
      <Waveform active={previewing} />
    </div>
  )
}

export default function VoiceSelector({ enVoice, previewingId, onPreview }) {
  return (
    <div className="rounded-2xl bg-card border border-line p-4">
      <div className="flex items-center justify-between mb-1">
        <h3 className="font-display text-sm font-semibold text-body">Voices</h3>
        <HiOutlineSpeakerWave className="text-dim" size={16} />
      </div>
      <p className="text-xs text-dim mb-3">
        Evil Eye replies with the voice that matches the language you write.
      </p>

      <div className="space-y-2">
        <VoiceRow
          language="English"
          code="en"
          nativeName=""
          voiceName={enVoice?.name.replace(/^Microsoft /, '')}
          available={Boolean(enVoice)}
          previewing={previewingId === 'preview-en'}
          onPreview={onPreview}
        />
        <VoiceRow
          language="Arabic"
          code="ar"
          nativeName="العربية"
          voiceName="Shakir · via edge-tts"
          available
          previewing={previewingId === 'preview-ar'}
          onPreview={onPreview}
        />
      </div>
    </div>
  )
}
