import Sidebar from './Sidebar'
import { Bell } from 'lucide-react'
import { useLocation } from 'react-router-dom'

const PAGE_TITLES = {
    '/dashboard': 'Dashboard',
    '/jobs': 'Job Management',
    '/applicants': 'Applicants',
    '/analytics': 'Analytics',
    '/settings': 'Settings',
}

export default function Layout({ children }) {
    const location = useLocation()
    const title = PAGE_TITLES[location.pathname] ||
        (location.pathname.startsWith('/jobs/create') ? 'Create Job' :
            location.pathname.startsWith('/applicants/') ? 'Candidate Details' : 'TalentFlow')

    return (
        <div style={{ display: 'flex', width: '100vw', minHeight: '100vh', overflowX: 'hidden' }}>
            <Sidebar />
            <div className="main-layout">
                <header className="topbar">
                    <div className="topbar-title">{title}</div>
                    <div className="topbar-actions">
                        <button className="btn-ghost" title="Notifications">
                            <Bell size={16} />
                        </button>
                    </div>
                </header>
                <main className="page-content">
                    {children}
                </main>
            </div>
        </div>
    )
}
