import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import api from '../api/client'
import { ChevronLeft, Mail, Phone, Linkedin, Github, Globe, Calendar, MessageSquare, Clock } from 'lucide-react'

const STATUS_OPTIONS = ['applied', 'shortlisted', 'interview_scheduled', 'rejected', 'offered', 'hired']

function Section({ title, children }) {
    return (
        <div className="card" style={{ padding: 24, marginBottom: 24 }}>
            <h3 style={{ fontSize: 15, fontWeight: 700, color: 'var(--text-primary)', marginBottom: 16, paddingBottom: 12, borderBottom: '1px solid var(--border)' }}>{title}</h3>
            {children}
        </div>
    )
}

export default function CandidateDetail() {
    const { id } = useParams()
    const navigate = useNavigate()
    const [app, setApp] = useState(null)
    const [loading, setLoading] = useState(true)
    const [questions, setQuestions] = useState([])
    const [questionsLoading, setQuestionsLoading] = useState(false)
    const [difficulty, setDifficulty] = useState('Medium')
    const [showInterview, setShowInterview] = useState(false)
    const [interviewForm, setInterviewForm] = useState({ date_time: '', meeting_link: '', interviewer: '' })
    const [statusLoading, setStatusLoading] = useState(false)
    const [interviewLoading, setInterviewLoading] = useState(false)
    const [toast, setToast] = useState('')
    const [showEmailModal, setShowEmailModal] = useState(false)
    const [pendingStatus, setPendingStatus] = useState('')
    const [sendEmail, setSendEmail] = useState(true)
    const [emailBody, setEmailBody] = useState('')

    // Interview Email Modal states
    const [showInterviewEmailModal, setShowInterviewEmailModal] = useState(false)
    const [sendInterviewEmail, setSendInterviewEmail] = useState(true)
    const [interviewEmailBody, setInterviewEmailBody] = useState('')

    useEffect(() => {
        api.get(`/applications/${id}`)
            .then(r => setApp(r.data))
            .catch(console.error)
            .finally(() => setLoading(false))
    }, [id])

    const showToast = (msg) => {
        setToast(msg)
        setTimeout(() => setToast(''), 3000)
    }

    const getDefaultEmailTemplate = (status, candidateName, jobTitle) => {
        const s = status.toLowerCase();
        const company = app?.company_name || 'TalentFlow Careers';

        if (s === 'shortlisted') {
            return `Hi ${candidateName},\n\nOur HR team reviewed your resume and we are excited to let you know that you have been shortlisted for the ${jobTitle} position!\n\nThe next step is a technical interview. We will schedule a virtual call with you shortly. Please keep an eye out for a scheduling invitation.\n\nBest regards,\n${company} Team`;
        }
        if (s === 'rejected') {
            return `Dear ${candidateName},\n\nThank you for your interest in the ${jobTitle} role and for taking the time to apply.\n\nAfter reviewing our applicant pool, we regret to inform you that we will not be moving forward with your application at this time.\n\nWe will keep your resume in our database for future opportunities. We wish you the very best in your job hunt.\n\nBest regards,\n${company} Team`;
        }
        if (s === 'offered' || s === 'offer') {
            return `Dear ${candidateName},\n\nWe are absolutely thrilled to extend an offer of employment to you for the position of ${jobTitle}! You are selected and your offer letter will be released soon.\n\nThe HR team will be emailing you the formal offer letter complete with compensation structure, benefits details, and start dates within the next 24 hours.\n\nBest regards,\n${company} Team`;
        }
        return `Hello ${candidateName},\n\nWe wanted to provide an update on your application for the ${jobTitle} position.\n\nYour candidate status has progressed to: ${status}.\n\nOur talent acquisition team will contact you shortly with the details and coordination for this round. Thank you!\n\nBest regards,\n${company} Team`;
    }

    const handleStatusClick = (newStatus) => {
        setPendingStatus(newStatus)
        setSendEmail(true)
        setEmailBody(getDefaultEmailTemplate(newStatus, app.name, app.job_title))
        setShowEmailModal(true)
    }

    const confirmUpdateStatus = async () => {
        setStatusLoading(true)
        try {
            await api.patch(`/applications/${id}/status`, {
                status: pendingStatus,
                send_email: sendEmail,
                email_body: sendEmail ? emailBody : null
            })
            setApp(prev => ({ ...prev, status: pendingStatus }))
            setShowEmailModal(false)
            showToast(`Status updated to ${pendingStatus}`)
        } catch (e) {
            showToast('Failed to update status')
        } finally {
            setStatusLoading(false)
        }
    }

    const loadQuestions = async () => {
        setQuestionsLoading(true)
        try {
            const resp = await api.get(`/applications/${id}/questions?difficulty=${difficulty}`)
            setQuestions(resp.data.questions || [])
        } catch (e) {
            showToast('Failed to generate questions')
        } finally {
            setQuestionsLoading(false)
        }
    }

    const getInterviewEmailTemplate = () => {
        const company = app?.company_name || 'TalentFlow Careers';
        return `Hi ${app?.name},\n\nWe are excited to invite you to an interview for the ${app?.job_title} position.\n\nDate & Time: ${interviewForm.date_time}\nInterviewer: ${interviewForm.interviewer}\nMeeting Link: ${interviewForm.meeting_link}\n\nPlease let us know if you need to reschedule or have any questions.\n\nBest regards,\n${company} Team`;
    }

    const promptInterviewEmail = () => {
        if (!interviewForm.date_time || !interviewForm.meeting_link || !interviewForm.interviewer) {
            showToast('Fill all interview fields')
            return
        }
        setInterviewEmailBody(getInterviewEmailTemplate())
        setSendInterviewEmail(true)
        setShowInterviewEmailModal(true)
    }

    const confirmScheduleInterview = async () => {
        setInterviewLoading(true)
        try {
            await api.post('/interviews', {
                application_id: id,
                ...interviewForm,
                send_email: sendInterviewEmail,
                email_body: sendInterviewEmail ? interviewEmailBody : null
            })
            setApp(prev => ({ ...prev, status: 'interview_scheduled' }))
            setShowInterview(false)
            setShowInterviewEmailModal(false)
            showToast('Interview scheduled! Email sent to candidate.')
        } catch (e) {
            showToast('Failed to schedule interview')
        } finally {
            setInterviewLoading(false)
        }
    }

    if (loading) return <div className="spinner-overlay"><div className="spinner-ring" /><span>Loading candidate...</span></div>
    if (!app) return <div className="empty-state"><h4>Candidate not found</h4></div>

    return (
        <div>
            {toast && <div className="alert-banner alert-info" style={{ position: 'fixed', top: 20, right: 20, zIndex: 999, minWidth: 250 }}>{toast}</div>}

            <button className="btn-ghost" onClick={() => navigate('/applicants')} style={{ marginBottom: 16 }}>
                <ChevronLeft size={16} /> Back
            </button>

            {/* Header */}
            <div className="candidate-detail-header">
                <div className="candidate-avatar">{app.name?.[0]?.toUpperCase()}</div>
                <div style={{ flex: 1 }}>
                    <h2 style={{ fontSize: 20, fontWeight: 700, color: 'var(--text-primary)', marginBottom: 4 }}>{app.name}</h2>
                    <div style={{ display: 'flex', gap: 16, flexWrap: 'wrap', marginBottom: 10 }}>
                        {app.email && <a href={`mailto:${app.email}`} style={{ display: 'flex', alignItems: 'center', gap: 5, fontSize: 13.5, color: 'var(--text-secondary)', textDecoration: 'none' }}><Mail size={13.5} />{app.email}</a>}
                        {app.phone && <span style={{ display: 'flex', alignItems: 'center', gap: 5, fontSize: 13.5, color: 'var(--text-secondary)' }}><Phone size={13.5} />{app.phone}</span>}
                        {app.linkedin && <a href={app.linkedin} target="_blank" rel="noopener noreferrer" style={{ display: 'flex', alignItems: 'center', gap: 5, fontSize: 13.5, color: 'var(--primary)' }}><Linkedin size={13.5} />LinkedIn</a>}
                        {app.github && <a href={app.github} target="_blank" rel="noopener noreferrer" style={{ display: 'flex', alignItems: 'center', gap: 5, fontSize: 13.5, color: 'var(--primary)' }}><Github size={13.5} />GitHub</a>}
                        {app.portfolio && <a href={app.portfolio} target="_blank" rel="noopener noreferrer" style={{ display: 'flex', alignItems: 'center', gap: 5, fontSize: 13.5, color: 'var(--primary)' }}><Globe size={13.5} />Portfolio</a>}
                    </div>
                    <div style={{ display: 'flex', gap: 10, flexWrap: 'wrap', alignItems: 'center' }}>
                        <span className={`status-badge badge-${app.status}`} style={{ fontSize: 12 }}>
                            {app.status?.replace('_', ' ').replace(/\b\w/g, c => c.toUpperCase())}
                        </span>
                        <span style={{ fontSize: 13, color: 'var(--text-muted)' }}>Applied for: <strong style={{ color: 'var(--text-primary)' }}>{app.job_title}</strong></span>
                        <span style={{ fontSize: 13, color: 'var(--text-muted)' }}>• {app.applied_at?.substring(0, 10)}</span>
                    </div>
                </div>
                <div style={{ textAlign: 'center', flexShrink: 0 }}>
                    <div style={{ fontSize: 36, fontWeight: 800, color: app.match_score >= 70 ? 'var(--success)' : app.match_score >= 45 ? 'var(--warning)' : 'var(--danger)' }}>
                        {app.match_score}
                    </div>
                    <div style={{ fontSize: 11, color: 'var(--text-muted)', fontWeight: 700, letterSpacing: '0.4px' }}>MATCH SCORE</div>
                </div>
            </div>

            {/* AI Summary */}
            {app.ai_summary && (
                <Section title="🤖 AI Summary">
                    <p style={{ fontSize: 14, color: 'var(--text-secondary)', lineHeight: 1.7 }}>{app.ai_summary}</p>
                    {app.match_explanation && <p style={{ fontSize: 13, color: 'var(--text-muted)', marginTop: 8, fontStyle: 'italic' }}>{app.match_explanation}</p>}
                </Section>
            )}

            {/* Skills Analysis */}
            <Section title="📊 Skills Analysis">
                <div className="grid-2">
                    <div>
                        <p style={{ fontSize: 12, fontWeight: 700, color: 'var(--text-muted)', marginBottom: 8, letterSpacing: '0.5px' }}>STRENGTHS</p>
                        <div>{(app.strengths || []).map(s => <span key={s} className="skill-tag strength">{s}</span>)}</div>
                        {(app.strengths || []).length === 0 && <p style={{ fontSize: 13.5, color: 'var(--text-muted)' }}>No strengths extracted</p>}
                    </div>
                    <div>
                        <p style={{ fontSize: 12, fontWeight: 700, color: 'var(--text-muted)', marginBottom: 8, letterSpacing: '0.5px' }}>MISSING SKILLS</p>
                        <div>{(app.missing_skills || []).map(s => <span key={s} className="skill-tag missing">{s}</span>)}</div>
                        {(app.missing_skills || []).length === 0 && <p style={{ fontSize: 13.5, color: 'var(--text-muted)' }}>No skill gaps detected</p>}
                    </div>
                </div>
                {(app.parsed_skills || []).length > 0 && (
                    <div style={{ marginTop: 16 }}>
                        <p style={{ fontSize: 12, fontWeight: 700, color: 'var(--text-muted)', marginBottom: 8, letterSpacing: '0.5px' }}>ALL EXTRACTED SKILLS</p>
                        <div>{app.parsed_skills.map(s => <span key={s} className="skill-tag">{s}</span>)}</div>
                    </div>
                )}
                {(app.career_path || []).length > 0 && (
                    <div style={{ marginTop: 16 }}>
                        <p style={{ fontSize: 12, fontWeight: 700, color: 'var(--text-muted)', marginBottom: 8, letterSpacing: '0.5px' }}>CAREER RECOMMENDATIONS</p>
                        <div>{app.career_path.map(c => <span key={c} className="skill-tag" style={{ background: 'rgba(6, 182, 212, 0.1)', color: 'var(--info)', borderColor: 'rgba(6, 182, 212, 0.2)' }}>🎯 {c}</span>)}</div>
                    </div>
                )}
            </Section>

            {/* Experience & Education */}
            <div className="grid-2" style={{ marginBottom: 24 }}>
                <Section title="💼 Experience">
                    <p style={{ fontSize: 14, color: 'var(--text-secondary)', lineHeight: 1.6 }}>{app.parsed_experience || 'Not extracted from resume'}</p>
                </Section>
                <Section title="🎓 Education">
                    <p style={{ fontSize: 14, color: 'var(--text-secondary)', lineHeight: 1.6 }}>{app.parsed_education || 'Not extracted from resume'}</p>
                </Section>
            </div>

            {/* Resume Link */}
            {app.resume_url && (
                <Section title="📄 Resume">
                    <a
                        href={`/api/applications/${id}/resume-preview?token=${localStorage.getItem('talentflow_token')}`}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="btn-primary-custom"
                        style={{ display: 'inline-flex' }}
                    >
                        View Resume
                    </a>
                </Section>
            )}

            {/* Interview Questions */}
            <Section title="❓ AI Interview Questions">
                <div style={{ display: 'flex', gap: 8, alignItems: 'center', marginBottom: 14 }}>
                    <select value={difficulty} onChange={e => setDifficulty(e.target.value)} className="form-control-custom" style={{ width: 140 }}>
                        {['Easy', 'Medium', 'Hard'].map(d => <option key={d}>{d}</option>)}
                    </select>
                    <button className="btn-primary-custom" onClick={loadQuestions} disabled={questionsLoading}>
                        {questionsLoading ? 'Generating...' : '✨ Generate Questions'}
                    </button>
                </div>
                {questions.length > 0 && (
                    <ol style={{ paddingLeft: 18 }}>
                        {questions.map((q, i) => (
                            <li key={i} style={{ fontSize: 14, color: 'var(--text-secondary)', marginBottom: 12, lineHeight: 1.6 }}>{q}</li>
                        ))}
                    </ol>
                )}
            </Section>

            {/* Status Update */}
            <Section title="📋 Update Status">
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
                    {(() => {
                        const rawRounds = app.hiring_rounds && app.hiring_rounds.length > 0
                            ? app.hiring_rounds
                            : ['shortlisted', 'interview_scheduled', 'offered', 'hired'];

                        const statusOptions = ['applied', ...rawRounds];
                        if (!statusOptions.some(x => x.toLowerCase() === 'rejected')) {
                            statusOptions.push('rejected');
                        }

                        return statusOptions.map(s => {
                            const isActive = app.status?.toLowerCase() === s.toLowerCase();
                            return (
                                <button
                                    key={s}
                                    onClick={() => handleStatusClick(s)}
                                    disabled={statusLoading || isActive}
                                    style={{
                                        padding: '8px 16px',
                                        borderRadius: '8px',
                                        border: isActive ? '1.5px solid var(--primary)' : '1.5px solid var(--border)',
                                        background: isActive ? 'var(--primary-glow)' : 'rgba(255, 255, 255, 0.02)',
                                        color: isActive ? '#a5b4fc' : 'var(--text-secondary)',
                                        fontWeight: isActive ? 700 : 500,
                                        fontSize: 13,
                                        cursor: isActive ? 'default' : 'pointer',
                                        transition: 'all 0.15s'
                                    }}
                                >
                                    {s.replace('_', ' ').replace(/\b\w/g, c => c.toUpperCase())}
                                </button>
                            );
                        });
                    })()}
                </div>
            </Section>

            {/* Schedule Interview */}
            <Section title="📅 Schedule Interview">
                {!showInterview ? (
                    <button className="btn-primary-custom" onClick={() => setShowInterview(true)}>
                        <Calendar size={15} /> Schedule Interview
                    </button>
                ) : (
                    <div>
                        <div className="grid-2" style={{ marginBottom: 12 }}>
                            <div>
                                <label className="form-label-custom">Date & Time</label>
                                <input
                                    type="datetime-local"
                                    value={interviewForm.date_time}
                                    onChange={e => setInterviewForm(p => ({ ...p, date_time: e.target.value }))}
                                    className="form-control-custom"
                                />
                            </div>
                            <div>
                                <label className="form-label-custom">Interviewer Name</label>
                                <input
                                    value={interviewForm.interviewer}
                                    onChange={e => setInterviewForm(p => ({ ...p, interviewer: e.target.value }))}
                                    className="form-control-custom"
                                    placeholder="e.g. John Doe - Engineering Lead"
                                />
                            </div>
                        </div>
                        <div style={{ marginBottom: 14 }}>
                            <label className="form-label-custom">Meeting Link</label>
                            <input
                                value={interviewForm.meeting_link}
                                onChange={e => setInterviewForm(p => ({ ...p, meeting_link: e.target.value }))}
                                className="form-control-custom"
                                placeholder="https://zoom.us/j/..."
                            />
                        </div>
                        <div style={{ display: 'flex', gap: 10 }}>
                            <button className="btn-primary-custom" onClick={promptInterviewEmail} disabled={interviewLoading}>
                                {interviewLoading ? 'Formatting...' : 'Generate Email Draft'}
                            </button>
                            <button className="btn-ghost" onClick={() => setShowInterview(false)}>Cancel</button>
                        </div>
                    </div>
                )}
            </Section>

            {showEmailModal && (
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
                            Update Status to: {pendingStatus.replace('_', ' ').replace(/\b\w/g, c => c.toUpperCase())}
                        </h3>
                        <p style={{ color: 'var(--text-secondary)', fontSize: 13.5, marginBottom: 18 }}>
                            Review and customize the update notification email to be sent to <strong>{app.name}</strong>.
                        </p>

                        <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 18 }}>
                            <input
                                id="send-email-checkbox"
                                type="checkbox"
                                checked={sendEmail}
                                onChange={e => setSendEmail(e.target.checked)}
                                style={{ width: 17, height: 17, cursor: 'pointer' }}
                            />
                            <label htmlFor="send-email-checkbox" style={{ fontSize: 14, fontWeight: 650, color: 'var(--text-primary)', cursor: 'pointer', userSelect: 'none' }}>
                                Send Email Notification
                            </label>
                        </div>

                        {sendEmail && (
                            <div style={{ marginBottom: 20 }}>
                                <label className="form-label-custom" style={{ marginBottom: 6 }}>Email Template Content (Editable)</label>
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
                                onClick={() => setShowEmailModal(false)}
                                style={{ padding: '8px 16px', fontSize: 13 }}
                            >
                                Cancel
                            </button>
                            <button
                                className="btn-primary-custom"
                                onClick={confirmUpdateStatus}
                                disabled={statusLoading}
                                style={{ padding: '8px 18px', fontSize: 13 }}
                            >
                                {statusLoading ? 'Updating...' : 'Confirm & Update'}
                            </button>
                        </div>
                    </div>
                </div>
            )}

            {/* Schedule Interview Email Modal */}
            {showInterviewEmailModal && (
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
                            Schedule Interview with {app.name}
                        </h3>
                        <p style={{ color: 'var(--text-secondary)', fontSize: 13.5, marginBottom: 18 }}>
                            Review and customize the scheduling invite email to be sent to <strong>{app.name}</strong>.
                        </p>

                        <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 18 }}>
                            <input
                                id="send-interview-checkbox"
                                type="checkbox"
                                checked={sendInterviewEmail}
                                onChange={e => setSendInterviewEmail(e.target.checked)}
                                style={{ width: 17, height: 17, cursor: 'pointer' }}
                            />
                            <label htmlFor="send-interview-checkbox" style={{ fontSize: 14, fontWeight: 650, color: 'var(--text-primary)', cursor: 'pointer', userSelect: 'none' }}>
                                Send Scheduling Invite Email
                            </label>
                        </div>

                        {sendInterviewEmail && (
                            <div style={{ marginBottom: 20 }}>
                                <label className="form-label-custom" style={{ marginBottom: 6 }}>Email Template Content (Editable)</label>
                                <textarea
                                    value={interviewEmailBody}
                                    onChange={e => setInterviewEmailBody(e.target.value)}
                                    className="form-control-custom"
                                    style={{ width: '100%', minHeight: 180, resize: 'vertical', fontSize: 13.5, lineHeight: 1.5, background: 'var(--bg-primary)' }}
                                />
                            </div>
                        )}

                        <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 10, borderTop: '1px solid var(--border)', paddingTop: 16 }}>
                            <button
                                className="btn-ghost"
                                onClick={() => setShowInterviewEmailModal(false)}
                                style={{ padding: '8px 16px', fontSize: 13 }}
                            >
                                Cancel
                            </button>
                            <button
                                className="btn-primary-custom"
                                onClick={confirmScheduleInterview}
                                disabled={interviewLoading}
                                style={{ padding: '8px 18px', fontSize: 13 }}
                            >
                                {interviewLoading ? 'Scheduling...' : 'Confirm & Schedule'}
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    )
}
