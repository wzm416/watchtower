import { Navigate, Route, Routes } from 'react-router-dom'
import { AuthProvider } from './auth'
import { MonitorsPage } from './pages/MonitorsPage'
import { SignInPage } from './pages/SignInPage'
import './App.css'

export default function App() {
  return (
    <AuthProvider>
      <Routes>
        <Route path="/" element={<SignInPage />} />
        <Route path="/monitors" element={<MonitorsPage />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </AuthProvider>
  )
}
