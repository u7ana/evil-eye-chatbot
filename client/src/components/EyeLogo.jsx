import { useEffect, useRef } from 'react'

// Brand mark: evil-eye rings set inside a map pin (see /logo-preview.html
// for the full lockup with the winding road and cross).

function Rings({ pupilRef, lidsClass }) {
  return (
    <>
      <path
        d="M256 26C157 26 77 106 77 205c0 76 50 146 100 202 33 37 63 63 79 77 16-14 46-40 79-77 50-56 100-126 100-202C435 106 355 26 256 26Z"
        fill="#1e5128"
      />
      <g className={lidsClass}>
        <circle cx="256" cy="205" r="126" fill="#6b9b4e" />
        <circle cx="256" cy="205" r="92" fill="#f2f5e8" />
        <g ref={pupilRef} className="eye-pupil">
          <circle cx="256" cy="205" r="62" fill="#94b877" />
          <circle cx="256" cy="205" r="32" fill="#10331b" />
          <circle cx="271" cy="191" r="9" fill="#fff" />
        </g>
      </g>
    </>
  )
}

export default function EyeLogo({ size = 40, className = '' }) {
  return (
    <span
      className={`inline-flex items-center justify-center ${className}`}
      style={{ width: size, height: size }}
    >
      <svg width={size} height={size} viewBox="0 0 512 512" aria-label="Evil Eye logo">
        <Rings />
      </svg>
    </span>
  )
}

/**
 * The living version of the mark: the pupil follows the cursor and the eye
 * blinks — quicker while `thinking`. Falls back to a still eye when the
 * user prefers reduced motion.
 */
export function LiveEye({ size = 40, thinking = false, className = '' }) {
  const wrapRef = useRef(null)
  const pupilRef = useRef(null)

  useEffect(() => {
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return

    let raf = null
    const onMove = (e) => {
      if (raf) return
      raf = requestAnimationFrame(() => {
        raf = null
        const wrap = wrapRef.current
        const pupil = pupilRef.current
        if (!wrap || !pupil) return
        const r = wrap.getBoundingClientRect()
        const cx = r.left + r.width / 2
        const cy = r.top + r.height * 0.4 // eye sits in the pin's head
        const dx = e.clientX - cx
        const dy = e.clientY - cy
        const dist = Math.hypot(dx, dy) || 1
        const reach = Math.min(dist / 6, 24) // viewBox units, capped
        pupil.style.transform = `translate(${(dx / dist) * reach}px, ${(dy / dist) * reach}px)`
      })
    }

    window.addEventListener('mousemove', onMove)
    return () => {
      window.removeEventListener('mousemove', onMove)
      if (raf) cancelAnimationFrame(raf)
    }
  }, [])

  return (
    <span
      ref={wrapRef}
      className={`inline-flex items-center justify-center ${className}`}
      style={{ width: size, height: size }}
    >
      <svg width={size} height={size} viewBox="0 0 512 512" aria-label="Evil Eye logo">
        <Rings
          pupilRef={pupilRef}
          lidsClass={`eye-lids${thinking ? ' eye-lids--thinking' : ''}`}
        />
      </svg>
    </span>
  )
}
