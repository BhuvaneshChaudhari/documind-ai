import { useState, useCallback, useRef } from "react"
import { askQuestion } from "../services/api"

export function useChat() {
  const [messages, setMessages] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const messagesEndRef = useRef(null)

  const sendMessage = useCallback(async (text) => {
    const userMsg = { role: "user", text }
    setMessages((prev) => [...prev, userMsg])
    setLoading(true)
    setError(null)
    try {
      const data = await askQuestion(text)
      const assistantMsg = {
        role: "assistant",
        text: data.answer,
        confidence: data.confidence_score,
        sources: data.sources || [],
      }
      setMessages((prev) => [...prev, assistantMsg])
    } catch (err) {
      setError(err.message)
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          text: `Error: ${err.message}`,
          confidence: 0,
          sources: [],
          isError: true,
        },
      ])
    } finally {
      setLoading(false)
    }
  }, [])

  const clearChat = useCallback(() => {
    setMessages([])
    setError(null)
  }, [])

  return { messages, loading, error, messagesEndRef, sendMessage, clearChat }
}
