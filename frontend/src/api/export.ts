const BASE = '/api/export'

function getToken() {
  return localStorage.getItem('access_token') || ''
}

export function exportCSV(jobId?: number, minScore = 0) {
  const params = new URLSearchParams()
  if (jobId) params.set('job_id', String(jobId))
  if (minScore > 0) params.set('min_score', String(minScore))
  const url = `${BASE}/csv?${params.toString()}`
  const a = document.createElement('a')
  a.href = url
  a.download = 'leads.csv'
  // For auth we need a fetch approach
  fetch(url, { headers: { Authorization: `Bearer ${getToken()}` } })
    .then((r) => r.blob())
    .then((blob) => {
      const blobUrl = URL.createObjectURL(blob)
      a.href = blobUrl
      a.click()
      URL.revokeObjectURL(blobUrl)
    })
}

export function exportJSON(jobId?: number, minScore = 0) {
  const params = new URLSearchParams()
  if (jobId) params.set('job_id', String(jobId))
  if (minScore > 0) params.set('min_score', String(minScore))
  const url = `${BASE}/json?${params.toString()}`
  fetch(url, { headers: { Authorization: `Bearer ${getToken()}` } })
    .then((r) => r.blob())
    .then((blob) => {
      const blobUrl = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = blobUrl
      a.download = 'leads.json'
      a.click()
      URL.revokeObjectURL(blobUrl)
    })
}
