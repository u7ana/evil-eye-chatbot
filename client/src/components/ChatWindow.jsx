import { useEffect, useRef } from 'react'
import MessageBubble from './MessageBubble'
import LoadingAnimation from './LoadingAnimation'

function sameDay(a, b) {
  const d1 = new Date(a)
  const d2 = new Date(b)
  return d1.toDateString() === d2.toDateString()
}

function dayLabel(date) {
  const d = new Date(date)
  const today = new Date()
  const yesterday = new Date()
  yesterday.setDate(today.getDate() - 1)
  if (sameDay(d, today)) return 'Today'
  if (sameDay(d, yesterday)) return 'Yesterday'
  return d.toLocaleDateString([], { month: 'short', day: 'numeric' })
}

/* The conversation travels along the brand's dashed road: each day is a
   new stretch of it. */
function RoadDivider({ label }) {
  return (
    <div className="flex items-center gap-3" aria-label={label}>
      <span className="flex-1 border-t-2 border-dashed border-sage/70" />
      <span className="text-xs text-dim bg-card px-3 py-1 rounded-full border border-line">
        {label}
      </span>
      <span className="flex-1 border-t-2 border-dashed border-sage/70" />
    </div>
  )
}

const STARTERS = [
  { text: 'Explain how AI works — simply', lang: 'en' },
  { text: 'Help me plan a productive day', lang: 'en' },
  { text: 'اشرح لي الذكاء الاصطناعي ببساطة', lang: 'ar' },
  { text: 'اقترح لي خطة ليوم منتج', lang: 'ar' },
]

/* First-visit moment: two English and two Arabic starters, so the first
   click already demonstrates the bilingual voice switching. */
function Starters({ onStarter }) {
  return (
    <div className="mt-2">
      <p className="text-xs text-dim text-center mb-3">
        Try one of these · جرّب واحدة من هذه
      </p>
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
        {STARTERS.map((s) => (
          <button
            key={s.text}
            dir="auto"
            onClick={() => onStarter(s.text)}
            className="text-left rounded-xl border border-line bg-card px-4 py-3 text-sm text-body hover:border-moss hover:-translate-y-0.5 transition-all shadow-[0_1px_4px_rgba(30,81,40,0.06)]"
          >
            {s.text}
          </button>
        ))}
      </div>
    </div>
  )
}

export default function ChatWindow({
  messages,
  isLoading,
  error,
  playingId,
  onPlayAudio,
  onRegenerate,
  onStarter,
}) {
  const bottomRef = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, isLoading])

  const showStarters =
    !isLoading && onStarter && !messages.some((m) => m.role === 'user')

  let lastLabel = null

  return (
    <div className="flex-1 overflow-y-auto px-6 py-6 grain">
      <div className="max-w-3xl mx-auto flex flex-col gap-5">
        {messages.map((m) => {
          const label = dayLabel(m.timestamp)
          const showDivider = label !== lastLabel
          lastLabel = label
          return (
            <div key={m.id} className="flex flex-col gap-5 msg-in">
              {showDivider && <RoadDivider label={label} />}
              <MessageBubble
                message={m}
                isPlaying={playingId === m.id}
                onPlayAudio={onPlayAudio}
                onRegenerate={onRegenerate}
              />
            </div>
          )
        })}

        {showStarters && <Starters onStarter={onStarter} />}

        {isLoading && <LoadingAnimation />}

        {error && (
          <div className="text-sm text-red-800 dark:text-red-300 bg-red-700/10 border border-red-700/30 rounded-xl px-4 py-3 text-left">
            {error}
          </div>
        )}

        <div ref={bottomRef} />
      </div>
    </div>
  )
}
