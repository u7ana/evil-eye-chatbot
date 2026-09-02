import { useEffect, useState } from 'react'
import { LiveEye } from './EyeLogo'

// While the AI thinks, the eye itself blinks faster — the brand is the
// typing indicator. If it runs long, that's almost always the free-tier
// backend waking back up from being idle, not something broken.
export default function LoadingAnimation() {
  const [showWakingHint, setShowWakingHint] = useState(false)

  useEffect(() => {
    const timer = setTimeout(() => setShowWakingHint(true), 6000)
    return () => clearTimeout(timer)
  }, [])

  return (
    <div className="flex items-center gap-3 max-w-[720px]">
      <LiveEye size={32} thinking className="shrink-0" />
      <div className="rounded-2xl rounded-tl-sm bg-card border border-line px-4 py-3">
        <span className="text-sm text-dim italic">
          {showWakingHint ? 'Waking up… this can take a minute the first time.' : 'Thinking…'}
        </span>
      </div>
    </div>
  )
}
