const base = () => (import.meta.env.VITE_API_URL || '').replace(/\/$/, '')

function authHeaders(token: string): HeadersInit {
  return {
    Authorization: `Bearer ${token}`,
    'Content-Type': 'application/json',
  }
}

export type Monitor = {
  id: string
  user_id: string
  label: string
  product_url: string
  css_selector: string | null
  schedule_cron: string
  timezone: string
  status: string
  target_price_minor: number | null
  last_price_minor: number | null
  last_currency: string | null
  next_run_at: string | null
  created_at: string
  updated_at: string
}

export async function listMonitors(token: string): Promise<Monitor[]> {
  const r = await fetch(`${base()}/api/v1/monitors`, {
    headers: authHeaders(token),
  })
  if (!r.ok) throw new Error(await r.text())
  return r.json()
}

export async function createMonitor(
  token: string,
  body: {
    label: string
    product_url: string
    css_selector?: string
    schedule_cron: string
    timezone: string
    target_price_minor?: number | null
  },
): Promise<Monitor> {
  const r = await fetch(`${base()}/api/v1/monitors`, {
    method: 'POST',
    headers: authHeaders(token),
    body: JSON.stringify(body),
  })
  if (!r.ok) throw new Error(await r.text())
  return r.json()
}

export async function deleteMonitor(token: string, id: string): Promise<void> {
  const r = await fetch(`${base()}/api/v1/monitors/${id}`, {
    method: 'DELETE',
    headers: { Authorization: `Bearer ${token}` },
  })
  if (!r.ok) throw new Error(await r.text())
}

export async function translateSchedule(
  token: string,
  text: string,
  timezone: string,
): Promise<{ cron: string; next_run_at: string; matched_natural_language: boolean }> {
  const r = await fetch(`${base()}/api/v1/schedule/translate`, {
    method: 'POST',
    headers: authHeaders(token),
    body: JSON.stringify({ text, timezone }),
  })
  if (!r.ok) throw new Error(await r.text())
  return r.json()
}
