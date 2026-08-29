import { LiveEye } from './EyeLogo'

// While the AI thinks, the eye itself blinks faster — the brand is the
// typing indicator.
export default function LoadingAnimation() {
  return (
    <div className="flex items-center gap-3 max-w-[720px]">
      <LiveEye size={32} thinking className="shrink-0" />
      <div className="rounded-2xl rounded-tl-sm bg-card border border-line px-4 py-3">
        <span className="text-sm text-dim italic">Thinking…</span>
      </div>
    </div>
  )
}
