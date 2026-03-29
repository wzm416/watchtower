import { useEffect, useRef, useState } from 'react'
import { Navigate } from 'react-router-dom'
import { useAuth } from '../auth'

export function SignInPage() {
  const { token, setToken } = useAuth()
  const [err, setErr] = useState<string | null>(null)
  const mounted = useRef(false)

  useEffect(() => {
    mounted.current = true
    return () => {
      mounted.current = false
    }
  }, [])

  useEffect(() => {
    const clientId = import.meta.env.VITE_GOOGLE_CLIENT_ID
    if (!clientId) {
      setErr('Set VITE_GOOGLE_CLIENT_ID in web/.env for Sign in with Google.')
      return
    }

    const tryInit = () => {
      if (!mounted.current || !window.google?.accounts?.id) return false
      window.google.accounts.id.initialize({
        client_id: clientId,
        callback: (resp) => setToken(resp.credential),
        auto_select: false,
      })
      const el = document.getElementById('gsi-btn')
      if (el) {
        el.innerHTML = ''
        window.google.accounts.id.renderButton(el, {
          theme: 'filled_black',
          size: 'large',
          text: 'signin_with',
          shape: 'rectangular',
        })
      }
      return true
    }

    if (tryInit()) return

    const id = window.setInterval(() => {
      if (tryInit()) window.clearInterval(id)
    }, 100)

    return () => window.clearInterval(id)
  }, [setToken])

  if (token) return <Navigate to="/monitors" replace />

  return (
    <div className="signin">
      <div className="signin-card">
        <h1 className="signin-title">Watchtower</h1>
        <p className="signin-copy">
          Track merchandise prices on your schedule — email when something moves.
        </p>
        {err ? <p className="signin-err">{err}</p> : null}
        <div id="gsi-btn" className="gsi-wrap" />
      </div>
    </div>
  )
}
