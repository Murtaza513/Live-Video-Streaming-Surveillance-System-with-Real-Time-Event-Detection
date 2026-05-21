/**
 * REST API client for the surveillance backend.
 *
 * Base URL is read from the VITE_API_URL environment variable so it can be
 * overridden per environment without rebuilding.
 */

const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1'

/**
 * Fetch paginated event history.
 *
 * @param {object} params
 * @param {number} [params.page=1]
 * @param {number} [params.pageSize=50]
 * @param {string} [params.eventType]   – 'motion' | 'person' | undefined (all)
 * @returns {Promise<{ events: object[], total: number }>}
 */
export async function fetchEvents({ page = 1, pageSize = 50, eventType } = {}) {
  const qs = new URLSearchParams({ page, page_size: pageSize })
  if (eventType) qs.append('event_type', eventType)

  const res = await fetch(`${BASE_URL}/events?${qs}`)
  if (!res.ok) {
    throw new Error(`fetchEvents failed: ${res.status} ${res.statusText}`)
  }
  return res.json()
}
