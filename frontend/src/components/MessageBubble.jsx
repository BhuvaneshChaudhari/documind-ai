import { useState } from "react"
import ConfidenceBar from "./ConfidenceBar"
import SourcePanel from "./SourcePanel"

export default function MessageBubble({ message }) {
  const [showSources, setShowSources] = useState(false)
  const isUser = message.role === "user"
  const isError = message.isError

  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"} mb-4`}>
      <div
        className={`
          max-w-[80%] rounded-2xl px-5 py-3
          backdrop-blur-xl
          ${isUser
            ? "bg-indigo-500/20 border border-indigo-400/30 text-white/90"
            : isError
              ? "bg-red-500/10 border border-red-400/30 text-red-200"
              : "bg-white/10 border border-white/10 text-white/90"
          }
        `}
      >
        {!isUser && !isError && (
          <div className="flex items-center gap-2 mb-2">
            <div className="w-6 h-6 rounded-full bg-gradient-to-br from-indigo-400 to-purple-400 flex items-center justify-center">
              <svg className="w-3.5 h-3.5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                  d="M9.75 3.104v5.714a2.25 2.25 0 01-.659 1.591L5 14.5M9.75 3.104c-.251.023-.501.05-.75.082m.75-.082a24.301 24.301 0 014.5 0m0 0v5.714c0 .597.237 1.17.659 1.591L19.8 15.3M14.25 3.104c.251.023.501.05.75.082M19.8 15.3l-1.57.393A9.065 9.065 0 0112 15a9.065 9.065 0 00-6.23.693L5 14.5m14.8.8l1.402 1.402c1.232 1.232.65 3.318-1.067 3.611A48.309 48.309 0 0112 21c-2.773 0-5.491-.235-8.135-.687-1.718-.293-2.3-2.379-1.067-3.61L5 14.5"
                />
              </svg>
            </div>
            <span className="text-xs font-medium text-white/50 uppercase tracking-wide">AI Assistant</span>
          </div>
        )}

        {isUser && (
          <div className="flex items-center gap-2 mb-1.5">
            <span className="text-xs font-medium text-indigo-300/70 uppercase tracking-wide">You</span>
          </div>
        )}

        <p className="text-sm leading-relaxed whitespace-pre-wrap">{message.text}</p>

        {!isUser && !isError && message.confidence !== undefined && (
          <ConfidenceBar score={message.confidence} />
        )}

        {!isUser && !isError && message.sources?.length > 0 && (
          <button
            onClick={() => setShowSources(!showSources)}
            className="mt-2 text-xs text-white/40 hover:text-white/70 transition-colors cursor-pointer flex items-center gap-1"
          >
            <svg className={`w-3 h-3 transition-transform ${showSources ? "rotate-90" : ""}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
            </svg>
            {showSources ? "Hide" : "Show"} sources ({message.sources.length})
          </button>
        )}

        {showSources && message.sources?.length > 0 && (
          <SourcePanel sources={message.sources} />
        )}
      </div>
    </div>
  )
}
