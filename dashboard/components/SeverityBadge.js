export default function SeverityBadge({ level, children }) {
    const styles = {
        flagged: 'bg-[rgba(245,185,77,0.12)] text-[var(--color-amber)] border-[rgba(245,185,77,0.3)]',
        high: 'bg-[rgba(247,110,124,0.12)] text-[var(--color-rose)] border-[rgba(247,110,124,0.3)]',
    }
    return (
        <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-mono border ${styles[level] || styles.flagged}`}>
            {children}
        </span>
    )
}