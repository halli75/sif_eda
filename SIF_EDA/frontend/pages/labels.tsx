import { useEffect, useState } from 'react'

interface LabelSummaryItem {
  label: string
  count: number
  avg_ppv: number | null
  roi_mean: number | null
  roi_std: number | null
}

export default function LabelsPage() {
  const [items, setItems] = useState<LabelSummaryItem[]>([])
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    async function fetchLabels() {
      try {
        const res = await fetch('http://localhost:8000/labels/summary')
        if (!res.ok) throw new Error(`HTTP ${res.status}`)
        const json = await res.json()
        setItems(json.labels)
      } catch (err: any) {
        setError(err.message)
      }
    }
    fetchLabels()
  }, [])

  return (
    <main className="min-h-screen bg-gray-50 p-6">
      <h1 className="text-3xl font-bold mb-4">Label Audit</h1>
      {error && <p className="text-red-600">{error}</p>}
      {!error && (
        <div className="overflow-x-auto">
          <table className="min-w-full bg-white rounded shadow text-sm">
            <thead className="bg-gray-100 text-gray-700">
              <tr>
                <th className="px-4 py-2 text-left">Label</th>
                <th className="px-4 py-2 text-right">Traders</th>
                <th className="px-4 py-2 text-right">Avg PPV</th>
                <th className="px-4 py-2 text-right">Mean ROI</th>
                <th className="px-4 py-2 text-right">ROI StdDev</th>
              </tr>
            </thead>
            <tbody>
              {items.map((item) => (
                <tr key={item.label} className="border-t">
                  <td className="px-4 py-2">{item.label}</td>
                  <td className="px-4 py-2 text-right">{item.count}</td>
                  <td className="px-4 py-2 text-right">{item.avg_ppv !== null ? item.avg_ppv.toFixed(6) : '—'}</td>
                  <td className="px-4 py-2 text-right">{item.roi_mean !== null ? (item.roi_mean * 100).toFixed(2) + '%' : '—'}</td>
                  <td className="px-4 py-2 text-right">{item.roi_std !== null ? (item.roi_std * 100).toFixed(2) + '%' : '—'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </main>
  )
}