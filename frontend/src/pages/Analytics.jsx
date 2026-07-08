import { useEffect, useState } from 'react'
import api from '../api/client'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, LineChart, Line, Legend } from 'recharts'

const COLORS = ['#2563eb', '#16a34a', '#d97706', '#dc2626', '#7c3aed', '#0284c7', '#9333ea', '#059669']

export default function Analytics() {
    const [data, setData] = useState(null)
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        api.get('/analytics').then(r => setData(r.data)).catch(console.error).finally(() => setLoading(false))
    }, [])

    if (loading) return <div className="spinner-overlay"><div className="spinner-ring" /><span>Loading analytics...</span></div>
    if (!data) return <div className="empty-state"><h4>No analytics data</h4></div>

    const { kpis, hiring_funnel, apps_per_job, top_skills, apps_by_month } = data
    const maxFunnel = hiring_funnel?.[0]?.count || 1

    return (
        <div>
            <div className="page-header">
                <div>
                    <h1>Analytics</h1>
                    <p>Recruitment performance at a glance</p>
                </div>
            </div>

            {/* KPIs */}
            <div className="grid-4" style={{ marginBottom: 28 }}>
                {[
                    { label: 'Total Applicants', value: kpis.total_applicants, icon: '👥' },
                    { label: 'Avg Match Score', value: `${kpis.avg_match_score}%`, icon: '🎯' },
                    { label: 'Shortlisted', value: kpis.shortlisted, icon: '📋' },
                    { label: 'Hired', value: kpis.hired, icon: '🏆' },
                ].map(({ label, value, icon }) => (
                    <div className="stat-card" key={label}>
                        <div className="stat-icon" style={{ background: '#f1f5f9' }}>{icon}</div>
                        <div className="stat-value">{value}</div>
                        <div className="stat-label">{label}</div>
                    </div>
                ))}
            </div>

            <div className="grid-2" style={{ marginBottom: 20 }}>
                {/* Hiring Funnel */}
                <div className="chart-card">
                    <div className="chart-title">🔽 Hiring Funnel</div>
                    {(hiring_funnel || []).map(item => (
                        <div className="hiring-funnel-item" key={item.stage}>
                            <div className="funnel-label">{item.stage}</div>
                            <div className="funnel-bar-wrapper">
                                <div className="funnel-bar-fill" style={{ width: `${(item.count / maxFunnel) * 100}%` }} />
                            </div>
                            <div className="funnel-count">{item.count}</div>
                        </div>
                    ))}
                </div>

                {/* Top Skills */}
                <div className="chart-card">
                    <div className="chart-title">🛠 Top Candidate Skills</div>
                    {top_skills && top_skills.length > 0 ? (
                        <ResponsiveContainer width="100%" height={200}>
                            <BarChart data={top_skills} layout="vertical" margin={{ top: 0, right: 20, left: 20, bottom: 0 }}>
                                <CartesianGrid strokeDasharray="3 3" horizontal={false} />
                                <XAxis type="number" tick={{ fontSize: 11 }} />
                                <YAxis dataKey="skill" type="category" tick={{ fontSize: 11 }} width={80} />
                                <Tooltip />
                                <Bar dataKey="count" fill="#2563eb" radius={[0, 4, 4, 0]} />
                            </BarChart>
                        </ResponsiveContainer>
                    ) : <div className="empty-state" style={{ padding: 20 }}><p>No skill data yet</p></div>}
                </div>
            </div>

            <div className="grid-2">
                {/* Applications per Job */}
                <div className="chart-card">
                    <div className="chart-title">💼 Applications per Job</div>
                    {apps_per_job && apps_per_job.length > 0 ? (
                        <ResponsiveContainer width="100%" height={200}>
                            <BarChart data={apps_per_job} margin={{ top: 0, right: 10, left: -10, bottom: 40 }}>
                                <CartesianGrid strokeDasharray="3 3" />
                                <XAxis dataKey="job_title" tick={{ fontSize: 10 }} angle={-25} textAnchor="end" />
                                <YAxis tick={{ fontSize: 11 }} />
                                <Tooltip />
                                <Bar dataKey="count" fill="#7c3aed" radius={[4, 4, 0, 0]} />
                            </BarChart>
                        </ResponsiveContainer>
                    ) : <div className="empty-state" style={{ padding: 20 }}><p>No data yet</p></div>}
                </div>

                {/* Applications by Month */}
                <div className="chart-card">
                    <div className="chart-title">📈 Applications Over Time</div>
                    {apps_by_month && apps_by_month.length > 0 ? (
                        <ResponsiveContainer width="100%" height={200}>
                            <LineChart data={apps_by_month} margin={{ top: 5, right: 10, left: -10, bottom: 0 }}>
                                <CartesianGrid strokeDasharray="3 3" />
                                <XAxis dataKey="month" tick={{ fontSize: 11 }} />
                                <YAxis tick={{ fontSize: 11 }} />
                                <Tooltip />
                                <Line type="monotone" dataKey="count" stroke="#16a34a" strokeWidth={2} dot={{ r: 4 }} />
                            </LineChart>
                        </ResponsiveContainer>
                    ) : <div className="empty-state" style={{ padding: 20 }}><p>No timeline data yet</p></div>}
                </div>
            </div>
        </div>
    )
}
