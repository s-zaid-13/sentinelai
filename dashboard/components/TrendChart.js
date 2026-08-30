import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts'

const tooltipStyle = {
    background: '#182338',
    border: '1px solid #232F49',
    borderRadius: 8,
    fontFamily: 'var(--font-mono)',
    fontSize: 12,
    color: '#EDF1F9',
}

export default function TrendChart({ data }) {
    const hasEnoughData = data && data.length > 1

    return (
        <div className="bg-[var(--color-surface)] border border-[var(--color-line)] rounded-xl p-5">
            <p className="text-xs font-mono uppercase tracking-widest text-[var(--color-text-faint)] mb-4">
                Flagged Trend
            </p>
            {!hasEnoughData ? (
                <div className="h-[260px] flex items-center justify-center">
                    <p className="text-sm text-[var(--color-text-faint)] font-mono">
                        need 2+ days to plot a trend
                    </p>
                </div>
            ) : (
                <ResponsiveContainer width="100%" height={260}>
                    <AreaChart data={data}>
                        <defs>
                            <linearGradient id="trendFill" x1="0" y1="0" x2="0" y2="1">
                                <stop offset="0%" stopColor="#2DD4EE" stopOpacity={0.35} />
                                <stop offset="100%" stopColor="#2DD4EE" stopOpacity={0} />
                            </linearGradient>
                        </defs>
                        <CartesianGrid strokeDasharray="3 3" stroke="#232F49" vertical={false} />
                        <XAxis
                            dataKey="day"
                            tick={{ fontSize: 10, fill: '#8D97B3', fontFamily: 'var(--font-mono)' }}
                            axisLine={{ stroke: '#232F49' }}
                            tickLine={false}
                        />
                        <YAxis
                            allowDecimals={false}
                            tick={{ fontSize: 10, fill: '#8D97B3', fontFamily: 'var(--font-mono)' }}
                            axisLine={false}
                            tickLine={false}
                        />
                        <Tooltip contentStyle={tooltipStyle} />
                        <Area
                            type="monotone"
                            dataKey="count"
                            stroke="#2DD4EE"
                            strokeWidth={2}
                            fill="url(#trendFill)"
                            dot={{ r: 3, fill: '#2DD4EE', strokeWidth: 0 }}
                        />
                    </AreaChart>
                </ResponsiveContainer>
            )}
        </div>
    )
}