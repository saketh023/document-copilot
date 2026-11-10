import { useEffect, useState } from 'react'
import { Button } from '@/components/ui/button'
import { api, ApiError } from '@/lib/api'

type CurrentUser = {
  id: string
  email: string | null
  application_user_exists: boolean
}

export function AccountStatus() {
  const [account, setAccount] = useState<CurrentUser | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [unauthorized, setUnauthorized] = useState(false)
  const [attempt, setAttempt] = useState(0)

  useEffect(() => {
    const controller = new AbortController()
    void api.get<CurrentUser>('/auth/me', { signal: controller.signal }).then((user) => {
      if (!controller.signal.aborted) setAccount(user)
    }).catch((cause: unknown) => {
      if (controller.signal.aborted) return
      const expired = cause instanceof ApiError && cause.status === 401
      setUnauthorized(expired)
      setError(expired ? 'Your session could not be verified. Please sign out and sign in again.'
        : cause instanceof ApiError && cause.isNetworkError
          ? 'Unable to connect to the server. Please try again.'
          : 'Unable to verify your account. Please try again.')
    })
    return () => controller.abort()
  }, [attempt])

  function retry() {
    setAccount(null)
    setError(null)
    setUnauthorized(false)
    setAttempt(attempt + 1)
  }

  if (error) return (
    <div className="mt-6 space-y-3">
      <p role="alert" className="text-sm text-destructive">{error}</p>
      {!unauthorized && <Button variant="outline" onClick={retry}>Try again</Button>}
    </div>
  )
  if (!account) return <p role="status" className="mt-6 text-sm text-muted-foreground">Verifying your account…</p>
  if (!account.application_user_exists) return (
    <div className="mt-6 space-y-3">
      <p role="alert" className="text-sm text-destructive">Your sign-in is verified, but account setup is incomplete. Contact your administrator.</p>
      <Button variant="outline" onClick={retry}>Check again</Button>
    </div>
  )
  return (
    <div className="mt-6 space-y-2" role="status">
      <p className="text-sm font-medium">Your account is verified and ready.</p>
      <p className="text-sm text-muted-foreground">The chat workspace is coming next.</p>
    </div>
  )
}
