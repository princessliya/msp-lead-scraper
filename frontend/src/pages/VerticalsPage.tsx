import { useEffect, useState } from 'react'
import { getVerticals } from '../api/verticals'
import type { VerticalsResponse, Vertical } from '../types/vertical'
import Spinner from '../components/ui/Spinner'
import Badge from '../components/ui/Badge'
import { scoreColor } from '../lib/formatters'

export default function VerticalsPage() {
  const [data, setData] = useState<VerticalsResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [expandedSectors, setExpandedSectors] = useState<Set<string>>(new Set())

  useEffect(() => {
    getVerticals()
      .then((res) => {
        setData(res)
        // Expand all sectors by default
        setExpandedSectors(new Set(res.sectors))
      })
      .finally(() => setLoading(false))
  }, [])

  const toggleSector = (sector: string) => {
    setExpandedSectors((prev) => {
      const next = new Set(prev)
      if (next.has(sector)) next.delete(sector)
      else next.add(sector)
      return next
    })
  }

  if (loading) {
    return <div className="flex items-center justify-center py-12"><Spinner /></div>
  }

  if (!data) return null

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold">Verticals</h1>
          <p className="text-gray-500 text-sm mt-1">{data.total} verticals across {data.sectors.length} sectors</p>
        </div>
      </div>

      <div className="space-y-4">
        {data.sectors.map((sector) => {
          const verticals = data.verticals[sector] || []
          const isExpanded = expandedSectors.has(sector)

          return (
            <div key={sector} className="bg-white rounded-xl border shadow-sm overflow-hidden">
              <button
                onClick={() => toggleSector(sector)}
                className="w-full flex items-center justify-between p-4 hover:bg-gray-50 transition-colors"
              >
                <div className="flex items-center gap-3">
                  <h2 className="font-semibold">{sector}</h2>
                  <span className="text-sm text-gray-500">{verticals.length} verticals</span>
                </div>
                <svg
                  className={`w-5 h-5 text-gray-400 transition-transform ${isExpanded ? 'rotate-180' : ''}`}
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                </svg>
              </button>

              {isExpanded && (
                <div className="border-t">
                  <table className="w-full text-sm">
                    <thead className="bg-gray-50">
                      <tr className="text-left text-gray-500">
                        <th className="px-4 py-2">Vertical</th>
                        <th className="px-4 py-2">MSP Fit</th>
                        <th className="px-4 py-2">Why</th>
                      </tr>
                    </thead>
                    <tbody>
                      {verticals.map((v: Vertical) => (
                        <tr key={v.name} className="border-t hover:bg-gray-50">
                          <td className="px-4 py-3">
                            <span className="mr-2">{v.icon}</span>
                            {v.name}
                          </td>
                          <td className="px-4 py-3">
                            <Badge className={scoreColor(v.msp_fit)}>{v.msp_fit}</Badge>
                          </td>
                          <td className="px-4 py-3 text-gray-600">{v.reason}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          )
        })}
      </div>
    </div>
  )
}
