export default function SourcePanel({ sources }) {
  return (
    <div className="mt-3 space-y-2 border-t border-white/10 pt-3">
      <p className="text-xs font-medium text-white/40 uppercase tracking-wide">Source Chunks</p>
      {sources.map((src, i) => (
        <div
          key={i}
          className="p-2.5 rounded-lg bg-white/5 border border-white/5 space-y-1"
        >
          <div className="flex items-center justify-between text-xs">
            <span className="text-indigo-300/70 font-medium truncate max-w-[60%]">
              {src.source_file}
            </span>
            <span className="text-white/30">score: {src.score.toFixed(3)}</span>
          </div>
          <p className="text-xs text-white/50 leading-relaxed line-clamp-3">
            {src.text}
          </p>
        </div>
      ))}
    </div>
  )
}
