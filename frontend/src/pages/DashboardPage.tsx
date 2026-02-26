import { useState } from 'react'
import { startScrape } from '../api/scrape'
import { useSSE } from '../hooks/useSSE'
import type { ScrapeJob } from '../types/scrape'
import Badge from '../components/ui/Badge'
import { scoreColor, statusColor } from '../lib/formatters'
import type { Lead } from '../types/lead'

const POPULAR_CATEGORIES = [
  'dental office', 'medical clinic', 'law firm', 'accounting firm',
  'insurance agency', 'veterinary clinic', 'chiropractic office',
  'real estate agency', 'auto dealership', 'pharmacy',
]

export default function DashboardPage() {
  const [category, setCategory] = useState('')
  const [location, setLocation] = useState('')
  const [useMock, setUseMock] = useState(false)
  const [activeJob, setActiveJob] = useState<ScrapeJob | null>(null)
  const [error, setError] = useState('')
  const [starting, setStarting] = useState(false)

  const { events, done, processedCount, totalFound } = useSSE(activeJob?.id ?? null)

  const handleStart = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!category.trim() || !location.trim()) return
    setError('')
    setStarting(true)
    try {
      const job = await startScrape({ category: category.trim(), location: location.trim(), use_mock: useMock })
      setActiveJob(job)
    } catch (err: unknown) {
      const msg = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail
      setError(msg || 'Failed to start scrape')
    } finally {
      setStarting(false)
    }
  }

  const isRunning = activeJob && !done
  const progress = totalFound > 0 ? Math.round((processedCount / totalFound) * 100) : 0

  // Collect leads from events
  const leads: Lead[] = events
    .filter((e) => e.type === 'lead_processed' && e.data.lead)
    .map((e) => e.data.lead as Lead)

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Dashboard</h1>

      {/* Search Form */}
      <div className="bg-white rounded-xl border shadow-sm p-6 mb-6">
        <h2 className="text-lg font-semibold mb-4">New Scrape</h2>
        <form onSubmit={handleStart} className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Business Category</label>
              <input
                type="text"
                value={category}
                onChange={(e) => setCategory(e.target.value)}
                placeholder="e.g., dental office"
                className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
                disabled={!!isRunning}
              />
              <div className="flex flex-wrap gap-1.5 mt-2">
                {POPULAR_CATEGORIES.map((c) => (
                  <button
                    key={c}
                    type="button"
                    onClick={() => setCategory(c)}
                    className="text-xs px-2 py-1 bg-gray-100 hover:bg-gray-200 rounded-md transition-colors"
                  >
                    {c}
                  </button>
                ))}
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Location</label>
              <input
                type="text"
                value={location}
                onChange={(e) => setLocation(e.target.value)}
                placeholder="e.g., Austin, TX"
                className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
                disabled={!!isRunning}
              />
            </div>
          </div>
          <div className="flex items-center gap-4">
            <label className="flex items-center gap-2 text-sm">
              <input
                type="checkbox"
                checked={useMock}
                onChange={(e) => setUseMock(e.target.checked)}
                className="rounded"
              />
              Use mock data (testing)
            </label>
          </div>
          {error && <div className="text-red-600 text-sm">{error}</div>}
          <button
            type="submit"
            disabled={starting || !!isRunning}
            className="bg-blue-600 text-white px-6 py-2.5 rounded-lg font-medium hover:bg-blue-700 disabled:opacity-50 transition-colors"
          >
            {starting ? 'Starting...' : isRunning ? 'Scraping...' : 'Start Scrape'}
          </button>
        </form>
      </div>

      {/* Progress */}
      {activeJob && (
        <div className="bg-white rounded-xl border shadow-sm p-6 mb-6">
          <div className="flex items-center justify-between mb-3">
            <h2 className="text-lg font-semibold">Progress</h2>
            <Badge className={statusColor(done ? 'completed' : 'running')}>
              {done ? 'Completed' : 'Running'}
            </Badge>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-3 mb-2">
            <div
              className="bg-blue-600 h-3 rounded-full transition-all duration-300"
              style={{ width: `${progress}%` }}
            />
          </div>
          <p className="text-sm text-gray-600">
            {processedCount} / {totalFound || '?'} leads processed
          </p>
          {events.length > 0 && (
            <p className="text-xs text-gray-400 mt-1">
              Latest: {events[events.length - 1].type}
            </p>
          )}
        </div>
      )}

      {/* Live Results */}
      {leads.length > 0 && (
        <div className="bg-white rounded-xl border shadow-sm p-6">
          <h2 className="text-lg font-semibold mb-4">Results ({leads.length} leads)</h2>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b text-left text-gray-500">
                  <th className="pb-2 pr-4">Score</th>
                  <th className="pb-2 pr-4">Business</th>
                  <th className="pb-2 pr-4">Category</th>
                  <th className="pb-2 pr-4">Email</th>
                  <th className="pb-2 pr-4">Phone</th>
                  <th className="pb-2">Rating</th>
                </tr>
              </thead>
              <tbody>
                {leads.map((lead, i) => (
                  <tr key={i} className="border-b last:border-0 hover:bg-gray-50">
                    <td className="py-2 pr-4">
                      <Badge className={scoreColor(lead.score)}>{lead.score}</Badge>
                    </td>
                    <td className="py-2 pr-4 font-medium">{lead.business_name}</td>
                    <td className="py-2 pr-4 text-gray-600">{lead.category}</td>
                    <td className="py-2 pr-4 text-gray-600">
                      {lead.hunter_email || lead.apollo_email || lead.emails_found || '-'}
                    </td>
                    <td className="py-2 pr-4 text-gray-600">{lead.phone || '-'}</td>
                    <td className="py-2">
                      {lead.rating > 0 ? `${lead.rating} (${lead.reviews})` : '-'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  )
}
