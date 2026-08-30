import { useEffect, useState } from 'react'
import axios from 'axios'
import { ArrowLeft, GitCompare } from 'lucide-react'

const API_URL = process.env.NEXT_PUBLIC_API_URL

export default function Benchmark() {
    const [report, setReport] = useState(null)
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        axios.get(`${API_URL}/benchmark/`)
            .then((res) => setReport(res.data.available === false ? null : res.data))
            .catch(() => setReport(null))
            .finally(() => setLoading(false))
    }, [])

    return (
        <div className="min-h-screen bg-[var(--color-ink)] font-body">
            <div className="max-w-6xl mx-auto px-6 py-8">
                <header className="flex items-center justify-between mb-8">
                    <div className="flex items-center gap-3">
                        <div className="w-9 h-9 rounded-lg bg-[var(--color-surface)] border border-[var(--color-line)] flex items-center justify-center">
                            <GitCompare size={18} className="text-[var(--color-cyan)]" />
                        </div>
                        <h1 className="text-xl font-display font-bold tracking-tight text-[var(--color-text)]">BENCHMARK</h1>
                    </div>
                    <a href="/" className="flex items-center gap-1 text-sm font-mono text-[var(--color-text-dim)] hover:text-[var(--color-cyan)] transition-colors">
                        <ArrowLeft size={14} />
                        <span>dashboard</span>
                    </a>
                </header>

                {loading ? (
                    <p className="text-[var(--color-text-faint)] font-mono text-sm">loading report...</p>
                ) : !report ? (
                    <div className="bg-[var(--color-surface)] border border-[var(--color-line)] rounded-xl p-10 text-center">
                        <p className="text-[var(--color-text-faint)] font-mono text-sm">
                            no benchmark data yet - run `python -m src.benchmark.compare_report`
                        </p>
                    </div>
                ) : (
                    <>
                        <p className="text-[var(--color-text-dim)] mb-6">
                            Sample size: {report.sample_size} messages, extrapolated to {report.daily_volume.toLocaleString()}/day.
                        </p>

                        <div className="bg-[var(--color-surface)] border border-[var(--color-line)] rounded-xl p-5 mb-6 overflow-x-auto">
                            <table className="w-full text-sm font-mono">
                                <thead>
                                    <tr className="text-left text-[var(--color-text-faint)] border-b border-[var(--color-line)]">
                                        <th className="py-2 pr-4">Model</th>
                                        <th className="py-2 pr-4">Macro-F1</th>
                                        <th className="py-2 pr-4">Avg Latency (s)</th>
                                        <th className="py-2">Daily Cost</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {report.results.map((r) => (
                                        <tr key={r.model} className="border-b border-[var(--color-line)]">
                                            <td className="py-2 pr-4 text-[var(--color-text)]">{r.model}</td>
                                            <td className="py-2 pr-4 text-[var(--color-cyan)]">{r.macro_f1.toFixed(4)}</td>
                                            <td className="py-2 pr-4 text-[var(--color-text)]">{r.avg_latency.toFixed(4)}</td>
                                            <td className="py-2 text-[var(--color-text)]">${r.daily_cost.toFixed(2)}</td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>

                        <div className="bg-[var(--color-surface)] border border-[var(--color-line)] rounded-xl p-5 overflow-x-auto">
                            <p className="text-xs font-mono uppercase tracking-widest text-[var(--color-text-faint)] mb-3">Per-Class F1</p>
                            <table className="w-full text-sm font-mono">
                                <thead>
                                    <tr className="text-left text-[var(--color-text-faint)] border-b border-[var(--color-line)]">
                                        <th className="py-2 pr-4">Category</th>
                                        <th className="py-2 pr-4">DistilBERT</th>
                                        <th className="py-2 pr-4">Gemini</th>
                                        <th className="py-2">Groq</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {Object.entries(report.per_class).map(([label, scores]) => (
                                        <tr key={label} className="border-b border-[var(--color-line)]">
                                            <td className="py-2 pr-4 text-[var(--color-text)]">{label}</td>
                                            <td className="py-2 pr-4 text-[var(--color-text-dim)]">{scores.distilbert.toFixed(3)}</td>
                                            <td className="py-2 pr-4 text-[var(--color-text-dim)]">{scores.gemini.toFixed(3)}</td>
                                            <td className="py-2 text-[var(--color-text-dim)]">{scores.groq.toFixed(3)}</td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    </>
                )}
            </div>
        </div>
    )
}