import { useEffect, useRef, useState } from 'react'
import type { ScrapeEvent } from '../types/scrape'

export function useSSE(jobId: number | null) {
  const [events, setEvents] = useState<ScrapeEvent[]>([])
  const [connected, setConnected] = useState(false)
  const [done, setDone] = useState(false)
  const esRef = useRef<EventSource | null>(null)

  useEffect(() => {
    if (!jobId) return

    const token = localStorage.getItem('access_token')
    const url = `/api/events/scrape/${jobId}?token=${token}`
    const es = new EventSource(url)
    esRef.current = es

    es.onopen = () => setConnected(true)

    es.onmessage = (e) => {
      try {
        const event: ScrapeEvent = JSON.parse(e.data)
        setEvents((prev) => [...prev, event])
        if (['completed', 'failed', 'cancelled'].includes(event.type)) {
          setDone(true)
          es.close()
        }
      } catch {
        // ignore parse errors
      }
    }

    es.onerror = () => {
      setConnected(false)
      es.close()
    }

    return () => {
      es.close()
      esRef.current = null
    }
  }, [jobId])

  const latestEvent = events.length > 0 ? events[events.length - 1] : null
  const processedCount = events.filter((e) => e.type === 'lead_processed').length
  const totalFound = (() => {
    const searchComplete = events.find((e) => e.type === 'search_complete')
    return (searchComplete?.data?.total as number) || 0
  })()

  return { events, latestEvent, connected, done, processedCount, totalFound }
}
