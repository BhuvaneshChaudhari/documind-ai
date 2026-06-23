export default function ConfidenceBar({ score }) {
  const pct = Math.round((score || 0) * 100)
  const getColor = () => {
    if (pct >= 70) return "from-emerald-400 to-emerald-300"
    if (pct >= 40) return "from-amber-400 to-amber-300"
    return "from-red-400 to-red-300"
  }

  return (
    <div className="mt-3 space-y-1">
      <div className="flex justify-between text-xs text-white/40">
        <span>Confidence</span>
        <span>{pct}%</span>
      </div>
      <div className="w-full bg-white/10 rounded-full h-1.5 overflow-hidden">
        <div
          className={`h-full rounded-full bg-gradient-to-r ${getColor()} transition-all duration-500 ease-out`}
          style={{ width: `${pct}%` }}
        />
      </div>
    </div>
  )
}
