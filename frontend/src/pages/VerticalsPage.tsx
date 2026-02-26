import { useEffect, useState } from 'react'

import { getRecommendations, getVerticals } from '../api/verticals'
import Badge from '../components/ui/Badge'
import Spinner from '../components/ui/Spinner'
import type { RecommendationsResponse, VerticalRecommendation, VerticalsResponse } from '../types/vertical'

// ─── helpers ──────────────────────────────────────────────────────────────────

function scoreColor(score: number): 'green' | 'blue' | 'yellow' | 'gray' {
  if (score >= 85) return 'green'
  if (score >= 75) return 'blue'
  if (score >= 65) return 'yellow'
  return 'gray'
}

function densityBadgeClass(label: string): string {
  switch (label) {
    case 'Very High': return 'bg-green-100 text-green-700'
    case 'High':      return 'bg-blue-100 text-blue-700'
    case 'Medium':    return 'bg-yellow-100 text-yellow-700'
    case 'Low':       return 'bg-gray-100 text-gray-500'
    default:          return 'bg-gray-100 text-gray-400'
  }
}

function densityDots(label: string): number {
  switch (label) {
    case 'Very High': return 4
    case 'High':      return 3
    case 'Medium':    return 2
    case 'Low':       return 1
    default:          return 0
  }
}

// ─── Recommendation Card ──────────────────────────────────────────────────────

function RecommendationCard({
  rank,
  rec,
  hasApiKey,
}: {
  rank: number
  rec: VerticalRecommendation
  hasApiKey: boolean
}) {
  const dots = densityDots(rec.density_label)
  return (
    <div className="flex items-center gap-4 bg-white border rounded-xl px-5 py-4 shadow-sm hover:shadow-md transition-shadow">
      {/* Rank */}
      <span className="text-xl font-bold text-gray-200 w-7 text-right shrink-0">
        {rank}
      </span>

      {/* Icon */}
      <span className="text-2xl shrink-0">{rec.icon}</span>

      {/* Name + reason */}
      <div className="flex-1 min-w-0">
        <div className="font-semibold text-gray-900 capitalize">{rec.name}</div>
        <div className="text-xs text-gray-400 mt-0.5 truncate">
          {rec.sector} · {rec.reason}
        </div>
      </div>

      {/* MSP Fit */}
      <div className="text-center shrink-0">
        <div className="text-xs text-gray-400 mb-1">MSP Fit</div>
        <Badge color={scoreColor(rec.msp_fit)}>{rec.msp_fit}</Badge>
      </div>

      {/* Local density — only shown when we have real API data */}
      {hasApiKey && (
        <div className="text-center shrink-0">
          <div className="text-xs text-gray-400 mb-1">Local density</div>
          <span className={`text-xs font-medium px-2.5 py-1 rounded-full ${densityBadgeClass(rec.density_label)}`}>
            {'●'.repeat(dots)}{'○'.repeat(4 - dots)} {rec.density_label}
          </span>
          <div className="text-xs text-gray-400 mt-1">{rec.local_count} found</div>
        </div>
      )}
    </div>
  )
}

// ─── Main Page ────────────────────────────────────────────────────────────────

