import { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import axios from 'axios'
import { MapPin, Clock, Briefcase, CheckCircle, AlertCircle, Upload } from 'lucide-react'
import { Zap } from 'lucide-react'

export default function PublicApply() {
    const { jobSlug } = useParams()
    const [job, setJob] = useState(null)
    const [loading, setLoading] = useState(true)
    const [submitting, setSubmitting] = useState(false)
    const [success, setSuccess] = useState(false)
    const [error, setError] = useState('')
    const [fileName, setFileName] = useState('')
    const [parsing, setParsing] = useState(false)
    const [parseSuccess, setParseSuccess] = useState(false)
    const [isDuplicate, setIsDuplicate] = useState(false)
    const [modalOpen, setModalOpen] = useState(false)
    const [modalData, setModalData] = useState(null)
    const { register, handleSubmit, setValue, formState: { errors } } = useForm()

    useEffect(() => {
        axios.get(`/api/jobs/public/${jobSlug}`)
            .then(r => setJob(r.data))
            .catch(() => setError('Job not found or no longer accepting applications.'))
            .finally(() => setLoading(false))
    }, [jobSlug])

    const handleFileChange = async (e) => {
        const file = e.target.files?.[0]
        if (!file) return
        setFileName(file.name)
        setParsing(true)
        setError('')
        setParseSuccess(false)
        setIsDuplicate(false)

        const formData = new FormData()
        formData.append('resume', file)

        try {
            const resp = await axios.post(`/api/apply/parse-resume?job_id=${job?.id || ''}`, formData, {
                headers: { 'Content-Type': 'multipart/form-data' }
            })
            const parsed = resp.data
            if (parsed) {
                if (parsed.is_duplicate) {
                    setIsDuplicate(true)
                    setError(parsed.duplicate_message || 'We have received your information already; you cannot apply for this position.')
                    setModalData({
                        title: 'Duplicate Application Detected',
                        message: 'Our records indicate you have already applied for this position with the email/phone specified below.',
                        type: 'error',
                        details: {
                            name: parsed.name || 'Candidate',
                            email: parsed.email || '',
                            phone: parsed.phone || ''
                        }
                    })
                    setModalOpen(true)
                } else {
                    setModalData({
                        title: 'Resume Processed Successfully!',
                        message: 'We scanned and found the following details. They have been pre-filled into the form for your review:',
                        type: 'success',
                        details: {
                            name: parsed.name && parsed.name !== 'Candidate' ? parsed.name : '',
                            email: parsed.email || '',
                            phone: parsed.phone || '',
                            linkedin: parsed.linkedin || '',
                            github: parsed.github || ''
                        }
                    })
                    setModalOpen(true)
                }
                if (parsed.name && parsed.name !== 'Candidate') setValue('name', parsed.name)
                if (parsed.email) setValue('email', parsed.email)
                if (parsed.phone) setValue('phone', parsed.phone)
                if (parsed.linkedin) setValue('linkedin', parsed.linkedin)
                if (parsed.github) setValue('github', parsed.github)
                if (!parsed.is_duplicate) {
                    setParseSuccess(true)
                }
            }
        } catch (err) {
            console.error('Failed to parse resume for autofill:', err)
        } finally {
            setParsing(false)
        }
    }

    const onSubmit = async (data) => {
        if (isDuplicate) {
            setError('We have your information already; you cannot apply for this position.')
            return
        }
        const fileInput = document.getElementById('resume-file')
        if (!fileInput?.files?.[0]) { setError('Please upload your resume.'); return }
        setSubmitting(true)
        setError('')
        const formData = new FormData()
        Object.entries(data).forEach(([k, v]) => formData.append(k, v || ''))
        formData.append('resume', fileInput.files[0])
        try {
            await axios.post(`/api/apply/${job.id}`, formData, { headers: { 'Content-Type': 'multipart/form-data' } })
            setSuccess(true)
        } catch (err) {
            const errMsg = err.response?.data?.detail
            if (errMsg && errMsg.includes('already')) {
                setIsDuplicate(true)
            }
            setError(errMsg || 'Submission failed. Please try again.')
        } finally {
            setSubmitting(false)
        }
    }

    if (loading) return (
        <div className="apply-page" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <div className="spinner-overlay">
                <div className="spinner-ring" />
                <span style={{ color: '#fff' }}>Loading job...</span>
            </div>
        </div>
    )

    return (
        <div className="apply-page">
            <div style={{ textAlign: 'center', marginBottom: 24 }}>
                <div style={{ display: 'inline-flex', alignItems: 'center', gap: 8, color: '#fff' }}>
                    <div style={{ width: 32, height: 32, background: 'rgba(255,255,255,0.15)', borderRadius: 8, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                        <Zap size={18} color="white" />
                    </div>
                    <span style={{ fontWeight: 700, fontSize: 18 }}>TalentFlow</span>
                </div>
            </div>

            {error && !job ? (
                <div className="apply-card" style={{ padding: 40, textAlign: 'center' }}>
                    <AlertCircle size={40} color="#dc2626" style={{ marginBottom: 16 }} />
                    <h2 style={{ fontSize: 20, fontWeight: 700, marginBottom: 8 }}>Job Not Found</h2>
                    <p style={{ color: '#64748b' }}>{error}</p>
                </div>
            ) : success ? (
                <div className="apply-card" style={{ padding: 40, textAlign: 'center' }}>
                    <CheckCircle size={48} color="#16a34a" style={{ marginBottom: 16 }} />
                    <h2 style={{ fontSize: 21, fontWeight: 700, marginBottom: 8 }}>Application Submitted! 🎉</h2>
                    <p style={{ color: '#64748b', fontSize: 14 }}>Your application has been received. We'll review it and get back to you.</p>
                </div>
            ) : job && (
                <div className="apply-card">
                    <div className="apply-card-header">
                        <div style={{ marginBottom: 8 }}>
                            <span style={{ fontSize: 12, opacity: 0.75, fontWeight: 500 }}>{job.company_name}</span>
                        </div>
                        <h1 style={{ fontSize: 22, fontWeight: 800, marginBottom: 10 }}>{job.title}</h1>
                        <div style={{ display: 'flex', gap: 16, flexWrap: 'wrap', opacity: 0.85, fontSize: 13 }}>
                            <span style={{ display: 'flex', alignItems: 'center', gap: 5 }}><MapPin size={13} />{job.location}</span>
                            <span style={{ display: 'flex', alignItems: 'center', gap: 5 }}><Clock size={13} />{job.experience}</span>
                            <span style={{ display: 'flex', alignItems: 'center', gap: 5 }}><Briefcase size={13} />{job.employment_type}</span>
                            {job.salary && <span>💰 {job.salary}</span>}
                        </div>
                    </div>

                    <div className="apply-card-body">
                        {error && <div className="alert-banner alert-error" style={{ marginBottom: 20 }}><AlertCircle size={16} />{error}</div>}

                        <div style={{ marginBottom: 24 }}>
                            <h3 style={{ fontSize: 16, fontWeight: 700, marginBottom: 16, color: 'var(--text-primary)' }}>About this role</h3>

                            {/* If structured sections exist, display them */}
                            {job.company_overview || job.role_summary || job.key_responsibilities ? (
                                <div style={{ fontSize: 14, color: 'var(--text-secondary)', lineHeight: 1.7, display: 'flex', flexDirection: 'column', gap: 16 }}>
                                    {job.company_overview && (
                                        <div>
                                            <h4 style={{ fontSize: 12.5, fontWeight: 700, color: 'var(--primary)', marginBottom: 4, textTransform: 'uppercase', letterSpacing: '0.5px' }}>Company Overview</h4>
                                            <p style={{ whiteSpace: 'pre-wrap', margin: 0, paddingLeft: 4 }}>{job.company_overview}</p>
                                        </div>
                                    )}
                                    {job.role_summary && (
                                        <div>
                                            <h4 style={{ fontSize: 12.5, fontWeight: 700, color: 'var(--primary)', marginBottom: 4, textTransform: 'uppercase', letterSpacing: '0.5px' }}>Role Summary</h4>
                                            <p style={{ whiteSpace: 'pre-wrap', margin: 0, paddingLeft: 4 }}>{job.role_summary}</p>
                                        </div>
                                    )}
                                    {job.key_responsibilities && (
                                        <div>
                                            <h4 style={{ fontSize: 12.5, fontWeight: 700, color: 'var(--primary)', marginBottom: 4, textTransform: 'uppercase', letterSpacing: '0.5px' }}>Key Responsibilities</h4>
                                            <p style={{ whiteSpace: 'pre-wrap', margin: 0, paddingLeft: 4 }}>{job.key_responsibilities}</p>
                                        </div>
                                    )}
                                    {job.required_qualifications && (
                                        <div>
                                            <h4 style={{ fontSize: 12.5, fontWeight: 700, color: 'var(--primary)', marginBottom: 4, textTransform: 'uppercase', letterSpacing: '0.5px' }}>Required Qualifications</h4>
                                            <p style={{ whiteSpace: 'pre-wrap', margin: 0, paddingLeft: 4 }}>{job.required_qualifications}</p>
                                        </div>
                                    )}
                                    {job.preferred_qualifications && (
                                        <div>
                                            <h4 style={{ fontSize: 12.5, fontWeight: 700, color: 'var(--primary)', marginBottom: 4, textTransform: 'uppercase', letterSpacing: '0.5px' }}>Preferred Qualifications</h4>
                                            <p style={{ whiteSpace: 'pre-wrap', margin: 0, paddingLeft: 4 }}>{job.preferred_qualifications}</p>
                                        </div>
                                    )}
                                    {job.skills_competencies && (
                                        <div>
                                            <h4 style={{ fontSize: 12.5, fontWeight: 700, color: 'var(--primary)', marginBottom: 4, textTransform: 'uppercase', letterSpacing: '0.5px' }}>Skills & Competencies</h4>
                                            <p style={{ whiteSpace: 'pre-wrap', margin: 0, paddingLeft: 4 }}>{job.skills_competencies}</p>
                                        </div>
                                    )}
                                    {job.work_environment && (
                                        <div>
                                            <h4 style={{ fontSize: 12.5, fontWeight: 700, color: 'var(--primary)', marginBottom: 4, textTransform: 'uppercase', letterSpacing: '0.5px' }}>Work Environment</h4>
                                            <p style={{ whiteSpace: 'pre-wrap', margin: 0, paddingLeft: 4 }}>{job.work_environment}</p>
                                        </div>
                                    )}
                                    {job.compensation_benefits && (
                                        <div>
                                            <h4 style={{ fontSize: 12.5, fontWeight: 700, color: 'var(--primary)', marginBottom: 4, textTransform: 'uppercase', letterSpacing: '0.5px' }}>Compensation & Benefits</h4>
                                            <p style={{ whiteSpace: 'pre-wrap', margin: 0, paddingLeft: 4 }}>{job.compensation_benefits}</p>
                                        </div>
                                    )}
                                    {job.career_growth && (
                                        <div>
                                            <h4 style={{ fontSize: 12.5, fontWeight: 700, color: 'var(--primary)', marginBottom: 4, textTransform: 'uppercase', letterSpacing: '0.5px' }}>Career Advancement & Growth</h4>
                                            <p style={{ whiteSpace: 'pre-wrap', margin: 0, paddingLeft: 4 }}>{job.career_growth}</p>
                                        </div>
                                    )}
                                </div>
                            ) : (
                                /* Fallback: display compiled description */
                                <p style={{ fontSize: 14, color: 'var(--text-secondary)', lineHeight: 1.7, whiteSpace: 'pre-wrap' }}>
                                    {job.job_description}
                                </p>
                            )}

                            <div style={{ marginTop: 24 }}>
                                <p style={{ fontSize: 12, fontWeight: 700, color: 'var(--text-muted)', marginBottom: 8, letterSpacing: '0.5px' }}>REQUIRED SKILLS</p>
                                <div>{(job.required_skills || []).map(s => <span key={s} className="skill-tag">{s}</span>)}</div>
                            </div>
                        </div>

                        <hr className="divider" />

                        <h3 style={{ fontSize: 16, fontWeight: 700, marginBottom: 20, color: 'var(--text-primary)' }}>Apply for this position</h3>

                        <form onSubmit={handleSubmit(onSubmit)}>
                            {/* Resume Upload at top */}
                            <div style={{ marginBottom: 24, padding: 20, border: '1.5px dashed var(--border)', borderRadius: 10, background: 'rgba(255, 255, 255, 0.02)' }}>
                                <label className="form-label-custom" style={{ fontWeight: 600, color: 'var(--text-primary)', marginBottom: 8 }}>Upload Resume * (PDF, DOCX, TXT)</label>
                                <label
                                    htmlFor="resume-file"
                                    style={{ display: 'flex', alignItems: 'center', gap: 10, padding: '12px 16px', border: '1.5px solid var(--border)', borderRadius: 8, cursor: 'pointer', background: 'rgba(255,255,255,0.04)', color: 'var(--text-secondary)', fontSize: 13, fontWeight: 500 }}
                                >
                                    <Upload size={16} style={{ color: 'var(--primary)' }} />
                                    {fileName || 'Click to choose file or drag here'}
                                </label>
                                <input
                                    id="resume-file"
                                    type="file"
                                    accept=".pdf,.docx,.txt"
                                    style={{ display: 'none' }}
                                    onChange={handleFileChange}
                                />
                                {parsing && (
                                    <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginTop: 10, color: 'var(--primary)', fontSize: 12.5, fontWeight: 500 }}>
                                        <div className="spinner-ring" style={{ width: 14, height: 14, borderWidth: 1.5, borderColor: 'var(--primary)', borderTopColor: 'transparent' }} />
                                        <span>✨ AI is parsing your resume for quick autofill...</span>
                                    </div>
                                )}
                                {parseSuccess && (
                                    <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginTop: 10, color: 'var(--success)', fontSize: 12.5, fontWeight: 500 }}>
                                        <CheckCircle size={14} />
                                        <span>🎉 Form autofilled from resume details! Please review.</span>
                                    </div>
                                )}
                            </div>

                            <div className="grid-2" style={{ marginBottom: 14 }}>
                                <div>
                                    <label className="form-label-custom">Full Name *</label>
                                    <input {...register('name', { required: 'Required' })} className="form-control-custom" placeholder="John Doe" />
                                    {errors.name && <p style={{ color: '#dc2626', fontSize: 12, marginTop: 4 }}>{errors.name.message}</p>}
                                </div>
                                <div>
                                    <label className="form-label-custom">Email Address *</label>
                                    <input {...register('email', { required: 'Required' })} type="email" className="form-control-custom" placeholder="john@example.com" />
                                    {errors.email && <p style={{ color: '#dc2626', fontSize: 12, marginTop: 4 }}>{errors.email.message}</p>}
                                </div>
                            </div>

                            <div className="grid-2" style={{ marginBottom: 14 }}>
                                <div>
                                    <label className="form-label-custom">Phone Number *</label>
                                    <input {...register('phone', { required: 'Required' })} className="form-control-custom" placeholder="+91 9876543210" />
                                    {errors.phone && <p style={{ color: '#dc2626', fontSize: 12, marginTop: 4 }}>{errors.phone.message}</p>}
                                </div>
                                <div>
                                    <label className="form-label-custom">LinkedIn Profile</label>
                                    <input {...register('linkedin')} className="form-control-custom" placeholder="https://linkedin.com/in/..." />
                                </div>
                            </div>

                            <div className="grid-2" style={{ marginBottom: 14 }}>
                                <div>
                                    <label className="form-label-custom">GitHub Profile</label>
                                    <input {...register('github')} className="form-control-custom" placeholder="https://github.com/..." />
                                </div>
                                <div>
                                    <label className="form-label-custom">Portfolio / Website</label>
                                    <input {...register('portfolio')} className="form-control-custom" placeholder="https://yoursite.com" />
                                </div>
                            </div>

                            <button
                                type="submit"
                                className="btn-primary-custom"
                                disabled={submitting || isDuplicate}
                                style={{ width: '100%', justifyContent: 'center', padding: '12px', fontSize: 14.5, borderRadius: 10 }}
                            >
                                {submitting ? 'Submitting Application...' : isDuplicate ? 'Already Applied' : '🚀 Submit Application'}
                            </button>
                        </form>
                    </div>
                </div>
            )}

            {/* Modal Popup for Resume Processing Details & Duplication Warnings */}
            {modalOpen && (
                <div style={{
                    position: 'fixed',
                    top: 0,
                    left: 0,
                    right: 0,
                    bottom: 0,
                    background: 'rgba(15, 23, 42, 0.4)',
                    backdropFilter: 'blur(8px)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    zIndex: 1000,
                    animation: 'fadeIn 0.2s ease-out'
                }}>
                    <div style={{
                        background: '#ffffff',
                        border: '1px solid var(--border)',
                        borderRadius: 16,
                        padding: 30,
                        maxWidth: 480,
                        width: '90%',
                        boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)',
                        animation: 'slideUp 0.3s ease-out'
                    }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 16 }}>
                            {modalData?.type === 'error' ? (
                                <AlertCircle size={28} color="#dc2626" />
                            ) : (
                                <CheckCircle size={28} color="#16a34a" />
                            )}
                            <h2 style={{ fontSize: 18, fontWeight: 700, margin: 0, color: 'var(--text-primary)' }}>
                                {modalData?.title}
                            </h2>
                        </div>

                        <p style={{ fontSize: 13.5, color: 'var(--text-secondary)', lineHeight: 1.6, marginBottom: 20 }}>
                            {modalData?.message}
                        </p>

                        {modalData?.details && (
                            <div style={{
                                background: 'rgba(0, 0, 0, 0.02)',
                                borderRadius: 10,
                                padding: 16,
                                border: '1.5px solid var(--border)',
                                marginBottom: 24,
                                display: 'flex',
                                flexDirection: 'column',
                                gap: 8
                            }}>
                                {Object.entries(modalData.details).map(([k, v]) => v && (
                                    <div key={k} style={{ fontSize: 13, display: 'flex', justifyContent: 'space-between' }}>
                                        <span style={{ fontWeight: 600, color: 'var(--text-muted)', textTransform: 'capitalize' }}>{k}:</span>
                                        <span style={{ color: 'var(--text-primary)', wordBreak: 'break-all', textAlign: 'right', marginLeft: 10 }}>{String(v)}</span>
                                    </div>
                                ))}
                            </div>
                        )}

                        <button
                            type="button"
                            onClick={() => setModalOpen(false)}
                            className="btn-primary-custom"
                            style={{ width: '100%', justifyContent: 'center', padding: '10px', fontSize: 14, borderRadius: 8 }}
                        >
                            {modalData?.type === 'error' ? 'OK, I Understand' : 'Confirm & Continue'}
                        </button>
                    </div>
                </div>
            )}
        </div>
    )
}
