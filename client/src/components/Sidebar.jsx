import { FiPlus, FiChevronDown, FiMessageSquare } from 'react-icons/fi'
import { HiOutlineSparkles } from 'react-icons/hi2'
import EyeLogo from './EyeLogo'

export default function Sidebar({
  conversations,
  activeId,
  onNewChat,
  onSelectConversation,
}) {
  return (
    <div className="flex flex-col bg-side h-full">
      <div className="flex items-center gap-3 px-5 py-5">
        <EyeLogo size={40} />
        <div className="text-left">
          <h1 className="font-display text-lg font-semibold text-cream leading-tight">
            EE
          </h1>
          <p dir="rtl" className="text-[10px] text-sage">
            أيها الداخلون اطرحوا عنكم كل أمل في الخروج
          </p>
        </div>
      </div>

      <div className="px-4">
        <button
          onClick={onNewChat}
          className="w-full flex items-center justify-center gap-2 rounded-full bg-cream text-pine hover:bg-white transition-colors py-2.5 font-bold text-sm"
        >
          <FiPlus /> New chat
        </button>
      </div>

      <div className="px-5 pt-6 pb-2 text-[11px] tracking-[0.15em] uppercase font-semibold text-sage/80 text-left">
        Chats
      </div>

      <nav className="flex-1 overflow-y-auto px-3 space-y-1">
        {conversations.map((c) => {
          const active = c.id === activeId
          return (
            <button
              key={c.id}
              onClick={() => onSelectConversation(c.id)}
              className={`w-full flex items-center gap-3 rounded-xl px-3 py-2.5 text-left transition-colors ${
                active
                  ? 'bg-white/10 border border-sage/40'
                  : 'border border-transparent hover:bg-white/5'
              }`}
            >
              <FiMessageSquare
                className={active ? 'text-sage' : 'text-cream/40'}
                size={16}
              />
              <span className="flex-1 min-w-0 truncate text-sm text-cream/90">
                {c.title}
              </span>
              <span className="text-[11px] text-cream/40 shrink-0">
                {c.timeLabel}
              </span>
            </button>
          )
        })}
      </nav>

      <div className="px-4 pb-4 pt-2">
        <div className="rounded-2xl border border-sage/30 bg-white/5 p-4 text-left">
          <div className="flex items-center gap-2 mb-1">
            <div className="w-8 h-8 rounded-lg bg-moss flex items-center justify-center">
              <HiOutlineSparkles className="text-cream" size={16} />
            </div>
            <span className="text-sm font-bold text-cream">Evil Eye Pro</span>
          </div>
          <p className="text-xs text-cream/60 mb-3">
            Unlimited messages, voice cloning and more.
          </p>
          <button className="w-full rounded-lg bg-moss text-white text-sm font-semibold py-2 hover:bg-sage hover:text-inkg transition-colors">
            Upgrade
          </button>
        </div>

        <button className="w-full flex items-center gap-3 mt-4 px-1 py-2 text-left">
          <div className="w-9 h-9 rounded-full bg-cream flex items-center justify-center text-pine text-sm font-bold">
            Y
          </div>
          <div className="flex-1 min-w-0">
            <div className="text-sm text-cream truncate">Youhana</div>
            <div className="text-xs text-cream/50 truncate">
              youhana.dev@gmail.com
            </div>
          </div>
          <FiChevronDown className="text-cream/50" size={16} />
        </button>
      </div>
    </div>
  )
}
