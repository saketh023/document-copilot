import { Navigate, Outlet } from 'react-router-dom'

import { useAuth } from '@/lib/auth'

export function ProtectedRoute() {
  const { session, loading } = useAuth()
  if (loading) return <p className="p-8 text-center" role="status">Restoring your session…</p>
  return session ? <Outlet /> : <Navigate to="/login" replace />
}
