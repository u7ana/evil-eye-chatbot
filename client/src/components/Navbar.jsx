import { FiMenu, FiSun, FiMoon } from 'react-icons/fi'
import { HiOutlineSpeakerWave } from 'react-icons/hi2'
import { LiveEye } from './EyeLogo'

export default function Navbar({ isDark, onToggleTheme, isThinking, onOpenLog, onOpenVoices }) {
  return (
    <header className="border-b-2 border-pine/15 bg-paper">
      <div className="grid grid-cols-[1fr_auto_1fr] items-center px-5 sm:px-8 py-4">
        <button
          onClick={onOpenLog}
          className="justify-self-start flex items-center gap-2 text-dim hover:text-body transition-colors -ml-1 px-1 py-1 rounded-md"
          aria-label="Open your chat log"
        >
          <FiMenu size={19} />
          <span className="hidden sm:inline text-xs tracking-[0.14em] uppercase font-semibold">
            Log
          </span>
        </button>

        <div className="justify-self-center flex flex-col items-center gap-1.5">
          <LiveEye size={40} thinking={isThinking} />
          <div className="text-center">
            <h1 className="font-display text-[22px] leading-none font-semibold text-pine dark:text-cream">
              EE
            </h1>
            <p dir="rtl" className="text-sm font-bold tracking-[0.04em] text-moss mt-1">
              أيها الداخلون اطرحوا عنكم كل أمل في الخروج
            </p>
          </div>
        </div>

        <div className="justify-self-end flex items-center gap-1">
          <button
            onClick={onOpenVoices}
            className="w-9 h-9 rounded-full flex items-center justify-center text-dim hover:bg-sage/20 hover:text-body transition-colors"
            aria-label="Open voice and settings"
          >
            <HiOutlineSpeakerWave size={17} />
          </button>
          <button
            onClick={onToggleTheme}
            className="w-9 h-9 rounded-full flex items-center justify-center text-dim hover:bg-sage/20 hover:text-body transition-colors"
            aria-label={isDark ? 'Switch to light mode' : 'Switch to dark mode'}
          >
            {isDark ? <FiSun size={17} /> : <FiMoon size={17} />}
          </button>
        </div>
      </div>
    </header>
  )
}
