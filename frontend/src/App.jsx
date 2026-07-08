import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider } from './context/AuthContext'
import ProtectedRoute from './components/ProtectedRoute'
import Layout from './components/Layout'
import Login from './pages/Login'
import Register from './pages/Register'
import Dashboard from './pages/Dashboard'
import Jobs from './pages/Jobs'
import CreateJob from './pages/CreateJob'
import Applicants from './pages/Applicants'
import CandidateDetail from './pages/CandidateDetail'
import Analytics from './pages/Analytics'
import PublicApply from './pages/PublicApply'
import Settings from './pages/Settings'

function ProtectedLayout({ children }) {
    return (
        <ProtectedRoute>
            <Layout>{children}</Layout>
        </ProtectedRoute>
    )
}

export default function App() {
    return (
        <AuthProvider>
            <BrowserRouter>
                <Routes>
                    {/* Public Routes */}
                    <Route path="/login" element={<Login />} />
                    <Route path="/register" element={<Register />} />
                    <Route path="/apply/:jobSlug" element={<PublicApply />} />

                    {/* Protected Routes */}
                    <Route path="/dashboard" element={<ProtectedLayout><Dashboard /></ProtectedLayout>} />
                    <Route path="/jobs" element={<ProtectedLayout><Jobs /></ProtectedLayout>} />
                    <Route path="/jobs/create" element={<ProtectedLayout><CreateJob /></ProtectedLayout>} />
                    <Route path="/jobs/edit/:id" element={<ProtectedLayout><CreateJob /></ProtectedLayout>} />
                    <Route path="/applicants" element={<ProtectedLayout><Applicants /></ProtectedLayout>} />
                    <Route path="/applicants/:id" element={<ProtectedLayout><CandidateDetail /></ProtectedLayout>} />
                    <Route path="/analytics" element={<ProtectedLayout><Analytics /></ProtectedLayout>} />
                    <Route path="/settings" element={<ProtectedLayout><Settings /></ProtectedLayout>} />

                    {/* Default */}
                    <Route path="/" element={<Navigate to="/dashboard" replace />} />
                    <Route path="*" element={<Navigate to="/dashboard" replace />} />
                </Routes>
            </BrowserRouter>
        </AuthProvider>
    )
}
