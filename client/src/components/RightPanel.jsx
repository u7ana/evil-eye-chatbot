import VoiceSelector from './VoiceSelector'
import VoiceSettings from './VoiceSettings'
import AboutPanel from './AboutPanel'

export default function RightPanel({
  enVoice,
  previewingId,
  onPreviewVoice,
  speed,
  pitch,
  volume,
  onSettingsChange,
}) {
  return (
    <div className="flex flex-col gap-4 bg-paper h-full p-4 pt-16 overflow-y-auto">
      <VoiceSelector
        enVoice={enVoice}
        previewingId={previewingId}
        onPreview={onPreviewVoice}
      />
      <VoiceSettings
        speed={speed}
        pitch={pitch}
        volume={volume}
        onChange={onSettingsChange}
      />
      <AboutPanel />
    </div>
  )
}
