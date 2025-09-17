import { useEffect, useState } from 'react'

interface ArchetypeItem {
  id: number
  name: string
  members: string[]
}

export default function ArchetypesPage() {
  const [items, setItems] = useState<ArchetypeItem[]>([])
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    async function fetchArchetypes() {
      try {
        const res = await fetch('http://localhost:8000/archetypes/map')
        if (!res.ok) throw new Error(`HTTP ${res.status}`)
        const json = await res.json()
        setItems(json.archetypes)
      } catch (err: any) {
        setError(err.message)
      }
    }
    fetchArchetypes()
  }, [])

  return (
    <main className="min-h-screen bg-gray-50 p-6">
      <h1 className="text-3xl font-bold mb-4">Archetypes</h1>
      {error && <p className="text-red-600">{error}</p>}
      {!error && (
        <div className="space-y-4">
          {items.map((archetype) => (
            <div key={archetype.id} className="p-4 bg-white rounded shadow">
              <h2 className="text-lg font-medium">{archetype.name}</h2>
              <p className="text-sm text-gray-600">{archetype.members.length} traders</p>
              <div className="mt-2 flex flex-wrap gap-2">
                {archetype.members.slice(0, 10).map((t) => (
                  <span key={t} className="px-2 py-1 bg-gray-200 text-xs font-mono rounded">{t}</span>
                ))}
                {archetype.members.length > 10 && (
                  <span className="px-2 py-1 bg-gray-300 text-xs rounded">…</span>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </main>
  )
}