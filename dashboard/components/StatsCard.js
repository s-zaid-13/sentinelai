export default function StatsCard({ label, value, icon: Icon, accent = 'cyan' }) {
    const accentMap = {
        cyan: { text: 'text-[var(--color-cyan)]', border: 'border-l-[var(--color-cyan)]', glow: 'shadow-[0_0_24px_-8px_rgba(45,212,238,0.35)]' },
        amber: { text: 'text-[var(--color-amber)]', border: 'border-l-[var(--color-amber)]', glow: 'shadow-[0_0_24px_-8px_rgba(245,185,77,0.35)]' },
        emerald: { text: 'text-[var(--color-emerald)]', border: 'border-l-[var(--color-emerald)]', glow: 'shadow-[0_0_24px_-8px_rgba(53,211,153,0.35)]' },
    }
    const a = accentMap[accent] || accentMap.cyan

    return (
        <div
            className={`bg-[var(--color-surface)] border border-[var(--color-line)] border-l-2 ${a.border} rounded-xl p-5 transition-all duration-300 hover:bg-[var(--color-surface-2)] hover:-translate-y-0.5 ${a.glow}`}
        >
            <div className="flex items-start justify-between mb-3">
                <p className="text-xs font-mono uppercase tracking-widest text-[var(--color-text-faint)]">
                    {label}
                </p>
                {Icon && <Icon size={16} className={a.text} strokeWidth={2} />}
            </div>
            <p className="text-4xl font-bold font-mono text-[var(--color-text)] tabular-nums">
                {value}
            </p>
        </div>
    )
}