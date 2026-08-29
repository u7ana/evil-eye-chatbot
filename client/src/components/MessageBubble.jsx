import { useState } from 'react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import {
  FiCopy,
  FiCheck,
  FiThumbsUp,
  FiThumbsDown,
  FiRefreshCw,
  FiVolume2,
  FiPauseCircle,
} from 'react-icons/fi'
import EyeLogo from './EyeLogo'

function formatTime(date) {
  return new Date(date).toLocaleTimeString([], {
    hour: '2-digit',
    minute: '2-digit',
  })
}

export default function MessageBubble({
  message,
  isPlaying,
  onPlayAudio,
  onRegenerate,
}) {
  const [copied, setCopied] = useState(false)
  const [feedback, setFeedback] = useState(null)
  const isUser = message.role === 'user'

  const handleCopy = () => {
    navigator.clipboard.writeText(message.content)
    setCopied(true)
    setTimeout(() => setCopied(false), 1500)
  }

  if (isUser) {
    return (
      <div className="flex items-start justify-end gap-3">
        <div className="max-w-[720px] flex flex-col items-end">
          <div
            dir="auto"
            className="rounded-[20px] rounded-tr-md bg-pine text-cream px-4 py-3 text-[15px] leading-relaxed whitespace-pre-wrap break-words shadow-[0_2px_10px_rgba(30,81,40,0.28)]"
          >
            {message.content}
          </div>
          <span className="text-[11px] text-dim mt-1.5 mr-1">
            {formatTime(message.timestamp)}
          </span>
        </div>
        <div className="w-8 h-8 rounded-full bg-cream border border-line flex items-center justify-center text-pine text-xs font-bold shrink-0">
          Y
        </div>
      </div>
    )
  }

  return (
    <div className="flex items-start gap-3">
      <EyeLogo size={32} className="shrink-0" />
      <div className="max-w-[720px] flex flex-col items-start">
        <div className="rounded-[20px] rounded-tl-md bg-card border border-line px-4 py-3 text-[15px] leading-relaxed text-body shadow-[0_1px_4px_rgba(30,81,40,0.07)]">
          <div dir="auto" className="markdown text-left">
            <ReactMarkdown remarkPlugins={[remarkGfm]}>
              {message.content}
            </ReactMarkdown>
          </div>
        </div>

        <div className="flex items-center gap-1 mt-1.5 ml-1 text-dim">
          <button
            onClick={handleCopy}
            className="p-1.5 rounded-md hover:bg-sage/20 hover:text-body transition-colors"
            aria-label="Copy message"
          >
            {copied ? (
              <FiCheck size={14} className="text-moss" />
            ) : (
              <FiCopy size={14} />
            )}
          </button>
          <button
            onClick={() => onPlayAudio(message)}
            className="p-1.5 rounded-md hover:bg-sage/20 hover:text-body transition-colors"
            aria-label={isPlaying ? 'Stop reading aloud' : 'Read aloud'}
          >
            {isPlaying ? (
              <FiPauseCircle size={14} className="text-moss" />
            ) : (
              <FiVolume2 size={14} />
            )}
          </button>
          <button
            onClick={() => setFeedback(feedback === 'up' ? null : 'up')}
            className={`p-1.5 rounded-md hover:bg-sage/20 transition-colors ${
              feedback === 'up' ? 'text-moss' : 'hover:text-body'
            }`}
            aria-label="Good response"
          >
            <FiThumbsUp size={14} />
          </button>
          <button
            onClick={() => setFeedback(feedback === 'down' ? null : 'down')}
            className={`p-1.5 rounded-md hover:bg-sage/20 transition-colors ${
              feedback === 'down' ? 'text-red-500' : 'hover:text-body'
            }`}
            aria-label="Bad response"
          >
            <FiThumbsDown size={14} />
          </button>
          <button
            onClick={() => onRegenerate(message.id)}
            className="p-1.5 rounded-md hover:bg-sage/20 hover:text-body transition-colors"
            aria-label="Regenerate response"
          >
            <FiRefreshCw size={14} />
          </button>
          <span className="text-[11px] text-dim ml-1">
            {formatTime(message.timestamp)}
          </span>
        </div>
      </div>
    </div>
  )
}
