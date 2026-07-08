import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import api from '../api/client'
import { Briefcase, Users, Calendar, Trophy, TrendingUp, Clock, ChevronRight } from 'lucide-react'

function StatCard({ icon, label, value, color, bgColor }) {
    return (
        <div className="stat-card">
            <div className="stat-icon" style={{ background: bgColor }}>
                <span style={{ fontSize: 20 }}>{icon}</span>
            </div>
            <div className="stat-value" style={{ color }}>{value}</div>
            <div className="stat-label">{label}</div>
        </div>
    )
}

export default function Dashboard() {
    const navigate = useNavigate()
    const [stats, setStats] = useState(null)
    const [recentApps, setRecentApps] = useState([])
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        Promise.all([
            api.get('/analytics'),
            api.get('/applications?sort_by=applied_at')
        ]).then(([analyticsResp, appsResp]) => {
            setStats(analyticsResp.data.kpis)
            setRecentApps((appsResp.data.applications || []).slice(0, 5))
        }).catch(console.error).finally(() => setLoading(false))
    }, [])

    if (loading) return <div className="spinner-overlay"><div className="spinner-ring" /><span>Loading Dashboard...</span></div>

    const kpis = stats || {}

    return (
        <div>
            <div className="page-header">
                <div>
                    <h1>Dashboard</h1>
                    <p>Your recruitment overview at a glance</p>
                </div>
                <button className="btn-primary-custom" onClick={() => navigate('/jobs/create')}>
                    + Post New Job
                </button>
            </div>

            {/* KPI Cards */}
            <div className="grid-4" style={{ marginBottom: 28 }}>
                <StatCard icon="💼" label="Total Jobs" value={kpis.total_jobs ?? 0} color="var(--primary)" bgColor="rgba(99, 102, 241, 0.1)" />
                <StatCard icon="✅" label="Active Jobs" value={kpis.active_jobs ?? 0} color="var(--success)" bgColor="rgba(16, 185, 129, 0.1)" />
                <StatCard icon="👥" label="Total Applicants" value={kpis.total_applicants ?? 0} color="var(--accent)" bgColor="rgba(168, 85, 247, 0.1)" />
                <StatCard icon="📅" label="Interviews" value={kpis.interviews_scheduled ?? 0} color="var(--warning)" bgColor="rgba(245, 158, 11, 0.1)" />
                <StatCard icon="📋" label="Shortlisted" value={kpis.shortlisted ?? 0} color="var(--info)" bgColor="rgba(6, 182, 212, 0.1)" />
                <StatCard icon="🎯" label="Avg Match Score" value={`${kpis.avg_match_score ?? 0}%`} color="var(--success)" bgColor="rgba(16, 185, 129, 0.1)" />
                <StatCard icon="🎁" label="Offers Sent" value={kpis.offers_sent ?? 0} color="var(--accent)" bgColor="rgba(168, 85, 247, 0.1)" />
                <StatCard icon="🏆" label="Hired" value={kpis.hired ?? 0} color="var(--success)" bgColor="rgba(16, 185, 129, 0.15)" />
            </div>

            {/* Recent Applications */}
            <div className="card" style={{ padding: 24 }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20 }}>
                    <h3 style={{ fontSize: 16, fontWeight: 700, color: 'var(--text-primary)' }}>Recent Applications</h3>
                    <button className="btn-ghost" onClick={() => navigate('/applicants')} style={{ fontSize: 12 }}>
                        View All <ChevronRight size={14} />
                    </button>
                </div>

                {recentApps.length === 0 ? (
                    <div className="empty-state" style={{ padding: '40px 20px' }}>
                        <div className="empty-state-icon">👥</div>
                        <h4>No applications yet</h4>
                        <p>Post a job and share the link for candidates to apply.</p>
                    </div>
                ) : (
                    <div className="table-wrapper">
                        <table className="custom-table">
                            <thead>
                                <tr>
                                    <th>Candidate</th>
                                    <th>Job Title</th>
                                    <th>Match Score</th>
                                    <th>Status</th>
                                    <th>Applied</th>
                                </tr>
                            </thead>
                            <tbody>
                                {recentApps.map(app => (
                                    <tr key={app._id} onClick={() => navigate(`/applicants/${app._id}`)}>
                                        <td>
                                            <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                                                <div style={{ width: 36, height: 36, borderRadius: '50%', background: 'linear-gradient(135deg, var(--primary), var(--accent))', display: 'flex', alignItems: 'center', justifycontent: 'center', color: '#fff', fontWeight: 700, fontSize: 13, flexShrink: 0, justifyContent: 'center' }}>
                                                    {app.name?.[0]?.toUpperCase() || '?'}
                                                </div>
                                                <div>
                                                    <div style={{ fontWeight: 600, fontSize: 14, color: 'var(--text-primary)' }}>{app.name}</div>
                                                    <div style={{ fontSize: 12, color: 'var(--text-muted)' }}>{app.email}</div>
                                                </div>
                                            </div>
                                        </td>
                                        <td style={{ fontSize: 13.5, color: 'var(--text-secondary)' }}>{app.job_title}</td>
                                        <td>
                                            <div className="score-bar">
                                                <div className="score-bar-track" style={{ width: 80 }}>
                                                    <div
                                                        className={`score-bar-fill ${app.match_score >= 70 ? 'high' : app.match_score >= 45 ? 'medium' : 'low'}`}
                                                        style={{ width: `${app.match_score}%` }}
                                                    />
                                                </div>
                                                <span className="score-text" style={{ color: app.match_score >= 70 ? 'var(--success)' : app.match_score >= 45 ? 'var(--warning)' : 'var(--danger)' }}>
                                                    {app.match_score}%
                                                </span>
                                            </div>
                                        </td>
                                        <td>
                                            <span className={`status-badge badge-${app.status}`}>
                                                {app.status?.replace('_', ' ').replace(/\b\w/g, c => c.toUpperCase())}
                                            </span>
                                        </td>
                                        <td style={{ fontSize: 13, color: 'var(--text-muted)' }}>{app.applied_at?.substring(0, 10)}</td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                )}
            </div>
        </div>
    )
}
