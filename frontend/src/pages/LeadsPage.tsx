import { useEffect, useState, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { getLeads, bulkDeleteLeads } from '../api/leads'
import { exportCSV, exportJSON } from '../api/export'
import type { Lead, LeadFilters, LeadsResponse } from '../types/lead'
import Badge from '../components/ui/Badge'
import Spinner from '../components/ui/Spinner'
import Pagination from '../components/ui/Pagination'
import { scoreColor } from '../lib/formatters'

export default function LeadsPage() {
  const navigate = useNavigate()
  const [data, setData] = useState<LeadsResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [selected, setSelected] = useState<Set<number>>(new Set())
  const [filters, setFilters] = useState<LeadFilters>({
    page: 1,
    per_page: 50,
    sort_by: 'score',
    sort_dir: 'desc',
    min_score: 0,
    max_score: 100,
  })

  const fetchLeads = useCallback(async () => {
    setLoading(true)
    try {
      const res = await getLeads(filters)
      setData(res)
    } catch {
      // handle error
    } finally {
      setLoading(false)
    }
  }, [filters])

  useEffect(() => { fetchLeads() }, [fetchLeads])

  const toggleSelect = (id: number) => {
    setSelected((prev) => {
      const next = new Set(prev)
      if (next.has(id)) next.delete(id)
      else next.add(id)
      return next
    })
  }

  const toggleAll = () => {
    if (!data) return
    if (selected.size === data.leads.length) {
      setSelected(new Set())
    } else {
      setSelected(new Set(data.leads.map((l) => l.id)))
    }
  }

  const handleBulkDelete = async () => {
    if (selected.size === 0) return
    if (!confirm(`Delete ${selected.size} leads?`)) return
    await bulkDeleteLeads([...selected])
    setSelected(new Set())
    fetchLeads()
  }

  const updateFilter = (key: keyof LeadFilters, value: unknown) => {
    setFilters((prev) => ({ ...prev, [key]: value, page: 1 }))
  }

  const totalPages = data ? Math.ceil(data.total / (filters.per_page || 50)) : 0

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold">Leads</h1>
        <div className="flex gap-2">
          <button
            onClick={() => exportCSV(filters.job_id, filters.min_score)}
            className="px-3 py-1.5 text-sm border rounded-lg hover:bg-gray-50"
          >
            Export CSV
          </button>
          <button
            onClick={() => exportJSON(filters.job_id, filters.min_score)}
            className="px-3 py-1.5 text-sm border rounded-lg hover:bg-gray-50"
          >
            Export JSON
          </button>
          {selected.size > 0 && (
            <button
              onClick={handleBulkDelete}
              className="px-3 py-1.5 text-sm bg-red-600 text-white rounded-lg hover:bg-red-700"
            >
              Delete ({selected.size})
            </button>
          )}
        </div>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-xl border shadow-sm p-4 mb-4">
        <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
          <input
            type="text"
            placeholder="Search business..."
            value={filters.search || ''}
            onChange={(e) => updateFilter('search', e.target.value || undefined)}
            className="px-3 py-2 border rounded-lg text-sm focus:ring-2 focus:ring-blue-500 outline-none"
          />
          <input
            type="text"
            placeholder="Category"
            value={filters.category || ''}
            onChange={(e) => updateFilter('category', e.target.value || undefined)}
            className="px-3 py-2 border rounded-lg text-sm focus:ring-2 focus:ring-blue-500 outline-none"
          />
          <div className="flex gap-2 items-center">
            <label className="text-xs text-gray-500">Score</label>
            <input
              type="number"
              min={0}
              max={100}
              value={filters.min_score}
              onChange={(e) => updateFilter('min_score', Number(e.target.value))}
              className="w-16 px-2 py-2 border rounded-lg text-sm"
            />
            <span className="text-gray-400">-</span>
            <input
              type="number"
              min={0}
              max={100}
              value={filters.max_score}
              onChange={(e) => updateFilter('max_score', Number(e.target.value))}
              className="w-16 px-2 py-2 border rounded-lg text-sm"
            />
          </div>
          <select
            value={filters.has_email === true ? 'yes' : filters.has_email === false ? 'no' : ''}
            onChange={(e) =>
              updateFilter('has_email', e.target.value === 'yes' ? true : e.target.value === 'no' ? false : undefined)
            }
            className="px-3 py-2 border rounded-lg text-sm focus:ring-2 focus:ring-blue-500 outline-none"
          >
            <option value="">All emails</option>
            <option value="yes">Has email</option>
            <option value="no">No email</option>
          </select>
          <select
            value={`${filters.sort_by}-${filters.sort_dir}`}
            onChange={(e) => {
              const [sortBy, sortDir] = e.target.value.split('-')
              setFilters((prev) => ({ ...prev, sort_by: sortBy, sort_dir: sortDir, page: 1 }))
            }}
            className="px-3 py-2 border rounded-lg text-sm focus:ring-2 focus:ring-blue-500 outline-none"
          >
            <option value="score-desc">Score (high first)</option>
            <option value="score-asc">Score (low first)</option>
            <option value="business_name-asc">Name (A-Z)</option>
            <option value="rating-desc">Rating (high first)</option>
            <option value="reviews-desc">Reviews (most first)</option>
          </select>
        </div>
      </div>

      {/* Table */}
      <div className="bg-white rounded-xl border shadow-sm overflow-hidden">
        {loading ? (
          <div className="flex items-center justify-center py-12"><Spinner /></div>
        ) : !data || data.leads.length === 0 ? (
          <div className="text-center py-12 text-gray-500">No leads found. Run a scrape to get started.</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="bg-gray-50 border-b">
                <tr className="text-left text-gray-500">
                  <th className="p-3">
                    <input type="checkbox" checked={selected.size === data.leads.length && data.leads.length > 0} onChange={toggleAll} />
                  </th>
                  <th className="p-3">Score</th>
                  <th className="p-3">Business</th>
                  <th className="p-3">Category</th>
                  <th className="p-3">Email</th>
                  <th className="p-3">Phone</th>
                  <th className="p-3">Rating</th>
                  <th className="p-3">Tech</th>
                </tr>
              </thead>
              <tbody>
                {data.leads.map((lead: Lead) => (
                  <tr
                    key={lead.id}
                    className="border-b last:border-0 hover:bg-gray-50 cursor-pointer"
                    onClick={() => navigate(`/leads/${lead.id}`)}
                  >
                    <td className="p-3" onClick={(e) => e.stopPropagation()}>
                      <input type="checkbox" checked={selected.has(lead.id)} onChange={() => toggleSelect(lead.id)} />
                    </td>
                    <td className="p-3">
                      <Badge className={scoreColor(lead.score)}>{lead.score}</Badge>
                    </td>
                    <td className="p-3 font-medium">{lead.business_name}</td>
                    <td className="p-3 text-gray-600">{lead.category}</td>
                    <td className="p-3 text-gray-600 max-w-[200px] truncate">
                      {lead.hunter_email || lead.apollo_email || lead.emails_found || '-'}
                    </td>
                    <td className="p-3 text-gray-600">{lead.phone || '-'}</td>
                    <td className="p-3">
                      {lead.rating > 0 ? `${lead.rating} (${lead.reviews})` : '-'}
                    </td>
                    <td className="p-3 max-w-[150px] truncate text-gray-500">
                      {lead.tech_stack || '-'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {data && (
        <div className="flex items-center justify-between mt-4">
          <span className="text-sm text-gray-500">{data.total} total leads</span>
          <Pagination page={filters.page || 1} totalPages={totalPages} onPageChange={(p) => setFilters((prev) => ({ ...prev, page: p }))} />
        </div>
      )}
    </div>
  )
}