export default function VerticalsPage() {
  const [data, setData] = useState<VerticalsResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [expandedSectors, setExpandedSectors] = useState<Set<string>>(new Set())

  // Geo recommendations state
  const [locationInput, setLocationInput] = useState('')
  const [searchLoading, setSearchLoading] = useState(false)
  const [recs, setRecs] = useState<RecommendationsResponse | null>(null)
  const [searchError, setSearchError] = useState('')

  useEffect(() => {
    getVerticals()
      .then((d) => {
        setData(d)
        setExpandedSectors(new Set(d.sectors))
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

  const handleAnalyze = async (e: React.FormEvent) => {
    e.preventDefault()
    const loc = locationInput.trim()
    if (!loc) return
    setSearchLoading(true)
    setRecs(null)
    setSearchError('')
    try {
      const result = await getRecommendations(loc)
      setRecs(result)
    } catch {
      setSearchError('Could not load recommendations. Check your connection and try again.')
    } finally {
      setSearchLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Spinner size="lg" />
      </div>
    )
  }

  return (
    <div className="p-6 max-w-5xl mx-auto space-y-8">

      {/* Page header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Verticals</h1>
        <p className="text-gray-500 mt-1">
          {data?.total} industries across {data?.sectors.length} sectors · ranked by MSP fit
        </p>
      </div>

      {/* ── Market Intelligence search ── */}
      <div className="bg-gradient-to-br from-blue-50 to-indigo-50 border border-blue-100 rounded-xl p-6">
        <div className="flex items-start gap-3 mb-4">
          <span className="text-2xl">📍</span>
          <div>
            <h2 className="text-base font-semibold text-gray-900">Market Intelligence</h2>
            <p className="text-sm text-gray-500 mt-0.5">
              Enter any city to see which industries actually dominate there — so you know
              exactly which verticals to target first.
            </p>
          </div>
        </div>

        <form onSubmit={handleAnalyze} className="flex gap-3">
          <input
            type="text"
            value={locationInput}
            onChange={(e) => setLocationInput(e.target.value)}
            placeholder="e.g. Chicago, IL   ·   Miami, FL   ·   Houston, TX   ·   London, UK"
            className="flex-1 px-4 py-2.5 border border-blue-200 rounded-lg bg-white focus:ring-2 focus:ring-blue-400 focus:border-blue-400 outline-none text-sm"
          />
          <button
            type="submit"
            disabled={searchLoading || !locationInput.trim()}
            className="px-5 py-2.5 bg-blue-600 text-white rounded-lg font-medium text-sm hover:bg-blue-700 disabled:opacity-50 transition-colors flex items-center gap-2 shrink-0"
          >
            {searchLoading ? (
              <>
                <Spinner size="sm" />
                Analyzing…
              </>
            ) : (
              'Analyze Market →'
            )}
          </button>
        </form>

        {searchLoading && (
          <p className="text-xs text-blue-500 mt-2">
            Searching for real businesses across 9 industry categories — this takes ~10 seconds…
          </p>
        )}

        {searchError && (
          <p className="text-xs text-red-600 mt-2">{searchError}</p>
        )}
      </div>

      {/* ── Recommendations results ── */}
      {recs && (
        <div className="space-y-4">
          <div className="flex items-center justify-between flex-wrap gap-2">
            <h2 className="text-lg font-semibold text-gray-900">
              Top 10 for{' '}
              <span className="text-blue-600">{recs.location}</span>
            </h2>
            {!recs.has_api_key && (
              <span className="text-xs bg-yellow-100 text-yellow-700 border border-yellow-200 px-3 py-1 rounded-full">
                MSP fit only — add API key for local data
              </span>
            )}
          </div>

          {/* No API key notice */}
          {!recs.has_api_key && recs.message && (
            <div className="bg-yellow-50 border border-yellow-200 rounded-lg px-4 py-3 flex items-start gap-2 text-sm text-yellow-800">
              <span className="shrink-0">⚠️</span>
              <span>
                {recs.message}{' '}
                <a href="/settings" className="underline hover:no-underline font-medium">
                  Go to Settings →
                </a>
              </span>
            </div>
          )}

          {/* Recommendation cards */}
          <div className="grid gap-3">
            {recs.recommendations.map((rec, i) => (
              <RecommendationCard
                key={rec.name}
                rank={i + 1}
                rec={rec}
                hasApiKey={recs.has_api_key}
              />
            ))}
          </div>

          {recs.has_api_key && (
            <p className="text-xs text-gray-400 text-center pt-1">
              Score = MSP fit (0–100) + local density bonus (up to +10 pts) based on live
              search results for {recs.location}
            </p>
          )}
        </div>
      )}

      {/* ── All 68 Verticals accordion ── */}
      <div>
        <h2 className="text-lg font-semibold text-gray-900 mb-4">
          All {data?.total} Verticals
        </h2>
        <div className="space-y-3">
          {data?.sectors.map((sector) => {
            const verticals = data.verticals[sector] ?? []
            const isOpen = expandedSectors.has(sector)
            return (
              <div key={sector} className="border rounded-xl overflow-hidden bg-white shadow-sm">
                <button
                  onClick={() => toggleSector(sector)}
                  className="w-full flex items-center justify-between px-5 py-4 hover:bg-gray-50 transition-colors text-left"
                >
                  <span className="font-medium text-gray-900">
                    {sector}{' '}
                    <span className="text-sm text-gray-400 font-normal">
                      ({verticals.length})
                    </span>
                  </span>
                  <span className="text-gray-400 text-sm">{isOpen ? '▲' : '▼'}</span>
                </button>

                {isOpen && (
                  <div className="border-t overflow-x-auto">
                    <table className="w-full text-sm">
                      <thead className="bg-gray-50 text-xs text-gray-500 uppercase tracking-wider">
                        <tr>
                          <th className="px-5 py-3 text-left">Vertical</th>
                          <th className="px-5 py-3 text-left w-24">MSP Fit</th>
                          <th className="px-5 py-3 text-left">Why it works</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-gray-100">
                        {verticals.map((v) => (
                          <tr key={v.name} className="hover:bg-gray-50 transition-colors">
                            <td className="px-5 py-3 font-medium text-gray-900 capitalize">
                              {v.icon} {v.name}
                            </td>
                            <td className="px-5 py-3">
                              <Badge color={scoreColor(v.msp_fit)}>{v.msp_fit}</Badge>
                            </td>
                            <td className="px-5 py-3 text-gray-500">{v.reason}</td>
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
    </div>
  )
}
