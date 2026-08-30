import SeverityBadge from './SeverityBadge'

export default function OffendersTable({ offenders }) {
    if (!offenders || offenders.length === 0) {
        return (
            <div className="bg-[var(--color-surface)] border border-[var(--color-line)] rounded-xl p-5">
                <p className="text-xs font-mono uppercase tracking-widest text-[var(--color-text-faint)] mb-3">
                    Repeat Offenders
                </p>
                <p className="text-sm text-[var(--color-text-faint)] font-mono py-6 text-center">
                    no repeat activity yet
                </p>
            </div>
        )
    }

    return (
        <div className="bg-[var(--color-surface)] border border-[var(--color-line)] rounded-xl p-5">
            <p className="text-xs font-mono uppercase tracking-widest text-[var(--color-text-faint)] mb-3">
                Repeat Offenders
            </p>
            <div className="divide-y divide-[var(--color-line)]">
                {offenders.map((u) => {
                    const highCount = u.deleted_count ?? u.high_confidence_count ?? 0
                    return (
                        <div key={u.slack_user_id} className="flex items-center justify-between py-2.5">
                            <span className="font-mono text-sm text-[var(--color-text)]">{u.slack_user_id}</span>
                            <div className="flex items-center gap-2">
                                <SeverityBadge level="flagged">{u.flagged_count} flagged</SeverityBadge>
                                {highCount > 0 && <SeverityBadge level="high">{highCount} high</SeverityBadge>}
                            </div>
                        </div>
                    )
                })}
            </div>
        </div>
    )
}