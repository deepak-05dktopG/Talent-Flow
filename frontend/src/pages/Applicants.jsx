import { useEffect, useState } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import api from '../api/client'
import { Search, Filter, SortAsc } from 'lucide-react'

const STATUS_OPTIONS = ['', 'applied', 'shortlisted', 'interview_scheduled', 'rejected', 'offered', 'hired']
const SORT_OPTIONS = [
    { value: 'match_score', label: 'Match Score' },
    { value: 'applied_at', label: 'Date Applied' },
]

export default function Applicants() {
    const navigate = useNavigate()
    const [searchParams] = useSearchParams()
    const [apps, setApps] = useState([])
    const [loading, setLoading] = useState(true)
    const [search, setSearch] = useState('')
    const [statusFilter, setStatusFilter] = useState('')
    const [sortBy, setSortBy] = useState('match_score')

    // Bulk Selection States
    const [selectedAppIds, setSelectedAppIds] = useState([])
    const [jobs, setJobs] = useState([])
    const [selectedJobId, setSelectedJobId] = useState(searchParams.get('job') || '')
    const [minScore, setMinScore] = useState(0)

    // Modal States
    const [showBulkModal, setShowBulkModal] = useState(false)
    const [bulkStatus, setBulkStatus] = useState('shortlisted')
    const [sendEmail, setSendEmail] = useState(true)
    const [emailBody, setEmailBody] = useState('')
    const [bulkLoading, setBulkLoading] = useState(false)

    const jobId = searchParams.get('job')

    const fetchJobs = () => {
        api.get('/jobs')
            .then(r => setJobs(r.data.jobs || []))
            .catch(console.error)
    }

    const fetchApps = () => {
        setLoading(true)
        const params = new URLSearchParams()
        if (search) params.set('search', search)
        if (statusFilter) params.set('status', statusFilter)
        if (sortBy) params.set('sort_by', sortBy)

        const activeJobId = selectedJobId || jobId
        if (activeJobId) params.set('job_id', activeJobId)

        api.get(`/applications?${params.toString()}`)
            .then(r => setApps(r.data.applications || []))
            .catch(console.error)
            .finally(() => setLoading(false))
    }

    useEffect(() => {
        fetchJobs()
    }, [])

    useEffect(() => {
        fetchApps()
        // Reset selections when filters refresh
        setSelectedAppIds([])
    }, [search, statusFilter, sortBy, jobId, selectedJobId])

    // Filter applicants by match score client-side
    const filteredApps = apps.filter(app => app.match_score >= minScore)

    const getBulkStatusOptions = () => {
        const activeJobId = selectedJobId || jobId
        if (activeJobId) {
            const jobObj = jobs.find(j => j._id === activeJobId)
            if (jobObj && jobObj.hiring_rounds && jobObj.hiring_rounds.length > 0) {
                const options = ['Applied', ...jobObj.hiring_rounds]
                if (!options.some(o => o.toLowerCase() === 'rejected')) options.push('Rejected')
                if (!options.some(o => o.toLowerCase() === 'hired')) options.push('Hired')
                return options
            }
        }

        if (selectedAppIds.length > 0) {
            const selectedApps = apps.filter(a => selectedAppIds.includes(a._id))
            const firstJobId = selectedApps[0]?.job_id
            const allSame = selectedApps.every(a => a.job_id === firstJobId)
            if (allSame && firstJobId) {
                const jobObj = jobs.find(j => j._id === firstJobId)
                if (jobObj && jobObj.hiring_rounds && jobObj.hiring_rounds.length > 0) {
                    const options = ['Applied', ...jobObj.hiring_rounds]
                    if (!options.some(o => o.toLowerCase() === 'rejected')) options.push('Rejected')
                    if (!options.some(o => o.toLowerCase() === 'hired')) options.push('Hired')
                    return options
                }
            }
        }

        return ['Applied', 'Shortlisted', 'Technical Interview', 'HR Round', 'Offered', 'Hired', 'Rejected']
    }

    const getBulkEmailTemplate = (status) => {
        const s = status.toLowerCase();
        if (s === 'shortlisted') {
            return `Hi {name},\n\nOur HR team reviewed your resume and we are excited to let you know that you have been shortlisted for the {job_title} position!\n\nThe next step is a technical interview. We will schedule a virtual call with you shortly.\n\nBest regards,\nTalentFlow Careers`;
        }
        if (s === 'rejected') {
            return `Dear {name},\n\nThank you for your interest in the {job_title} role and for taking the time to apply.\n\nAfter reviewing our applicant pool, we regret to inform you that we will not be moving forward with your application at this time.\n\nBest regards,\nTalentFlow Careers`;
        }
        if (s === 'offered' || s === 'offer') {
            return `Dear {name},\n\nWe are absolutely thrilled to extend an offer of employment to you for the position of {job_title}! You are selected and your offer letter will be released soon.\n\nThe HR team will be emailing you the formal offer letter complete with compensation structure, benefits details, and start dates within the next 24 hours.\n\nBest regards,\nTalentFlow Careers`;
        }
        return `Hello {name},\n\nWe wanted to provide an update on your application for the {job_title} position.\n\nYour candidate status has progressed to: ${status}.\n\nOur talent acquisition team will contact you shortly with details. Thank you!\n\nBest regards,\nTalentFlow Careers`;
    }

    const handleBulkUpdateClick = () => {
        const opts = getBulkStatusOptions()
        const defaultStatus = opts.length > 0 ? opts[0] : 'Shortlisted'
        setBulkStatus(defaultStatus)
        setSendEmail(true)
        setEmailBody(getBulkEmailTemplate(defaultStatus))
        setShowBulkModal(true)
    }

    const handleModalStatusChange = (newStatusVal) => {
        setBulkStatus(newStatusVal)
        setEmailBody(getBulkEmailTemplate(newStatusVal))
    }

    const confirmBulkUpdate = async () => {
        setBulkLoading(true)
        try {
            await api.patch('/applications/bulk-status', {
                application_ids: selectedAppIds,
                status: bulkStatus,
                send_email: sendEmail,
                email_body: sendEmail ? emailBody : null
            })
            setShowBulkModal(false)
            setSelectedAppIds([])
            fetchApps()
            alert(`Successfully updated status for ${selectedAppIds.length} candidate(s)`)
        } catch (e) {
            console.error(e)
            alert(e.response?.data?.detail || 'Failed to update status in bulk_status')
        } finally {
            setBulkLoading(false)
        }
    }

    return (
        <div>
            <div className="page-header">
                <div>
                    <h1>Applicants</h1>
                    <p>{filteredApps.length} candidate{filteredApps.length !== 1 ? 's' : ''} found</p>
                </div>
            </div>

            {/* Filters */}
            <div style={{ display: 'flex', gap: 10, marginBottom: 20, flexWrap: 'wrap', alignItems: 'center' }}>
                <div className="search-bar" style={{ maxWidth: 280 }}>
                    <Search size={15} color="#94a3b8" />
                    <input
                        value={search}
                        onChange={e => setSearch(e.target.value)}
                        placeholder="Search by name, skill, job..."
                    />
                </div>

                <select
                    value={statusFilter}
                    onChange={e => setStatusFilter(e.target.value)}
                    className="form-control-custom"
                    style={{ width: 'auto', minWidth: 150 }}
                >
                    {STATUS_OPTIONS.map(s => (
                        <option key={s} value={s}>{s ? s.replace('_', ' ').replace(/\b\w/g, c => c.toUpperCase()) : 'All Statuses'}</option>
                    ))}
                </select>

                <select
                    value={selectedJobId}
                    onChange={e => {
                        setSelectedJobId(e.target.value)
                        setSelectedAppIds([])
                    }}
                    className="form-control-custom"
                    style={{ width: 'auto', minWidth: 165 }}
                >
                    <option value="">All Jobs</option>
                    {jobs.map(j => (
                        <option key={j._id} value={j._id}>{j.title}</option>
                    ))}
                </select>

                <select
                    value={sortBy}
                    onChange={e => setSortBy(e.target.value)}
                    className="form-control-custom"
                    style={{ width: 'auto', minWidth: 140 }}
                >
                    {SORT_OPTIONS.map(o => <option key={o.value} value={o.value}>{o.label}</option>)}
                </select>

                <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginLeft: 'auto' }}>
                    <label style={{ fontSize: 13, color: 'var(--text-muted)', fontWeight: 650 }}>Min ATS Score:</label>
                    <input
                        type="number"
                        min="0"
                        max="100"
                        value={minScore || ''}
                        onChange={e => setMinScore(Number(e.target.value) || 0)}
                        className="form-control-custom"
                        style={{ width: 80, placeholderColor: '#94a3b8', textAlign: 'center' }}
                    />
                </div>
            </div>

            {/* Bulk Actions Panel */}
            {selectedAppIds.length > 0 && (
                <div style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    padding: '14px 20px',
                    background: 'var(--primary-glow)',
                    border: '1.5px solid var(--primary)',
                    borderRadius: 12,
                    marginBottom: 16,
                    color: 'var(--text-primary)'
                }}>
                    <span style={{ fontSize: 14, fontWeight: 650 }}>
                        📋 Selected <strong>{selectedAppIds.length}</strong> candidate{selectedAppIds.length !== 1 ? 's' : ''} for bulk actions
                    </span>
                    <button
                        className="btn-primary-custom"
                        onClick={handleBulkUpdateClick}
                        style={{ padding: '8px 16px', fontSize: 13 }}
                    >
                        Bulk Update Status
                    </button>
                </div>
            )}

            {loading ? (
                <div className="spinner-overlay"><div className="spinner-ring" /><span>Loading applicants...</span></div>
            ) : filteredApps.length === 0 ? (
                <div className="card">
                    <div className="empty-state">
                        <div className="empty-state-icon">👥</div>
                        <h4>No applicants found</h4>
                        <p>Adjust your filters or share job links to receive applications.</p>
                    </div>
                </div>
            ) : (
                <div className="table-wrapper">
                    <table className="custom-table">
                        <thead>
                            <tr>
                                <th style={{ width: 40, textAlign: 'center' }}>
                                    <input
                                        type="checkbox"
                                        checked={filteredApps.length > 0 && selectedAppIds.length === filteredApps.length}
                                        onChange={() => {
                                            if (selectedAppIds.length === filteredApps.length) {
                                                setSelectedAppIds([])
                                            } else {
                                                setSelectedAppIds(filteredApps.map(a => a._id))
                                            }
                                        }}
                                        style={{ width: 16, height: 16, cursor: 'pointer' }}
                                    />
                                </th>
                                <th>Candidate</th>
                                <th>Job</th>
                                <th>Skills</th>
                                <th>Match Score</th>
                                <th>Status</th>
                                <th>Applied</th>
                            </tr>
                        </thead>
                        <tbody>
                            {filteredApps.map(app => (
                                <tr key={app._id} onClick={() => navigate(`/applicants/${app._id}`)}>
                                    <td onClick={e => e.stopPropagation()} style={{ textAlign: 'center' }}>
                                        <input
                                            type="checkbox"
                                            checked={selectedAppIds.includes(app._id)}
                                            onChange={() => {
                                                if (selectedAppIds.includes(app._id)) {
                                                    setSelectedAppIds(selectedAppIds.filter(id => id !== app._id))
                                                } else {
                                                    setSelectedAppIds([...selectedAppIds, app._id])
                                                }
                                            }}
                                            style={{ width: 16, height: 16, cursor: 'pointer' }}
                                        />
                                    </td>
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
                                        <div style={{ display: 'flex', flexWrap: 'wrap', gap: 4, maxWidth: 200 }}>
                                            {(app.parsed_skills || []).slice(0, 3).map(s => (
                                                <span key={s} className="skill-tag" style={{ fontSize: 11 }}>{s}</span>
                                            ))}
                                            {(app.parsed_skills || []).length > 3 && (
                                                <span className="skill-tag" style={{ background: 'rgba(255,255,255,0.05)', color: 'var(--text-secondary)', fontSize: 11 }}>+{app.parsed_skills.length - 3}</span>
                                            )}
                                        </div>
                                    </td>
                                    <td>
                                        <div className="score-bar">
                                            <div className="score-bar-track" style={{ width: 80 }}>
                                                <div
                                                    className={`score-bar-fill ${app.match_score >= 70 ? 'high' : app.match_score >= 45 ? 'medium' : 'low'}`}
                                                    style={{ width: `${app.match_score}%` }}
                                                />
                                            </div>
                                            <span className="score-text" style={{ color: app.match_score >= 70 ? 'var(--success)' : app.match_score >= 45 ? 'var(--warning)' : 'var(--danger)', fontSize: 12.5 }}>
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

            {/* Bulk Status Update Modal */}
            {showBulkModal && (
                <div style={{
                    position: 'fixed',
                    top: 0,
                    left: 0,
                    right: 0,
                    bottom: 0,
                    backgroundColor: 'rgba(15, 23, 42, 0.4)',
                    backdropFilter: 'blur(4px)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    zIndex: 1000
                }}>
                    <div className="card" style={{
                        padding: 30,
                        width: '90%',
                        maxWidth: 550,
                        boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.15), 0 10px 10px -5px rgba(0, 0, 0, 0.1)',
                        border: '1.5px solid var(--border)',
                        background: 'var(--card-bg)'
                    }}>
                        <h3 style={{ fontSize: 18, fontWeight: 700, marginBottom: 12, color: 'var(--text-primary)', borderBottom: '1px solid var(--border)', paddingBottom: 10 }}>
                            Bulk Update Status ({selectedAppIds.length} candidate{selectedAppIds.length !== 1 ? 's' : ''})
                        </h3>

                        <div style={{ marginBottom: 16 }}>
                            <label className="form-label-custom" style={{ marginBottom: 6 }}>Select New Status</label>
                            <select
                                value={bulkStatus}
                                onChange={e => handleModalStatusChange(e.target.value)}
                                className="form-control-custom"
                                style={{ width: '100%' }}
                            >
                                {getBulkStatusOptions().map(opt => (
                                    <option key={opt} value={opt}>
                                        {opt.replace('_', ' ').replace(/\b\w/g, c => c.toUpperCase())}
                                    </option>
                                ))}
                            </select>
                        </div>

                        <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 18 }}>
                            <input
                                id="bulk-send-email-checkbox"
                                type="checkbox"
                                checked={sendEmail}
                                onChange={e => setSendEmail(e.target.checked)}
                                style={{ width: 17, height: 17, cursor: 'pointer' }}
                            />
                            <label htmlFor="bulk-send-email-checkbox" style={{ fontSize: 14, fontWeight: 650, color: 'var(--text-primary)', cursor: 'pointer', userSelect: 'none' }}>
                                Send Individualized Email Notifications
                            </label>
                        </div>

                        {sendEmail && (
                            <div style={{ marginBottom: 20 }}>
                                <label className="form-label-custom" style={{ marginBottom: 6 }}>
                                    Email Template (Use {"{name}"} and {"{job_title}"} placeholders)
                                </label>
                                <textarea
                                    value={emailBody}
                                    onChange={e => setEmailBody(e.target.value)}
                                    className="form-control-custom"
                                    style={{ width: '100%', minHeight: 180, resize: 'vertical', fontSize: 13.5, lineHeight: 1.5, background: 'var(--bg-primary)' }}
                                />
                            </div>
                        )}

                        <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 10, borderTop: '1px solid var(--border)', paddingTop: 16 }}>
                            <button
                                className="btn-ghost"
                                onClick={() => setShowBulkModal(false)}
                                style={{ padding: '8px 16px', fontSize: 13 }}
                                disabled={bulkLoading}
                            >
                                Cancel
                            </button>
                            <button
                                className="btn-primary-custom"
                                onClick={confirmBulkUpdate}
                                disabled={bulkLoading}
                                style={{ padding: '8px 18px', fontSize: 13 }}
                            >
                                {bulkLoading ? 'Updating...' : `Confirm & Update ${selectedAppIds.length} Candidate(s)`}
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    )
}
