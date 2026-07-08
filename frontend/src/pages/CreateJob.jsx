import { useState, useEffect } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import api from '../api/client'
import { ChevronLeft, Plus, X, CheckCircle } from 'lucide-react'

const SKILLS_SUGGESTIONS = ['Python', 'React', 'Node.js', 'FastAPI', 'MongoDB', 'PostgreSQL', 'Docker', 'AWS', 'Java', 'TypeScript', 'Vue', 'Angular', 'Django', 'Machine Learning']

export default function CreateJob() {
    const navigate = useNavigate()
    const { id } = useParams()
    const isEdit = !!id
    const { register, handleSubmit, reset, formState: { errors } } = useForm()
    const [skills, setSkills] = useState([])
    const [skillInput, setSkillInput] = useState('')
    const [rounds, setRounds] = useState(['Resume Screening', 'Phone Interview', 'Technical Interview', 'HR Round', 'Offer Release'])
    const [roundInput, setRoundInput] = useState('')
    const [loading, setLoading] = useState(false)
    const [success, setSuccess] = useState(false)
    const [error, setError] = useState('')

    useEffect(() => {
        if (isEdit) {
            setLoading(true)
            api.get(`/jobs/${id}`)
                .then(r => {
                    const job = r.data
                    reset(job)
                    setSkills(job.required_skills || [])
                    setRounds(job.hiring_rounds && job.hiring_rounds.length > 0 ? job.hiring_rounds : ['Resume Screening', 'Phone Interview', 'Technical Interview', 'HR Round', 'Offer Release'])
                })
                .catch(err => {
                    console.error(err)
                    setError('Failed to load job details')
                })
                .finally(() => setLoading(false))
        }
    }, [id, isEdit, reset])

    const addSkill = (skill) => {
        const trimmed = skill.trim()
        if (trimmed && !skills.includes(trimmed)) {
            setSkills([...skills, trimmed])
        }
        setSkillInput('')
    }

    const removeSkill = (skill) => setSkills(skills.filter(s => s !== skill))

    const addRound = () => {
        const trimmed = roundInput.trim()
        if (trimmed && !rounds.includes(trimmed)) {
            setRounds([...rounds, trimmed])
        }
        setRoundInput('')
    }

    const removeRound = (index) => {
        setRounds(rounds.filter((_, i) => i !== index))
    }

    const onSubmit = async (data) => {
        if (skills.length === 0) { setError('Add at least one required skill'); return }
        if (rounds.length === 0) { setError('Add at least one hiring round completely from initial round to offer release'); return }
        setLoading(true)
        setError('')
        try {
            if (isEdit) {
                await api.put(`/jobs/${id}`, { ...data, required_skills: skills, hiring_rounds: rounds })
            } else {
                await api.post('/jobs', { ...data, required_skills: skills, hiring_rounds: rounds })
            }
            setSuccess(true)
            setTimeout(() => navigate('/jobs'), 1500)
        } catch (err) {
            setError(err.response?.data?.detail || `Failed to ${isEdit ? 'update' : 'create'} job`)
        } finally {
            setLoading(false)
        }
    }

    return (
        <div style={{ maxWidth: 800, margin: '0 auto', paddingBottom: 40 }}>
            <div style={{ marginBottom: 24 }}>
                <button className="btn-ghost" onClick={() => navigate('/jobs')} style={{ marginBottom: 12 }}>
                    <ChevronLeft size={16} /> Back to Jobs
                </button>
                <h1 style={{ fontSize: 24, fontWeight: 800, color: 'var(--text-primary)', fontFamily: 'Outfit, sans-serif' }}>
                    {isEdit ? 'Edit Job Posting' : 'Post New Job'}
                </h1>
                <p style={{ fontSize: 14, color: 'var(--text-secondary)', marginTop: 4 }}>
                    {isEdit ? 'Modify the details of this job posting' : 'Fill in the details to create a public job posting'}
                </p>
            </div>

            {success && (
                <div className="alert-banner alert-success" style={{ marginBottom: 20 }}>
                    <CheckCircle size={16} /> {isEdit ? 'Job changes saved successfully! Redirecting...' : 'Job posted successfully! Redirecting...'}
                </div>
            )}
            {error && <div className="alert-banner alert-error" style={{ marginBottom: 20 }}>{error}</div>}

            <div className="card" style={{ padding: 28 }}>
                <form onSubmit={handleSubmit(onSubmit)}>
                    {/* Basic details */}
                    <div style={{ marginBottom: 28 }}>
                        <h4 style={{ fontSize: 15, fontWeight: 700, color: 'var(--text-primary)', marginBottom: 16, borderBottom: '1px solid var(--border)', paddingBottom: 8 }}>💼 Job Details</h4>

                        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16, marginBottom: 16 }}>
                            <div>
                                <label className="form-label-custom">Job Title *</label>
                                <input
                                    {...register('title', { required: true })}
                                    className="form-control-custom"
                                    placeholder="e.g. Senior Backend Engineer"
                                />
                                {errors.title && <span style={{ color: 'red', fontSize: 12 }}>Title is required</span>}
                            </div>
                            <div>
                                <label className="form-label-custom">Department *</label>
                                <input
                                    {...register('department', { required: true })}
                                    className="form-control-custom"
                                    placeholder="e.g. Engineering"
                                />
                                {errors.department && <span style={{ color: 'red', fontSize: 12 }}>Department is required</span>}
                            </div>
                        </div>

                        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: 16, marginBottom: 16 }}>
                            <div>
                                <label className="form-label-custom">Experience Level *</label>
                                <select {...register('experience', { required: true })} className="form-control-custom">
                                    <option value="">Select Level</option>
                                    <option value="Entry Level">Entry Level</option>
                                    <option value="Mid Level">Mid Level</option>
                                    <option value="Senior Level">Senior Level</option>
                                    <option value="Lead / Management">Lead / Management</option>
                                </select>
                            </div>
                            <div>
                                <label className="form-label-custom">Location *</label>
                                <input
                                    {...register('location', { required: true })}
                                    className="form-control-custom"
                                    placeholder="e.g. Remote / Bangalore"
                                />
                            </div>
                            <div>
                                <label className="form-label-custom">Employment Type *</label>
                                <select {...register('employment_type', { required: true })} className="form-control-custom">
                                    <option value="">Select Type</option>
                                    <option value="Full-time">Full-time</option>
                                    <option value="Part-time">Part-time</option>
                                    <option value="Contract">Contract</option>
                                    <option value="Internship">Internship</option>
                                </select>
                            </div>
                        </div>

                        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
                            <div>
                                <label className="form-label-custom">Salary Range (Optional)</label>
                                <input
                                    {...register('salary')}
                                    className="form-control-custom"
                                    placeholder="e.g. $120,000 - $150,000"
                                />
                            </div>
                            <div>
                                <label className="form-label-custom">Application Deadline *</label>
                                <input
                                    type="date"
                                    {...register('deadline', { required: true })}
                                    className="form-control-custom"
                                />
                            </div>
                        </div>
                    </div>

                    {/* Split optional inputs */}
                    <div style={{ marginBottom: 28 }}>
                        <h4 style={{ fontSize: 15, fontWeight: 700, color: 'var(--text-primary)', marginBottom: 16, borderBottom: '1px solid var(--border)', paddingBottom: 8 }}>📝 Job Description Details (Optional)</h4>

                        <div style={{ marginBottom: 16 }}>
                            <label className="form-label-custom">Company Overview (Optional)</label>
                            <textarea
                                {...register('company_overview')}
                                className="form-control-custom"
                                placeholder="Describe your company culture and mission..."
                                style={{ minHeight: 80 }}
                            />
                        </div>
                        <div style={{ marginBottom: 16 }}>
                            <label className="form-label-custom">Role Summary (Optional)</label>
                            <textarea
                                {...register('role_summary')}
                                className="form-control-custom"
                                placeholder="Summarize the core purpose of this role..."
                                style={{ minHeight: 80 }}
                            />
                        </div>
                        <div style={{ marginBottom: 16 }}>
                            <label className="form-label-custom">Key Responsibilities (Optional)</label>
                            <textarea
                                {...register('key_responsibilities')}
                                className="form-control-custom"
                                placeholder="List primary duties and responsibilities..."
                                style={{ minHeight: 100 }}
                            />
                        </div>

                        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16, marginBottom: 16 }}>
                            <div>
                                <label className="form-label-custom">Required Qualifications (Optional)</label>
                                <textarea
                                    {...register('required_qualifications')}
                                    className="form-control-custom"
                                    placeholder="Degrees, certifications, or minimum years of experience..."
                                    style={{ minHeight: 100 }}
                                />
                            </div>
                            <div>
                                <label className="form-label-custom">Preferred Qualifications (Optional)</label>
                                <textarea
                                    {...register('preferred_qualifications')}
                                    className="form-control-custom"
                                    placeholder="Desired but not strictly required skills/experience..."
                                    style={{ minHeight: 100 }}
                                />
                            </div>
                        </div>

                        <div style={{ marginBottom: 16 }}>
                            <label className="form-label-custom">Skills & Competencies (Optional)</label>
                            <textarea
                                {...register('skills_competencies')}
                                className="form-control-custom"
                                placeholder="Soft skills, team fit qualities, work styles..."
                                style={{ minHeight: 80 }}
                            />
                        </div>

                        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16, marginBottom: 16 }}>
                            <div>
                                <label className="form-label-custom">Work Environment (Optional)</label>
                                <textarea
                                    {...register('work_environment')}
                                    className="form-control-custom"
                                    placeholder="Hybrid schedule pattern, physical demands..."
                                    style={{ minHeight: 80 }}
                                />
                            </div>
                            <div>
                                <label className="form-label-custom">Compensation & Benefits (Optional)</label>
                                <textarea
                                    {...register('compensation_benefits')}
                                    className="form-control-custom"
                                    placeholder="Equity, insurance, remote work allowance, wellness programs..."
                                    style={{ minHeight: 80 }}
                                />
                            </div>
                        </div>

                        <div style={{ display: 'grid', gridTemplateColumns: '1fr', gap: 16 }}>
                            <div>
                                <label className="form-label-custom">Career Growth & Progression (Optional)</label>
                                <textarea
                                    {...register('career_growth')}
                                    className="form-control-custom"
                                    placeholder="Promotion pathways, learning resources..."
                                    style={{ minHeight: 80 }}
                                />
                            </div>
                        </div>
                    </div>

                    {/* Required Skills */}
                    <div style={{ marginBottom: 28 }}>
                        <h4 style={{ fontSize: 15, fontWeight: 700, color: 'var(--text-primary)', marginBottom: 16, borderBottom: '1px solid var(--border)', paddingBottom: 8 }}>🛠 Required Skills</h4>
                        <div style={{ display: 'flex', gap: 8, marginBottom: 12 }}>
                            <input
                                value={skillInput}
                                onChange={e => setSkillInput(e.target.value)}
                                onKeyDown={e => { if (e.key === 'Enter') { e.preventDefault(); addSkill(skillInput) } }}
                                className="form-control-custom"
                                placeholder="Type a skill and press Enter"
                                style={{ flex: 1 }}
                            />
                            <button type="button" className="btn-ghost" onClick={() => addSkill(skillInput)}>
                                <Plus size={15} /> Add
                            </button>
                        </div>
                        {/* Suggestions */}
                        <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6, marginBottom: 14 }}>
                            {SKILLS_SUGGESTIONS.filter(s => !skills.includes(s)).map(s => (
                                <span
                                    key={s}
                                    onClick={() => addSkill(s)}
                                    style={{ padding: '4px 10px', background: 'rgba(0, 0, 0, 0.03)', border: '1px solid rgba(0, 0, 0, 0.06)', borderRadius: 6, fontSize: 13, cursor: 'pointer', color: 'var(--text-secondary)', transition: 'all 0.2s' }}
                                    className="skill-suggestion-pill"
                                >
                                    + {s}
                                </span>
                            ))}
                        </div>
                        {/* Added skills */}
                        <div style={{ display: 'flex', flexWrap: 'wrap', gap: 5 }}>
                            {skills.map(s => (
                                <span key={s} className="skill-tag" style={{ paddingRight: 4 }}>
                                    {s}
                                    <button type="button" onClick={() => removeSkill(s)} style={{ background: 'none', border: 'none', cursor: 'pointer', marginLeft: 4, display: 'flex', alignItems: 'center', padding: 0 }}>
                                        <X size={11} color="#2563eb" />
                                    </button>
                                </span>
                            ))}
                        </div>
                    </div>

                    {/* Recruitment Hiring Rounds */}
                    <div style={{ marginBottom: 28 }}>
                        <h4 style={{ fontSize: 15, fontWeight: 700, color: 'var(--text-primary)', marginBottom: 16, borderBottom: '1px solid var(--border)', paddingBottom: 8 }}>📋 Recruitment Hiring Rounds (In Order)</h4>
                        <p style={{ fontSize: 13, color: 'var(--text-secondary)', marginBottom: 12 }}>Define progressive hiring rounds for this job. Note: Applied and Rejected/Hired options are supported automatically.</p>

                        <div style={{ display: 'flex', gap: 8, marginBottom: 14 }}>
                            <input
                                value={roundInput}
                                onChange={e => setRoundInput(e.target.value)}
                                onKeyDown={e => { if (e.key === 'Enter') { e.preventDefault(); addRound() } }}
                                className="form-control-custom"
                                placeholder="Type a stage: e.g. Technical Interview"
                                style={{ flex: 1 }}
                            />
                            <button type="button" className="btn-ghost" onClick={addRound} style={{ gap: 5 }}>
                                <Plus size={15} /> Add Stage
                            </button>
                        </div>

                        {/* Progressive sequence visualization */}
                        <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8, alignItems: 'center', background: 'rgba(255, 255, 255, 0.02)', border: '1px solid var(--border)', padding: 14, borderRadius: 8, minHeight: 48 }}>
                            {rounds.length === 0 && <span style={{ fontSize: 13, color: 'var(--text-muted)' }}>No rounds added yet. Add custom stages above.</span>}
                            {rounds.map((r, idx) => (
                                <div key={idx} style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                                    <div style={{ display: 'inline-flex', alignItems: 'center', gap: 6, padding: '6px 12px', background: 'rgba(37, 99, 235, 0.05)', border: '1.5px solid rgba(37, 99, 235, 0.2)', borderRadius: 20, fontSize: 13, color: 'var(--text-primary)', fontWeight: 600 }}>
                                        <span style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', width: 18, height: 18, background: '#2563eb', color: '#fff', borderRadius: '50%', fontSize: 10 }}>{idx + 1}</span>
                                        {r}
                                        <button type="button" onClick={() => removeRound(idx)} style={{ background: 'none', border: 'none', padding: 0, margin: 0, cursor: 'pointer', display: 'flex', alignItems: 'center', marginLeft: 4 }}>
                                            <X size={12} style={{ color: 'var(--text-secondary)' }} />
                                        </button>
                                    </div>
                                    {idx < rounds.length - 1 && <span style={{ color: 'var(--text-muted)', fontSize: 14, fontWeight: 700 }}>➔</span>}
                                </div>
                            ))}
                        </div>
                    </div>

                    <div style={{ display: 'flex', gap: 12 }}>
                        <button
                            type="submit"
                            className="btn-primary-custom"
                            disabled={loading}
                            style={{ padding: '10px 24px' }}
                        >
                            {loading ? (isEdit ? 'Saving...' : 'Posting...') : (isEdit ? '💾 Save Changes' : '🚀 Post Job')}
                        </button>
                        <button type="button" className="btn-ghost" onClick={() => navigate('/jobs')}>
                            Cancel
                        </button>
                    </div>
                </form>
            </div>
        </div>
    )
}
