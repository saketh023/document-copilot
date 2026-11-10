import { useState, type FormEvent } from 'react'

import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { supabase } from '@/lib/supabase'

export function AuthForm({ signup }: { signup: boolean }) {
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [notice, setNotice] = useState<string | null>(null)

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    if (busy) return
    const form = event.currentTarget
    const values = new FormData(form)
    const email = String(values.get('email')).trim()
    const password = String(values.get('password'))
    setError(null)
    setNotice(null)
    if (signup && password !== values.get('confirmPassword')) {
      setError('Passwords do not match.')
      return
    }
    setBusy(true)
    try {
      const { data, error: authError } = signup
        ? await supabase.auth.signUp({
          email, password,
          options: { emailRedirectTo: `${window.location.origin}/login` },
        })
        : await supabase.auth.signInWithPassword({ email, password })
      if (authError) {
        setError(authError.message)
      } else if (signup && !data.session) {
        form.reset()
        setNotice('Check your inbox for a confirmation link. If you already have an account, sign in instead.')
      }
    } catch {
      setError('Unable to connect. Check your connection and try again.')
    } finally {
      setBusy(false)
    }
  }

  return (
    <form onSubmit={submit} className="space-y-5">
      <fieldset disabled={busy} className="space-y-5">
        <div className="space-y-2">
          <Label htmlFor="email">Email</Label>
          <Input id="email" name="email" type="email" autoComplete="email" placeholder="you@company.com" required />
        </div>
        <div className="space-y-2">
          <Label htmlFor="password">Password</Label>
          <Input id="password" name="password" type="password" autoComplete={signup ? 'new-password' : 'current-password'} minLength={signup ? 8 : undefined} required aria-describedby={signup ? 'password-help' : undefined} />
          {signup && <p id="password-help" className="text-xs text-muted-foreground">Use at least 8 characters.</p>}
        </div>
        {signup && <div className="space-y-2">
          <Label htmlFor="confirmPassword">Confirm password</Label>
          <Input id="confirmPassword" name="confirmPassword" type="password" autoComplete="new-password" minLength={8} required />
        </div>}
        {error && <p role="alert" className="text-sm text-destructive">{error}</p>}
        {notice && <p role="status" className="rounded-lg bg-muted p-3 text-sm">{notice}</p>}
        <Button type="submit" className="w-full" size="lg">
          {busy ? 'Please wait…' : signup ? 'Create account' : 'Sign in'}
        </Button>
      </fieldset>
    </form>
  )
}
