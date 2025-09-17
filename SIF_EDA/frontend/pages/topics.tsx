import { useState } from 'react'

interface TopicShare {
  topic: string
  share: number
}

interface TraderTopicResponse {
  trader: string
  active_topics: number
  topic_entropy: number
  niche_score: number
  topic_shares: TopicShare[]
}

export default function TopicsPage() {
  const [traderId, setTraderId] = useState('')
  const [data, setData] = useState<TraderTopicResponse | null>(null)
  const [error, setError] = useState<string | null>(null)

  async function fetchTopics() {
    setData(null)
    setError(null)
    try {
      const res = await fetch(`http://localhost:8000/topics/trader/${encodeURIComponent(traderId)}`)
      if (!res.ok) throw new Error(`HTTP ${res.status}`)
      const json = await res.json()
      setData(json)
    } catch (err: any) {
      setError(err.message)
    }
  }

  return (
    <main className="min-h-screen bg-gray-50 p-6">
      <h1 className="text-3xl font-bold mb-4">Topic Studio</h1>
      <div className="mb-4">
        <label className="block mb-2 text-sm font-medium">Trader ID</label>
        <input
          type="text"
          value={traderId}
          onChange={(e) => setTraderId(e.target.value)}
          className="w-full p-2 border rounded"
          placeholder="0x..."
        />
        <button
          onClick={fetchTopics}
          className="mt-2 px-4 py-2 bg-blue-600 text-white rounded"
        >
          Load Topics
        </button>
      </div>
      {error && <p className="text-red-600">{error}</p>}
      {data && (
        <div className="space-y-4">
          <div className="p-4 bg-white rounded shadow">
            <h2 className="text-lg font-medium mb-2">Trader Metrics</h2>
            <p><strong>Active Topics:</strong> {data.active_topics}</p>
            <p><strong>Entropy:</strong> {data.topic_entropy.toFixed(4)}</p>
            <p><strong>Niche Score:</strong> {data.niche_score.toFixed(4)}</p>
          </div>
          <div className="p-4 bg-white rounded shadow">
            <h2 className="text-lg font-medium mb-2">Topic Shares</h2>
            <table className="min-w-full text-sm">
              <thead className="bg-gray-100 text-gray-700">
                <tr>
                  <th className="px-4 py-2 text-left">Topic</th>
                  <th className="px-4 py-2 text-right">Share</th>
                </tr>
              </thead>
              <tbody>
                {data.topic_shares.map((ts) => (
                  <tr key={ts.topic} className="border-t">
                    <td className="px-4 py-2">{ts.topic}</td>
                    <td className="px-4 py-2 text-right">{(ts.share * 100).toFixed(2)}%</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </main>
  )
}