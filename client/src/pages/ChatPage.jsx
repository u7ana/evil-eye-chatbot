import { useEffect, useMemo, useState } from 'react'
import Sidebar from '../components/Sidebar'
import Navbar from '../components/Navbar'
import ChatWindow from '../components/ChatWindow'
import ChatInput from '../components/ChatInput'
import RightPanel from '../components/RightPanel'
import Drawer from '../components/Drawer'
import useChat from '../hooks/useChat'
import useSpeechSynthesis from '../hooks/useSpeechSynthesis'
import { bestVoiceFor } from '../utils/detectLanguage'

const SEEDED_MESSAGES = [
  {
    id: 'seed-1',
    role: 'user',
    content: 'Hello Evil Eye! Can you explain how artificial intelligence works?',
    timestamp: new Date(),
  },
  {
    id: 'seed-2',
    role: 'assistant',
    content:
      'Hello! 👋\n\nArtificial Intelligence (AI) works by enabling machines to learn from data, recognize patterns, and make decisions or predictions without being explicitly programmed for every task.',
    timestamp: new Date(),
  },
  {
    id: 'seed-3',
    role: 'user',
    content: 'Can you give me an example?',
    timestamp: new Date(),
  },
  {
    id: 'seed-4',
    role: 'assistant',
    content:
      'Sure! A common example is recommendation systems like Netflix. AI analyzes what you watch, learns your preferences, and suggests movies or shows you might like.',
    timestamp: new Date(),
  },
]

const INITIAL_CONVERSATIONS = [
  { id: 'c-active', title: 'New Conversation', timeLabel: '10:46 AM' },
  { id: 'c-2', title: 'AI and the future', timeLabel: 'Yesterday' },
  { id: 'c-3', title: 'React Project Help', timeLabel: 'Yesterday' },
  { id: 'c-4', title: 'Study Plan', timeLabel: '2 days ago' },
  { id: 'c-5', title: 'Healthy habits', timeLabel: '3 days ago' },
  { id: 'c-6', title: 'Travel Ideas', timeLabel: '4 days ago' },
]

function seedFor(id, title) {
  if (id === 'c-active') return SEEDED_MESSAGES
  return [
    {
      id: `${id}-seed`,
      role: 'assistant',
      content: `This is the start of your saved conversation about **${title}**.`,
      timestamp: new Date(),
    },
  ]
}

// SpeechSynthesisUtterance.pitch is 0-2 (1 = normal); our UI slider is -10..10 (0 = normal).
function toUtterancePitch(sliderValue) {
  return 1 + sliderValue / 10
}

