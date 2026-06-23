import { useState, useEffect } from "react"
import Uploader from "../components/Uploader"
import Chat from "../components/Chat"
import { useUpload } from "../hooks/useUpload"
import { useChat } from "../hooks/useChat"

export default function HomePage() {
  const { uploading, processing, progress, result, error: uploadError, upload, reset } = useUpload()
  const { messages, loading, messagesEndRef, sendMessage, clearChat } = useChat()
  const [llmModel, setLlmModel] = useState("qwen3:4b")

  useEffect(() => {
    fetch("http://localhost:8000/config")
      .then(r => r.json())
      .then(d => { if (d.llm_model) setLlmModel(d.llm_model) })
      .catch(() => {})
  }, [])

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-slate-900 to-indigo-950">
      <div className="fixed inset-0 pointer-events-none">
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-indigo-500/20 rounded-full blur-3xl" />
        <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-purple-500/20 rounded-full blur-3xl" />
      </div>

      <div className="relative max-w-6xl mx-auto px-4 py-6 min-h-screen flex flex-col">
        <header className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-indigo-400 to-purple-400 flex items-center justify-center shadow-lg">
              <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}>
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                <polyline points="14 2 14 8 20 8"/>
                <circle cx="9" cy="14" r="1.5" fill="currentColor"/>
                <circle cx="15" cy="14" r="1.5" fill="currentColor"/>
                <circle cx="12" cy="10" r="1.5" fill="currentColor"/>
                <line x1="9" y1="14" x2="12" y2="10"/>
                <line x1="15" y1="14" x2="12" y2="10"/>
              </svg>
            </div>
            <div>
              <h1 className="text-lg font-bold text-white/90">DocuMind AI</h1>
              <p className="text-xs text-white/30">Ask. Retrieve. Understand.</p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            {result && (
              <>
                <span className="text-xs text-emerald-400/70 bg-emerald-500/10 px-3 py-1.5 rounded-lg border border-emerald-400/20">
                  {result.filename}
                </span>
                <button
                  onClick={() => { reset(); clearChat() }}
                  className="text-xs px-3 py-1.5 rounded-lg bg-white/5 hover:bg-white/10 text-white/50
                             hover:text-white/80 border border-white/10 transition-all cursor-pointer"
                >
                  New Upload
                </button>
              </>
            )}
          </div>
        </header>

        {!result && (
          <div className="mb-6">
            <Uploader
              onUpload={upload}
              uploading={uploading}
              processing={processing}
              progress={progress}
              error={uploadError}
              result={result}
            />
          </div>
        )}

        <div className="flex-1 min-h-0 flex flex-col">
          <div className={"flex flex-col rounded-2xl backdrop-blur-xl bg-white/5 border border-white/10 p-4 " + (result ? 'h-[520px]' : 'h-[260px]')}>
            {result ? (
              <Chat
                messages={messages}
                loading={loading}
                onSend={sendMessage}
                messagesEndRef={messagesEndRef}
              />
            ) : (
              <div className="flex items-center justify-center h-full">
                <div className="text-center">
                  <svg className="w-16 h-16 text-white/10 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1}
                      d="M8.625 12a.375.375 0 11-.75 0 .375.375 0 01.75 0zm0 0H8.25m4.125 0a.375.375 0 11-.75 0 .375.375 0 01.75 0zm0 0H12m4.125 0a.375.375 0 11-.75 0 .375.375 0 01.75 0zm0 0h-.375M21 12c0 4.556-4.03 8.25-9 8.25a9.764 9.764 0 01-2.555-.337A5.972 5.972 0 015.41 20.97a5.969 5.969 0 01-.474-.065 4.48 4.48 0 00.978-2.025c.09-.457-.133-.901-.467-1.226C3.93 16.178 3 14.189 3 12c0-4.556 4.03-8.25 9-8.25s9 3.694 9 8.25z"
                    />
                  </svg>
                  <p className="text-white/20 text-sm">Upload a PDF above to start asking questions</p>
                </div>
              </div>
            )}
          </div>
        </div>

        <footer className="mt-4 text-center">
          <p className="text-xs text-white/20">DocuMind AI • all-MiniLM-L6-v2 • BM25 • ChromaDB • {llmModel}</p>
        </footer>
      </div>
    </div>
  )
}
