import { NavLink, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import {
    LayoutDashboard, Briefcase, Users, BarChart2,
    Settings, LogOut, Zap
} from 'lucide-react'

const navItems = [
    { label: 'Dashboard', icon: LayoutDashboard, to: '/dashboard' },
    { label: 'Jobs', icon: Briefcase, to: '/jobs' },
    { label: 'Applicants', icon: Users, to: '/applicants' },
    { label: 'Analytics', icon: BarChart2, to: '/analytics' },
]

export default function Sidebar() {
    const { user, logout } = useAuth()
    const navigate = useNavigate()

    const handleLogout = () => {
        logout()
        navigate('/login')
    }

    const initials = user?.company_name
        ? user.company_name.split(' ').map(w => w[0]).join('').slice(0, 2).toUpperCase()
        : 'HR'

    return (
        <aside className="sidebar">
            <div className="sidebar-logo">
                <div className="logo-icon">
                    <Zap size={18} color="white" />
                </div>
                <div>
                    <div className="logo-text">TalentFlow</div>
                </div>
                <span className="logo-badge">AI</span>
            </div>

            <nav className="sidebar-nav">
                <div className="sidebar-section-title">Main Menu</div>
                {navItems.map(({ label, icon: Icon, to }) => (
                    <NavLink
                        key={to}
                        to={to}
                        className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
                    >
                        <Icon size={17} />
                        {label}
                    </NavLink>
                ))}
                <div className="sidebar-section-title" style={{ marginTop: 12 }}>Account</div>
                <div className="nav-item" onClick={() => navigate('/settings')}>
                    <Settings size={17} />
                    Settings
                </div>
                <div className="nav-item" onClick={handleLogout} style={{ color: '#f87171' }}>
                    <LogOut size={17} />
                    Logout
                </div>
            </nav>

            <div className="sidebar-footer">
                <div className="sidebar-user">
                    <div className="avatar">{initials}</div>
                    <div className="user-info">
                        <div className="user-name">{user?.company_name || 'HR User'}</div>
                        <div className="user-role">{user?.email || ''}</div>
                    </div>
                </div>
            </div>
        </aside>
    )
}
