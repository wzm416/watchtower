import {
  createContext,
  useCallback,
  useContext,
  useMemo,
  useState,
  type ReactNode,
} from 'react'

const STORAGE_KEY = 'watchtower_id_token'

type AuthCtx = {
  token: string | null
  setToken: (t: string | null) => void
  signOut: () => void
}

const Ctx = createContext<AuthCtx | null>(null)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [token, setTokenState] = useState<string | null>(() =>
    typeof localStorage !== 'undefined' ? localStorage.getItem(STORAGE_KEY) : null,
  )

  const setToken = useCallback((t: string | null) => {
    setTokenState(t)
    if (typeof localStorage === 'undefined') return
    if (t) localStorage.setItem(STORAGE_KEY, t)
    else localStorage.removeItem(STORAGE_KEY)
  }, [])

  const signOut = useCallback(() => {
    window.google?.accounts?.id?.disableAutoSelect()
    setToken(null)
  }, [setToken])

  const value = useMemo(
    () => ({ token, setToken, signOut }),
    [token, setToken, signOut],
  )

  return <Ctx.Provider value={value}>{children}</Ctx.Provider>
}

export function useAuth(): AuthCtx {
  const v = useContext(Ctx)
  if (!v) throw new Error('useAuth outside AuthProvider')
  return v
}
