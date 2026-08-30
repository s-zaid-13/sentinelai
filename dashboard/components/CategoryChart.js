import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts'

const tooltipStyle = {
    background: '#182338',
    border: '1px solid #232F49',
    borderRadius: 8,
    fontFamily: 'var(--font-mono)',
    fontSize: 12,
    color: '#EDF1F9',
}

export default function CategoryChart({ data }) {
    const chartData = Object.entries(data || {}).map(([category, count]) => ({
        category: category.replace('_', ' '),
        count,
    }))

    return (
        <div className="bg-[var(--color-surface)] border border-[var(--color-line)] rounded-xl p-5">
            <p className="text-xs font-mono uppercase tracking-widest text-[var(--color-text-faint)] mb-4">
                Category Breakdown
            </p>
            <ResponsiveContainer width="100%" height={260}>
                <BarChart data={chartData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#232F49" vertical={false} />
                    <XAxis
                        dataKey="category"
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
                    <Tooltip contentStyle={tooltipStyle} cursor={{ fill: 'rgba(45,212,238,0.06)' }} />
                    <Bar dataKey="count" fill="#2DD4EE" radius={[4, 4, 0, 0]} maxBarSize={36} />
                </BarChart>
            </ResponsiveContainer>
        </div>
    )
}