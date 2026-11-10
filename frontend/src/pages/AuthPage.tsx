import { useState } from 'react'
import { Link, Navigate } from 'react-router-dom'

import { AuthForm } from '@/components/AuthForm'
import { useAuth } from '@/lib/auth'

export function AuthPage({ signup = false }: { signup?: boolean }) {
  const { session, loading, error } = useAuth()
  const [confirmationError] = useState(() =>
    new URLSearchParams(window.location.hash.slice(1)).get('error_description')
    ?? new URLSearchParams(window.location.search).get('error_description'))
  if (loading) return <p className="p-8 text-center" role="status">Restoring your session…</p>
  if (session) return <Navigate to="/app" replace />

  return (
    <main className="flex min-h-svh items-center justify-center bg-muted/40 px-4 py-12">
      <section className="w-full max-w-md rounded-2xl border bg-card p-6 shadow-sm sm:p-8" aria-labelledby="auth-title">
        <p className="mb-8 text-sm font-semibold tracking-tight">Document Copilot</p>
        <h1 id="auth-title" className="text-2xl font-semibold tracking-tight">{signup ? 'Create your account' : 'Welcome back'}</h1>
        <p className="mb-7 mt-2 text-sm text-muted-foreground">{signup ? 'Start your research with answers you can trace to the source.' : 'Sign in to your research workspace.'}</p>
        {(error || confirmationError) && <p role="alert" className="mb-4 text-sm text-destructive">{error || confirmationError}</p>}
        <AuthForm key={signup ? 'signup' : 'login'} signup={signup} />
        <p className="mt-6 text-center text-sm text-muted-foreground">
          {signup ? 'Already have an account? ' : 'New to Document Copilot? '}
          <Link className="font-medium text-foreground underline underline-offset-4" to={signup ? '/login' : '/signup'}>{signup ? 'Sign in' : 'Create an account'}</Link>
        </p>
      </section>
    </main>
  )
}
