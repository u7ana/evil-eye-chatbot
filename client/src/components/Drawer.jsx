import { useEffect } from 'react'
import { FiX } from 'react-icons/fi'

/**
 * Slide-over panel. The sidebar (chat log) and the voice panel are summoned
 * through this rather than sitting as permanent columns — the chat itself
 * stays the whole page.
 */
export default function Drawer({ side = 'left', open, onClose, title, children }) {
  useEffect(() => {
    if (!open) return
    const onKey = (e) => e.key === 'Escape' && onClose()
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [open, onClose])

  const edge = side === 'left' ? 'left-0' : 'right-0'
  const hiddenX = side === 'left' ? '-translate-x-full' : 'translate-x-full'

  return (
    <>
      <div
        className={`fixed inset-0 bg-inkg/40 backdrop-blur-[2px] z-40 transition-opacity duration-300 ${
          open ? 'opacity-100' : 'opacity-0 pointer-events-none'
        }`}
        onClick={onClose}
        aria-hidden="true"
      />
      <div
        role="dialog"
        aria-modal="true"
        aria-label={title}
        className={`fixed top-0 ${edge} h-full w-[320px] max-w-[86vw] z-50 shadow-2xl transition-transform duration-300 ease-out ${
          open ? 'translate-x-0' : hiddenX
        }`}
      >
        {side === 'right' && (
          <button
            onClick={onClose}
            className="absolute top-4 left-[-44px] w-9 h-9 rounded-full bg-card border border-line flex items-center justify-center text-dim hover:text-body"
            aria-label={`Close ${title}`}
          >
            <FiX size={16} />
          </button>
        )}
        {children}
        {side === 'left' && (
          <button
            onClick={onClose}
            className="absolute top-4 right-[-44px] w-9 h-9 rounded-full bg-card border border-line flex items-center justify-center text-dim hover:text-body"
            aria-label={`Close ${title}`}
          >
            <FiX size={16} />
          </button>
        )}
      </div>
    </>
  )
}
