import { useState } from 'react'

import { AccountStatus } from '@/components/AccountStatus'
import { Button } from '@/components/ui/button'
import { useAuth } from '@/lib/auth'
import { supabase } from '@/lib/supabase'

export function WorkspacePage() {
  const { session } = useAuth()
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState<string | null>(null)

  async function signOut() {
    setBusy(true)
    setError(null)
    try {
      const { error } = await supabase.auth.signOut()
      if (error) setError(error.message)
    } catch {
      setError('Unable to sign out. Please try again.')
    } finally {
      setBusy(false)
    }
  }

  return (
    <main className="mx-auto max-w-4xl px-6 py-12">
      <header className="flex flex-wrap items-center justify-between gap-4 border-b pb-6">
        <h1 className="text-xl font-semibold">Document Copilot</h1>
        <Button variant="outline" disabled={busy} onClick={signOut}>{busy ? 'Signing out…' : 'Sign out'}</Button>
      </header>
      <section className="py-12">
        <h2 className="text-2xl font-semibold">You’re signed in</h2>
        <p className="mt-2 break-all text-muted-foreground">{session?.user.email}</p>
        <AccountStatus key={session?.user.id} />
        {error && <p role="alert" className="mt-4 text-sm text-destructive">{error}</p>}
      </section>
    </main>
  )
}
