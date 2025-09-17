import { useEffect, useState } from 'react'

interface FootprintPoint {
  trader: string
  footprint: number
  edge: number
}

export default function FootprintPage() {
  const [points, setPoints] = useState<FootprintPoint[]>([])
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    async function fetchPoints() {
      try {
        const res = await fetch('http://localhost:8000/footprint/scatter?limit=500')
        if (!res.ok) throw new Error(`HTTP ${res.status}`)
        const json = await res.json()
        setPoints(json.points)
      } catch (err: any) {
        setError(err.message)
      }
    }
    fetchPoints()
  }, [])

  return (
    <main className="min-h-screen bg-gray-50 p-6">
      <h1 className="text-3xl font-bold mb-4">Footprint vs Edge</h1>
      {error && <p className="text-red-600">{error}</p>}
      {!error && (
        <div className="overflow-x-auto">
          <table className="min-w-full bg-white rounded shadow text-sm">
            <thead className="bg-gray-100 text-gray-700">
              <tr>
                <th className="px-4 py-2 text-left">Trader</th>
                <th className="px-4 py-2 text-right">Footprint</th>
                <th className="px-4 py-2 text-right">Edge (ROI)</th>
              </tr>
            </thead>
            <tbody>
              {points.map((p) => (
                <tr key={p.trader} className="border-t">
                  <td className="px-4 py-2 font-mono text-xs truncate max-w-xs">{p.trader}</td>
                  <td className="px-4 py-2 text-right">{p.footprint.toFixed(6)}</td>
                  <td className="px-4 py-2 text-right">{(p.edge * 100).toFixed(2)}%</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </main>
  )
}