export default function ChatPage() {
  const chat = useChat()
  const tts = useSpeechSynthesis()

  const [conversations, setConversations] = useState(INITIAL_CONVERSATIONS)
  const [activeId, setActiveId] = useState('c-active')
  const [store, setStore] = useState(() => ({ 'c-active': SEEDED_MESSAGES }))

  const [speed, setSpeed] = useState(1)
  const [pitch, setPitch] = useState(0)
  const [volume, setVolume] = useState(0.8)
  const [voiceReplyEnabled, setVoiceReplyEnabled] = useState(true)
  const [isDark, setIsDark] = useState(false)
  const [isLogOpen, setIsLogOpen] = useState(false)
  const [isVoicesOpen, setIsVoicesOpen] = useState(false)

  useEffect(() => {
    chat.loadConversation(SEEDED_MESSAGES)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  useEffect(() => {
    document.documentElement.classList.toggle('dark', isDark)
  }, [isDark])

  // English speaks with the best browser voice available; Arabic always
  // goes through the backend's edge-tts (male, Egyptian) - the hook itself
  // decides which based on the text, so there's nothing to pick here for Arabic.
  const enVoice = useMemo(() => bestVoiceFor(tts.voices, 'en'), [tts.voices])

  const speechOptions = {
    voiceURI: enVoice?.voiceURI,
    rate: speed,
    pitch: toUtterancePitch(pitch),
    volume,
  }

  const handleNewChat = () => {
    setStore((prev) => ({ ...prev, [activeId]: chat.messages }))
    const newId = `c-${Date.now()}`
    setConversations((prev) => [
      { id: newId, title: 'New Conversation', timeLabel: 'Just now' },
      ...prev,
    ])
    setActiveId(newId)
    chat.clearChat()
    setIsLogOpen(false)
  }

  const handleSelectConversation = (id) => {
    setIsLogOpen(false)
    if (id === activeId) return
    setStore((prev) => ({ ...prev, [activeId]: chat.messages }))
    const conversation = conversations.find((c) => c.id === id)
    const messages = store[id] || seedFor(id, conversation?.title || 'this chat')
    setActiveId(id)
    chat.loadConversation(messages)
  }

  const handleSend = async (text) => {
    const isFirstUserMessage = !chat.messages.some((m) => m.role === 'user')
    const assistantMessage = await chat.sendMessage(text)

    if (isFirstUserMessage) {
      setConversations((prev) =>
        prev.map((c) =>
          c.id === activeId && c.title === 'New Conversation'
            ? { ...c, title: text.slice(0, 32) }
            : c,
        ),
      )
    }

    if (assistantMessage && voiceReplyEnabled) {
      tts.speak(assistantMessage.id, assistantMessage.content, speechOptions)
    }
  }

  const handlePlayAudio = (message) => {
    tts.speak(message.id, message.content, speechOptions)
  }

  const handlePreviewVoice = (language) => {
    const previewId = `preview-${language}`
    const sample =
      language === 'ar'
        ? 'مرحبًا! أنا عين الحماية، رفيقك الذكي.'
        : "Hi! I'm Evil Eye, your guardian companion."
    tts.speak(previewId, sample, speechOptions)
  }

  const handleRegenerate = (messageId) => {
    chat.regenerate(messageId)
  }

  const handleVoiceSettingsChange = (partial) => {
    if ('speed' in partial) setSpeed(partial.speed)
    if ('pitch' in partial) setPitch(partial.pitch)
    if ('volume' in partial) setVolume(partial.volume)
  }

  return (
    <div className="flex flex-col h-screen w-full bg-paper text-body overflow-hidden">
      <Navbar
        isDark={isDark}
        onToggleTheme={() => setIsDark((d) => !d)}
        isThinking={chat.isLoading}
        onOpenLog={() => setIsLogOpen(true)}
        onOpenVoices={() => setIsVoicesOpen(true)}
      />

      <ChatWindow
        messages={chat.messages}
        isLoading={chat.isLoading}
        error={chat.error}
        playingId={tts.speakingId}
        onPlayAudio={handlePlayAudio}
        onRegenerate={handleRegenerate}
        onStarter={handleSend}
      />
      <ChatInput
        onSend={handleSend}
        disabled={chat.isLoading}
        voiceReplyEnabled={voiceReplyEnabled}
        onToggleVoiceReply={() => setVoiceReplyEnabled((v) => !v)}
      />

      <Drawer side="left" open={isLogOpen} onClose={() => setIsLogOpen(false)} title="Chat log">
        <Sidebar
          conversations={conversations}
          activeId={activeId}
          onNewChat={handleNewChat}
          onSelectConversation={handleSelectConversation}
        />
      </Drawer>

      <Drawer
        side="right"
        open={isVoicesOpen}
        onClose={() => setIsVoicesOpen(false)}
        title="Voice and settings"
      >
        <RightPanel
          enVoice={enVoice}
          previewingId={tts.speakingId}
          onPreviewVoice={handlePreviewVoice}
          speed={speed}
          pitch={pitch}
          volume={volume}
          onSettingsChange={handleVoiceSettingsChange}
        />
      </Drawer>
    </div>
  )
}
