export default function StatusPulse({ label = 'live · scanning' }) {
    return (
        <div className="flex items-center gap-2">
            <span className="relative inline-flex h-2 w-2 pulse-dot">
                <span className="relative inline-flex rounded-full h-2 w-2 bg-[var(--color-emerald)]" />
            </span>
            <span className="text-xs font-mono tracking-wide text-[var(--color-text-dim)] uppercase">
                {label}
            </span>
        </div>
    )
}