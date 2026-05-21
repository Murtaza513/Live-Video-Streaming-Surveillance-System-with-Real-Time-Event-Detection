/**
 * WebSocket client with automatic exponential-backoff reconnection.
 *
 * Usage:
 *   const client = createWsClient({ url, onOpen, onClose, onError, onMessage })
 *   // later...
 *   client.close()
 */

const BASE_DELAY_MS = 1_000
const MAX_DELAY_MS  = 30_000
const MAX_RETRIES   = 10

/**
 * @param {object}   opts
 * @param {string}   opts.url        – WebSocket server URL
 * @param {Function} opts.onOpen     – called when the connection opens
 * @param {Function} opts.onClose    – called when the connection closes
 * @param {Function} opts.onError    – called on socket error
 * @param {Function} opts.onMessage  – called with parsed JSON payload
 * @returns {{ close: Function, readyState: number }}
 */
export function createWsClient({ url, onOpen, onClose, onError, onMessage }) {
  let ws = null
  let retries = 0
  let intentionallyClosed = false

  function connect() {
    ws = new WebSocket(url)

    ws.onopen = () => {
      retries = 0
      onOpen?.()
    }

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        onMessage?.(data)
      } catch (err) {
        console.error('[wsClient] Failed to parse message:', err)
      }
    }

    ws.onerror = (err) => {
      console.error('[wsClient] Socket error:', err)
      onError?.(err)
    }

    ws.onclose = () => {
      onClose?.()
      if (!intentionallyClosed && retries < MAX_RETRIES) {
        // Exponential backoff capped at MAX_DELAY_MS
        const delay = Math.min(BASE_DELAY_MS * 2 ** retries, MAX_DELAY_MS)
        retries++
        console.warn(
          `[wsClient] Reconnecting in ${delay}ms (attempt ${retries}/${MAX_RETRIES})…`
        )
        setTimeout(connect, delay)
      }
    }
  }

  connect()

  return {
    close() {
      intentionallyClosed = true
      ws?.close()
    },
    get readyState() {
      return ws?.readyState ?? WebSocket.CLOSED
    },
  }
}
