import { useEffect, useState, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { getScrapeHistory } from '../api/scrape'
import type { ScrapeJob } from '../types/scrape'
import Badge from '../components/ui/Badge'
import Spinner from '../components/ui/Spinner'
import Pagination from '../components/ui/Pagination'
import { formatDate, statusColor } from '../lib/formatters'

export default function HistoryPage() {
  const navigate = useNavigate()
  const [jobs, setJobs] = useState<ScrapeJob[]>([])
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(1)
  const [loading, setLoading] = useState(true)

  const fetch = useCallback(async () => {
    setLoading(true)
    try {
      const res = await getScrapeHistory(page, 20)
      setJobs(res.jobs)
      setTotal(res.total)
    } finally {
      setLoading(false)
    }
  }, [page])

  useEffect(() => { fetch() }, [fetch])

  const totalPages = Math.ceil(total / 20)

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Scrape History</h1>

      <div className="bg-white rounded-xl border shadow-sm overflow-hidden">
        {loading ? (
          <div className="flex items-center justify-center py-12"><Spinner /></div>
        ) : jobs.length === 0 ? (
          <div className="text-center py-12 text-gray-500">No scrape jobs yet. Start a scrape from the Dashboard.</div>
        ) : (
          <table className="w-full text-sm">
            <thead className="bg-gray-50 border-b">
              <tr className="text-left text-gray-500">
                <th className="p-3">Category</th>
                <th className="p-3">Location</th>
                <th className="p-3">Status</th>
                <th className="p-3">Leads</th>
                <th className="p-3">Started</th>
                <th className="p-3">Completed</th>
              </tr>
            </thead>
            <tbody>
              {jobs.map((job) => (
                <tr
                  key={job.id}
                  className="border-b last:border-0 hover:bg-gray-50 cursor-pointer"
                  onClick={() => navigate(`/leads?job_id=${job.id}`)}
                >
                  <td className="p-3 font-medium">{job.category}</td>
                  <td className="p-3 text-gray-600">{job.location}</td>
                  <td className="p-3">
                    <Badge className={statusColor(job.status)}>{job.status}</Badge>
                  </td>
                  <td className="p-3">{job.lead_count}</td>
                  <td className="p-3 text-gray-500">{formatDate(job.created_at)}</td>
                  <td className="p-3 text-gray-500">{job.completed_at ? formatDate(job.completed_at) : '-'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      <div className="flex items-center justify-between mt-4">
        <span className="text-sm text-gray-500">{total} total jobs</span>
        <Pagination page={page} totalPages={totalPages} onPageChange={setPage} />
      </div>
    </div>
  )
}
