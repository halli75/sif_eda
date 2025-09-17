import { useEffect, useState } from 'react'

interface TraderSummary {
  trader: string
  pnl: number
  roi: number | null
  volume: number | null
  label: string | null
}

interface OverviewResponse {
  total_traders: number
  total_volume: number
  total_pnl: number
  average_roi: number | null
  top_traders: TraderSummary[]
}

export default function Home() {
  const [data, setData] = useState<OverviewResponse | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    async function fetchOverview() {
      try {
        const res = await fetch('http://localhost:8000/overview')
        if (!res.ok) throw new Error(`HTTP ${res.status}`)
        const json = await res.json()
        setData(json)
      } catch (err: any) {
        setError(err.message)
      }
    }
    fetchOverview()
  }, [])

  return (
    <main className="min-h-screen bg-gray-50 p-6">
      <h1 className="text-3xl font-bold mb-4">Polymarket Trader Explorer</h1>
      {!data && !error && <p>Loading...</p>}
      {error && <p className="text-red-600">{error}</p>}
      {data && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="p-4 bg-white rounded shadow">
              <h2 className="text-sm text-gray-600">Total Traders</h2>
              <p className="text-xl font-semibold">{data.total_traders.toLocaleString()}</p>
            </div>
            <div className="p-4 bg-white rounded shadow">
              <h2 className="text-sm text-gray-600">Total Volume</h2>
              <p className="text-xl font-semibold">{data.total_volume.toLocaleString(undefined, { maximumFractionDigits: 2 })}</p>
            </div>
            <div className="p-4 bg-white rounded shadow">
              <h2 className="text-sm text-gray-600">Total PnL</h2>
              <p className="text-xl font-semibold">{data.total_pnl.toLocaleString(undefined, { maximumFractionDigits: 2 })}</p>
            </div>
            <div className="p-4 bg-white rounded shadow">
              <h2 className="text-sm text-gray-600">Average ROI</h2>
              <p className="text-xl font-semibold">{data.average_roi !== null ? (data.average_roi * 100).toFixed(2) + '%' : 'N/A'}</p>
            </div>
          </div>
          <div>
            <h2 className="text-lg font-medium mb-2">Top Traders by Profit</h2>
            <div className="overflow-x-auto">
              <table className="min-w-full bg-white rounded shadow text-sm">
                <thead className="bg-gray-100 text-gray-700">
                  <tr>
                    <th className="px-4 py-2 text-left">Trader</th>
                    <th className="px-4 py-2 text-right">PnL</th>
                    <th className="px-4 py-2 text-right">ROI</th>
                    <th className="px-4 py-2 text-right">Volume</th>
                    <th className="px-4 py-2">Label</th>
                  </tr>
                </thead>
                <tbody>
                  {data.top_traders.map((t) => (
                    <tr key={t.trader} className="border-t">
                      <td className="px-4 py-2 font-mono text-xs truncate max-w-xs">{t.trader}</td>
                      <td className="px-4 py-2 text-right">{t.pnl.toLocaleString(undefined, { maximumFractionDigits: 2 })}</td>
                      <td className="px-4 py-2 text-right">{t.roi !== null ? (t.roi * 100).toFixed(2) + '%' : '—'}</td>
                      <td className="px-4 py-2 text-right">{t.volume !== null ? t.volume.toLocaleString(undefined, { maximumFractionDigits: 2 }) : '—'}</td>
                      <td className="px-4 py-2">{t.label ?? '—'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}
    </main>
  )
}