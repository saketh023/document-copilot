import { useEffect, useState, type ReactNode } from 'react'
import type { Session } from '@supabase/supabase-js'

import { AuthContext } from '@/lib/auth'
import { supabase } from '@/lib/supabase'

export function AuthProvider({ children }: { children: ReactNode }) {
  const [session, setSession] = useState<Session | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let active = true
    let receivedEvent = false
    const { data: { subscription } } = supabase.auth.onAuthStateChange((_event, next) => {
      receivedEvent = true
      if (!active) return
      setSession(next)
      setLoading(false)
    })
    void supabase.auth.getSession().then(({ data, error: sessionError }) => {
      if (!active || receivedEvent) return
      setSession(data.session)
      setError(sessionError?.message ?? null)
      setLoading(false)
    }).catch(() => {
      if (!active || receivedEvent) return
      setError('Unable to restore your session. Please try signing in again.')
      setLoading(false)
    })
    return () => {
      active = false
      subscription.unsubscribe()
    }
  }, [])

  return <AuthContext.Provider value={{ session, loading, error }}>{children}</AuthContext.Provider>
}
