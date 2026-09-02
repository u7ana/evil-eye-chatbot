import { useCallback, useState } from 'react'
import { sendChatMessage } from '../services/api'

let idCounter = 0
const nextId = () => `msg-${Date.now()}-${idCounter++}`

function describeError(err, fallback) {
  if (err?.code === 'ECONNABORTED') {
    return "Evil Eye's server is taking longer than usual to wake up. Please try sending that again."
  }
  return err?.response?.data?.detail || fallback
}

const WELCOME_MESSAGE = {
  id: 'welcome',
  role: 'assistant',
  content: "Hello! 👋\n\nI'm Evil Eye, your AI assistant. Ask me anything, and I can speak my answers back to you in the voice you choose.",
  timestamp: new Date(),
}

export default function useChat() {
  const [messages, setMessages] = useState([WELCOME_MESSAGE])
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState(null)

  const clearChat = useCallback(() => {
    setMessages([WELCOME_MESSAGE])
    setError(null)
  }, [])

  const loadConversation = useCallback((newMessages) => {
    setMessages(newMessages && newMessages.length ? newMessages : [WELCOME_MESSAGE])
    setError(null)
  }, [])

  const sendMessage = useCallback(
    async (text) => {
      const trimmed = text.trim()
      if (!trimmed || isLoading) return

      const userMessage = {
        id: nextId(),
        role: 'user',
        content: trimmed,
        timestamp: new Date(),
      }

      setMessages((prev) => [...prev, userMessage])
      setIsLoading(true)
      setError(null)

      try {
        const history = [...messages, userMessage]
          .filter((m) => m.id !== 'welcome')
          .map((m) => ({ role: m.role, content: m.content }))

        const data = await sendChatMessage({ message: trimmed, history })

        const assistantMessage = {
          id: nextId(),
          role: 'assistant',
          content: data.reply,
          timestamp: new Date(),
        }

        setMessages((prev) => [...prev, assistantMessage])
        return assistantMessage
      } catch (err) {
        setError(describeError(err, 'Something went wrong reaching Evil Eye. Please try again.'))
      } finally {
        setIsLoading(false)
      }
    },
    [messages, isLoading],
  )

  const regenerate = useCallback(
    async (messageId) => {
      const index = messages.findIndex((m) => m.id === messageId)
      if (index <= 0) return
      const priorUserMessage = [...messages.slice(0, index)]
        .reverse()
        .find((m) => m.role === 'user')
      if (!priorUserMessage) return

      setIsLoading(true)
      setError(null)
      try {
        const history = messages
          .slice(0, index)
          .filter((m) => m.id !== 'welcome')
          .map((m) => ({ role: m.role, content: m.content }))

        const data = await sendChatMessage({ message: priorUserMessage.content, history })

        setMessages((prev) =>
          prev.map((m) =>
            m.id === messageId
              ? { ...m, content: data.reply, timestamp: new Date() }
              : m,
          ),
        )
      } catch (err) {
        setError(describeError(err, 'Could not regenerate the response.'))
      } finally {
        setIsLoading(false)
      }
    },
    [messages],
  )

  return {
    messages,
    isLoading,
    error,
    sendMessage,
    regenerate,
    clearChat,
    loadConversation,
  }
}
