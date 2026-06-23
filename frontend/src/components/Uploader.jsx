import { useState, useRef } from "react"

export default function Uploader({ onUpload, uploading, processing, progress, error, result }) {
  const [dragOver, setDragOver] = useState(false)
  const inputRef = useRef(null)

  const handleFile = (file) => {
    if (file) onUpload(file)
  }

  const handleDrop = (e) => {
    e.preventDefault()
    setDragOver(false)
    const file = e.dataTransfer.files[0]
    if (file) handleFile(file)
  }

  const handleDragOver = (e) => {
    e.preventDefault()
    setDragOver(true)
  }

  const handleDragLeave = () => setDragOver(false)

  return (
    <div
      className={`
        relative rounded-2xl p-8 text-center transition-all duration-300
        backdrop-blur-xl bg-white/10 border-2 border-dashed
        ${dragOver ? "border-indigo-400 bg-indigo-500/10 scale-[1.02]" : "border-white/20"}
        ${result ? "border-emerald-400/50 bg-emerald-500/5" : ""}
      `}
      onDrop={handleDrop}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
    >
      <input
        ref={inputRef}
        type="file"
        accept=".pdf"
        className="hidden"
        onChange={(e) => {
          if (e.target.files[0]) handleFile(e.target.files[0])
          e.target.value = ""
        }}
      />

      {!result && !uploading && (
        <div className="space-y-4">
          <div className="flex justify-center">
            <svg className="w-12 h-12 text-white/60" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}
                d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
              />
            </svg>
          </div>
          <div>
            <p className="text-white/80 text-lg font-medium">
              Drag & drop your PDF here
            </p>
            <p className="text-white/40 text-sm mt-1">or click to browse (max 25 MB)</p>
          </div>
          <button
            onClick={() => inputRef.current?.click()}
            className="px-6 py-2.5 rounded-xl bg-white/10 hover:bg-white/20 text-white/80
                       border border-white/10 transition-all duration-200 cursor-pointer"
          >
            Select PDF
          </button>
        </div>
      )}

      {uploading && (
        <div className="space-y-4">
          <div className="flex justify-center">
            <div className="w-12 h-12 border-4 border-white/20 border-t-indigo-400 rounded-full animate-spin" />
          </div>
          <p className="text-white/70 font-medium">
            {progress < 100 ? "Uploading..." : "Processing with AI models..."}
          </p>
          <div className="w-full max-w-xs mx-auto bg-white/10 rounded-full h-2 overflow-hidden">
            <div
              className="h-full bg-gradient-to-r from-indigo-400 to-purple-400 rounded-full transition-all duration-300"
              style={{ width: `${progress}%` }}
            />
          </div>
          <p className="text-white/40 text-sm">
            {progress < 100
              ? `${progress}%`
              : "Extracting text → Chunking → Embedding → Storing..."
            }
          </p>
        </div>
      )}

      {result && (
        <div className="space-y-3">
          <div className="flex justify-center">
            <svg className="w-12 h-12 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
            </svg>
          </div>
          <p className="text-emerald-300 font-medium text-lg">Upload successful!</p>
          <div className="text-white/50 text-sm space-y-1">
            <p>File: {result.filename}</p>
            <p>Chunks: {result.chunk_count}</p>
            <p>Text: {result.text_length.toLocaleString()} chars</p>
            <p>DB total: {result.total_chunks_in_db} chunks</p>
          </div>
        </div>
      )}

      {error && (
        <div className="mt-4 p-3 rounded-xl bg-red-500/10 border border-red-400/30">
          <p className="text-red-300 text-sm">{error}</p>
        </div>
      )}
    </div>
  )
}
