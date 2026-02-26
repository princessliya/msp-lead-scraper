export function formatDate(dateStr: string) {
  return new Date(dateStr).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

export function scoreColor(score: number): string {
  if (score >= 80) return 'text-green-600 bg-green-50'
  if (score >= 60) return 'text-yellow-600 bg-yellow-50'
  if (score >= 40) return 'text-orange-600 bg-orange-50'
  return 'text-red-600 bg-red-50'
}

export function statusColor(status: string): string {
  switch (status) {
    case 'completed': return 'text-green-700 bg-green-100'
    case 'running': return 'text-blue-700 bg-blue-100'
    case 'failed': return 'text-red-700 bg-red-100'
    case 'cancelled': return 'text-gray-700 bg-gray-100'
    default: return 'text-yellow-700 bg-yellow-100'
  }
}
