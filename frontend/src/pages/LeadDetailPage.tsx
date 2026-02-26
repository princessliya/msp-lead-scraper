import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { getLead, updateLeadNotes, deleteLead } from '../api/leads'
import type { Lead } from '../types/lead'
import Badge from '../components/ui/Badge'
import Spinner from '../components/ui/Spinner'
import { scoreColor, formatDate } from '../lib/formatters'

export default function LeadDetailPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const [lead, setLead] = useState<Lead | null>(null)
  const [loading, setLoading] = useState(true)
  const [notes, setNotes] = useState('')
  const [saving, setSaving] = useState(false)

  useEffect(() => {
    if (!id) return
    setLoading(true)
    getLead(Number(id))
      .then((l) => {
        setLead(l)
        setNotes(l.notes || '')
      })
      .catch(() => navigate('/leads'))
      .finally(() => setLoading(false))
  }, [id, navigate])

  const handleSaveNotes = async () => {
    if (!lead) return
    setSaving(true)
    try {
      const updated = await updateLeadNotes(lead.id, notes)
      setLead(updated)
    } finally {
      setSaving(false)
    }
  }

  const handleDelete = async () => {
    if (!lead || !confirm('Delete this lead?')) return
    await deleteLead(lead.id)
    navigate('/leads')
  }

  if (loading) {
    return <div className="flex items-center justify-center py-12"><Spinner /></div>
  }

  if (!lead) return null

  const bestEmail = lead.hunter_email || lead.apollo_email || lead.emails_found
  const techList = lead.tech_stack ? lead.tech_stack.split(',').map((t) => t.trim()).filter(Boolean) : []

  return (
    <div>
      <button onClick={() => navigate('/leads')} className="text-sm text-blue-600 hover:underline mb-4 inline-block">
        &larr; Back to Leads
      </button>

      <div className="flex items-start justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold">{lead.business_name}</h1>
          <p className="text-gray-500">{lead.category} &middot; {lead.address}</p>
        </div>
        <div className="flex items-center gap-3">
          <Badge className={scoreColor(lead.score) + ' text-lg px-4 py-1'}>{lead.score}</Badge>
          <button onClick={handleDelete} className="text-sm text-red-600 hover:underline">Delete</button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Contact Info */}
        <div className="bg-white rounded-xl border shadow-sm p-6">
          <h2 className="font-semibold mb-4">Contact Information</h2>
          <dl className="space-y-3 text-sm">
            <div className="flex justify-between">
              <dt className="text-gray-500">Phone</dt>
              <dd>{lead.phone || '-'}</dd>
            </div>
            <div className="flex justify-between">
              <dt className="text-gray-500">Website</dt>
              <dd>
                {lead.website ? (
                  <a href={lead.website} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline truncate max-w-[250px] inline-block">
                    {lead.domain || lead.website}
                  </a>
                ) : '-'}
              </dd>
            </div>
            <div className="flex justify-between">
              <dt className="text-gray-500">Best Email</dt>
              <dd className="text-right">{bestEmail || '-'}</dd>
            </div>
            {lead.hunter_email && (
              <div className="flex justify-between">
                <dt className="text-gray-500">Hunter.io</dt>
                <dd>{lead.hunter_email} ({lead.hunter_name}, {lead.hunter_confidence}%)</dd>
              </div>
            )}
            {lead.apollo_email && (
              <div className="flex justify-between">
                <dt className="text-gray-500">Apollo.io</dt>
                <dd>{lead.apollo_email} ({lead.apollo_name}, {lead.apollo_title})</dd>
              </div>
            )}
            <div className="flex justify-between">
              <dt className="text-gray-500">Scraped Emails</dt>
              <dd>{lead.emails_found || '-'}</dd>
            </div>
          </dl>
        </div>

        {/* Business Details */}
        <div className="bg-white rounded-xl border shadow-sm p-6">
          <h2 className="font-semibold mb-4">Business Details</h2>
          <dl className="space-y-3 text-sm">
            <div className="flex justify-between">
              <dt className="text-gray-500">Rating</dt>
              <dd>{lead.rating > 0 ? `${lead.rating} / 5 (${lead.reviews} reviews)` : '-'}</dd>
            </div>
            <div className="flex justify-between">
              <dt className="text-gray-500">Company Size</dt>
              <dd>{lead.company_size || '-'}</dd>
            </div>
            <div className="flex justify-between">
              <dt className="text-gray-500">Industry</dt>
              <dd>{lead.industry || '-'}</dd>
            </div>
            <div className="flex justify-between">
              <dt className="text-gray-500">SSL Valid</dt>
              <dd>{lead.ssl_valid ? 'Yes' : 'No'}</dd>
            </div>
            <div className="flex justify-between">
              <dt className="text-gray-500">IT Mention</dt>
              <dd>{lead.has_it_mention ? 'Yes' : 'No'}</dd>
            </div>
            <div className="flex justify-between">
              <dt className="text-gray-500">Existing MSP</dt>
              <dd>{lead.has_existing_msp ? 'Yes (lower priority)' : 'No'}</dd>
            </div>
            <div className="flex justify-between">
              <dt className="text-gray-500">Compliance Mention</dt>
              <dd>{lead.compliance_mention ? 'Yes' : 'No'}</dd>
            </div>
            <div className="flex justify-between">
              <dt className="text-gray-500">Scrape Status</dt>
              <dd>{lead.scrape_status}</dd>
            </div>
            <div className="flex justify-between">
              <dt className="text-gray-500">Added</dt>
              <dd>{formatDate(lead.created_at)}</dd>
            </div>
          </dl>
        </div>

        {/* Tech Stack */}
        <div className="bg-white rounded-xl border shadow-sm p-6">
          <h2 className="font-semibold mb-4">Tech Stack</h2>
          {techList.length > 0 ? (
            <div className="flex flex-wrap gap-2">
              {techList.map((tech) => (
                <Badge key={tech} className="bg-blue-50 text-blue-700">{tech}</Badge>
              ))}
            </div>
          ) : (
            <p className="text-gray-500 text-sm">No technology detected</p>
          )}
        </div>

        {/* Notes */}
        <div className="bg-white rounded-xl border shadow-sm p-6">
          <h2 className="font-semibold mb-4">Notes</h2>
          <textarea
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
            rows={4}
            className="w-full px-3 py-2 border rounded-lg text-sm focus:ring-2 focus:ring-blue-500 outline-none resize-none"
            placeholder="Add notes about this lead..."
          />
          <button
            onClick={handleSaveNotes}
            disabled={saving}
            className="mt-2 px-4 py-2 text-sm bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
          >
            {saving ? 'Saving...' : 'Save Notes'}
          </button>
        </div>
      </div>
    </div>
  )
}
