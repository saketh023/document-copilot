import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'

import { AuthProvider } from '@/components/AuthProvider'
import { ProtectedRoute } from '@/components/ProtectedRoute'
import { AuthPage } from '@/pages/AuthPage'
import { WorkspacePage } from '@/pages/WorkspacePage'

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          <Route path="/signup" element={<AuthPage signup />} />
          <Route path="/login" element={<AuthPage />} />
          <Route element={<ProtectedRoute />}>
            <Route path="/app" element={<WorkspacePage />} />
          </Route>
          <Route path="*" element={<Navigate to="/app" replace />} />
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  )
}
