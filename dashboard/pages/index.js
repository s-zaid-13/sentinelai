import { useEffect, useState } from 'react'
import axios from 'axios'
import { Activity, Radar, ShieldAlert, ArrowUpRight } from 'lucide-react'
import StatsCard from '@/components/StatsCard'
import CategoryChart from '@/components/CategoryChart'
import TrendChart from '@/components/TrendChart'
import OffendersTable from '@/components/OffendersTable'
import StatusPulse from '@/components/StatusPulse'

const API_URL = process.env.NEXT_PUBLIC_API_URL
const POLL_INTERVAL_MS = 3000

export default function Dashboard() {
  const [stats, setStats] = useState(null)
  const [error, setError] = useState(null)

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const res = await axios.get(`${API_URL}/stats/`)
        setStats(res.data)
        setError(null)
      } catch (err) {
        setError('backend unreachable - check API connection')
      }
    }
    fetchStats()
    const interval = setInterval(fetchStats, POLL_INTERVAL_MS)
    return () => clearInterval(interval)
  }, [])

  return (
    <div className="min-h-screen bg-[var(--color-ink)] font-body">
      <div className="max-w-6xl mx-auto px-6 py-8">
        <header className="flex items-center justify-between mb-8">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-lg bg-[var(--color-surface)] border border-[var(--color-line)] flex items-center justify-center">
              <ShieldAlert size={18} className="text-[var(--color-cyan)]" />
            </div>
            <div>
              <h1 className="text-xl font-display font-bold tracking-tight text-[var(--color-text)]">SENTINEL</h1>
              <StatusPulse />
            </div>
          </div>
          <a href="/benchmark" className="flex items-center gap-1 text-sm font-mono text-[var(--color-text-dim)] hover:text-[var(--color-cyan)] transition-colors">
            <span>benchmark report</span>
            <ArrowUpRight size={14} />
          </a>
        </header>

        {error && (
          <div className="mb-6 px-4 py-3 rounded-lg bg-[rgba(247,110,124,0.1)] border border-[rgba(247,110,124,0.3)] text-[var(--color-rose)] text-sm font-mono">
            {error}
          </div>
        )}

        {!stats ? (
          <div className="text-[var(--color-text-faint)] font-mono text-sm py-20 text-center">
            connecting to feed...
          </div>
        ) : (
          <>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
              <StatsCard label="Total Scanned" value={stats.total_scanned} icon={Activity} accent="cyan" />
              <StatsCard label="Scanned Today" value={stats.scanned_today} icon={Radar} accent="cyan" />
              <StatsCard label="Flagged Today" value={stats.flagged_today} icon={ShieldAlert} accent="amber" />
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
              <CategoryChart data={stats.category_breakdown} />
              <TrendChart data={stats.trend} />
            </div>

            <OffendersTable offenders={stats.repeat_offenders} />
          </>
        )}
      </div>
    </div>
  )
}