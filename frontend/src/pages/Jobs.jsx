import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import api from '../api/client'
import { Plus, MapPin, Clock, Users, Copy, ToggleLeft, ToggleRight, Trash2, ExternalLink, Download, Pencil } from 'lucide-react'

export default function Jobs() {
    const navigate = useNavigate()
    const [jobs, setJobs] = useState([])
    const [loading, setLoading] = useState(true)
    const [copied, setCopied] = useState(null)
    const [generatingPoster, setGeneratingPoster] = useState(null)

    const fetchJobs = () => {
        api.get('/jobs').then(r => setJobs(r.data.jobs || [])).catch(console.error).finally(() => setLoading(false))
    }

    useEffect(() => { fetchJobs() }, [])

    const copyLink = (job) => {
        const link = `${window.location.origin}/apply/${job.public_link?.split('/apply/')[1] || job._id}`
        navigator.clipboard.writeText(link)
        setCopied(job._id)
        setTimeout(() => setCopied(null), 2000)
    }

    const downloadPoster = (job) => {
        if (generatingPoster) return
        setGeneratingPoster(job._id)

        const canvas = document.createElement('canvas')
        canvas.width = 900
        canvas.height = 1350
        const ctx = canvas.getContext('2d')

        // 1. Futuristic dark-theme gradient background
        const bgGrad = ctx.createLinearGradient(0, 0, 0, 1350)
        bgGrad.addColorStop(0, '#0c0f1d')
        bgGrad.addColorStop(1, '#05070e')
        ctx.fillStyle = bgGrad
        ctx.fillRect(0, 0, 900, 1350)

        // 2. Abstract Ambient Aurora Glow overlays
        // Aurora 1 (Indigo glow in top right)
        let radGrad1 = ctx.createRadialGradient(750, 250, 50, 750, 250, 450)
        radGrad1.addColorStop(0, 'rgba(79, 70, 229, 0.16)')
        radGrad1.addColorStop(1, 'rgba(79, 70, 229, 0)')
        ctx.fillStyle = radGrad1
        ctx.beginPath()
        ctx.arc(750, 250, 450, 0, Math.PI * 2)
        ctx.fill()

        // Aurora 2 (Purple glow in bottom left)
        let radGrad2 = ctx.createRadialGradient(150, 1100, 50, 150, 1100, 500)
        radGrad2.addColorStop(0, 'rgba(124, 58, 237, 0.12)')
        radGrad2.addColorStop(1, 'rgba(124, 58, 237, 0)')
        ctx.fillStyle = radGrad2
        ctx.beginPath()
        ctx.arc(150, 1100, 500, 0, Math.PI * 2)
        ctx.fill()

        // Aurora 3 (Cyan/Teal accent near middle)
        let radGrad3 = ctx.createRadialGradient(450, 700, 50, 450, 700, 350)
        radGrad3.addColorStop(0, 'rgba(6, 182, 212, 0.05)')
        radGrad3.addColorStop(1, 'rgba(6, 182, 212, 0)')
        ctx.fillStyle = radGrad3
        ctx.beginPath()
        ctx.arc(450, 700, 350, 0, Math.PI * 2)
        ctx.fill()

        // 3. Grid Overlay Line Pattern for engineering aesthetic
        ctx.strokeStyle = 'rgba(99, 102, 241, 0.025)'
        ctx.lineWidth = 1
        const gridSize = 50
        for (let x = 0; x < canvas.width; x += gridSize) {
            ctx.beginPath()
            ctx.moveTo(x, 0)
            ctx.lineTo(x, canvas.height)
            ctx.stroke()
        }
        for (let y = 0; y < canvas.height; y += gridSize) {
            ctx.beginPath()
            ctx.moveTo(0, y)
            ctx.lineTo(canvas.width, y)
            ctx.stroke()
        }

        // Draw elegant thin borders
        ctx.strokeStyle = 'rgba(255, 255, 255, 0.05)'
        ctx.lineWidth = 16
        ctx.strokeRect(8, 8, 884, 1334)

        // 4. Header Branding (Company Name Primarily)
        const companyText = (job.company_name || 'Global Enterprise').toUpperCase()
        ctx.fillStyle = '#ffffff'
        ctx.font = "bold 34px 'Outfit', 'Plus Jakarta Sans', sans-serif"
        ctx.fillText(companyText, 60, 105)

        // Subtitle indicator
        ctx.fillStyle = '#818cf8' // vibrant soft indigo
        ctx.font = "600 13px 'Plus Jakarta Sans', sans-serif"
        ctx.fillText("CAREERS & OPPORTUNITIES", 60, 138)

        // Small tech accent line
        ctx.fillStyle = 'rgba(129, 140, 248, 0.3)'
        ctx.fillRect(60, 160, 80, 3)

        // 5. Floating Glassmorphic Main Job Position Card
        const cardY = 210
        const cardH = 750
        const cardW = 780
        const cardX = 60

        // Card backdrop fill
        ctx.fillStyle = 'rgba(255, 255, 255, 0.02)'
        ctx.beginPath()
        ctx.roundRect(cardX, cardY, cardW, cardH, 20)
        ctx.fill()

        // Card border stroke
        ctx.strokeStyle = 'rgba(255, 255, 255, 0.06)'
        ctx.lineWidth = 2.5
        ctx.stroke()

        // Card inner highlight sheen
        const highlightGrad = ctx.createLinearGradient(cardX, cardY, cardX + cardW, cardY + cardH)
        highlightGrad.addColorStop(0, 'rgba(255, 255, 255, 0.04)')
        highlightGrad.addColorStop(1, 'rgba(0, 0, 0, 0)')
        ctx.fillStyle = highlightGrad
        ctx.beginPath()
        ctx.roundRect(cardX, cardY, cardW, cardH, 20)
        ctx.fill()

        // Helper wrapping logic
        const wrapText = (context, text, x, y, maxWidth, lineHeight) => {
            const words = text.split(' ')
            let line = ''
            let currentY = y
            for (let n = 0; n < words.length; n++) {
                let testLine = line + words[n] + ' '
                let metrics = context.measureText(testLine)
                let testWidth = metrics.width
                if (testWidth > maxWidth && n > 0) {
                    context.fillText(line, x, currentY)
                    line = words[n] + ' '
                    currentY += lineHeight
                } else {
                    line = testLine
                }
            }
            context.fillText(line, x, currentY)
            return currentY
        }

        // Job Title Text (Large & Radiant)
        ctx.fillStyle = '#ffffff'
        ctx.font = "bold 44px 'Outfit', 'Plus Jakarta Sans', sans-serif"
        let headingY = wrapText(ctx, job.title, cardX + 50, cardY + 80, cardW - 100, 54)

        // 6. Metadata Pills (Location, Experience, Type)
        let pillY = headingY + 36
        const metadata = [
            `📍 ${job.location}`,
            `💼 ${job.employment_type}`,
            `⏱️ ${job.experience}`,
            job.salary ? `💰 ${job.salary}` : null
        ].filter(Boolean)

        let startX = cardX + 50
        metadata.forEach((text) => {
            ctx.font = "600 13px 'Plus Jakarta Sans', sans-serif"
            const textWidth = ctx.measureText(text).width
            const padX = 14
            const padY = 8
            const badgeW = textWidth + padX * 2
            const badgeH = 13 + padY * 2

            // Draw pill shapes
            ctx.fillStyle = 'rgba(255, 255, 255, 0.05)'
            ctx.strokeStyle = 'rgba(255, 255, 255, 0.06)'
            ctx.lineWidth = 1
            ctx.beginPath()
            ctx.roundRect(startX, pillY, badgeW, badgeH, 8)
            ctx.fill()
            ctx.stroke()

            ctx.fillStyle = '#e2e8f0'
            ctx.fillText(text, startX + padX, pillY + padY + 11)
            startX += badgeW + 12
        })

        // Divider
        let contentY = pillY + 75
        ctx.fillStyle = 'rgba(255, 255, 255, 0.06)'
        ctx.fillRect(cardX + 50, contentY, cardW - 100, 1.5)

        // 7. Role Description
        contentY += 45
        ctx.fillStyle = '#c7d2fe' // soft lavender label
        ctx.font = "bold 15px 'Outfit', 'Plus Jakarta Sans', sans-serif"
        ctx.fillText("ROLE OVERVIEW", cardX + 50, contentY)

        contentY += 25
        ctx.fillStyle = '#94a3b8' // Slate-400 font
        ctx.font = "normal 16px 'Plus Jakarta Sans', sans-serif"
        const descText = job.job_description || "We are searching for a qualified candidate to join our high-performing team. In this position, you will collaborate on innovative features and contribute to business outcomes."
        const shortDesc = descText.length > 340 ? descText.substring(0, 335) + "..." : descText
        contentY = wrapText(ctx, shortDesc, cardX + 50, contentY, cardW - 100, 26)

        // Divider
        contentY += 35
        ctx.fillStyle = 'rgba(255, 255, 255, 0.06)'
        ctx.fillRect(cardX + 50, contentY, cardW - 100, 1.5)

        // 8. Key Target Skills
        contentY += 45
        ctx.fillStyle = '#c7d2fe'
        ctx.font = "bold 15px 'Outfit', 'Plus Jakarta Sans', sans-serif"
        ctx.fillText("KEY SKILLS & STACK", cardX + 50, contentY)

        contentY += 25
        const skillsObj = job.required_skills || []
        let skillX = cardX + 50
        let skillY = contentY
        skillsObj.slice(0, 8).forEach((skill) => {
            ctx.font = "600 13px 'Plus Jakarta Sans', sans-serif"
            const width = ctx.measureText(skill).width
            const padX = 14
            const padY = 7
            const tagW = width + padX * 2
            const tagH = 13 + padY * 2

            if (skillX + tagW > cardX + cardW - 50) {
                skillX = cardX + 50
                skillY += tagH + 8
            }

            ctx.fillStyle = 'rgba(129, 140, 248, 0.06)'
            ctx.strokeStyle = 'rgba(129, 140, 248, 0.12)'
            ctx.lineWidth = 1
            ctx.beginPath()
            ctx.roundRect(skillX, skillY, tagW, tagH, 6)
            ctx.fill()
            ctx.stroke()

            ctx.fillStyle = '#a5b4fc'
            ctx.fillText(skill, skillX + padX, skillY + padY + 10)
            skillX += tagW + 8
        })

        // 9. QR Scan Card Section (Static Bottom placement)
        const qrCardY = 1010
        const qrCardW = 780
        const qrCardH = 260
        const qrCardX = 60

        // QR card backdrop
        ctx.fillStyle = 'rgba(255, 255, 255, 0.015)'
        ctx.beginPath()
        ctx.roundRect(qrCardX, qrCardY, qrCardW, qrCardH, 16)
        ctx.fill()

        ctx.strokeStyle = 'rgba(255, 255, 255, 0.04)'
        ctx.lineWidth = 1.5
        ctx.stroke()

        // Text labels inside QR Card
        ctx.fillStyle = '#ffffff'
        ctx.font = "bold 22px 'Outfit', 'Plus Jakarta Sans', sans-serif"
        ctx.fillText("Scan to Apply", qrCardX + 270, qrCardY + 68)

        ctx.fillStyle = '#94a3b8'
        ctx.font = "normal 14px 'Plus Jakarta Sans', sans-serif"
        const applyUrl = `${window.location.origin}/apply/${job.public_link?.split('/apply/')[1] || job._id}`
        wrapText(ctx, "Point your phone camera here to review full requirements, job benefits, and submit your resume directly to our hiring team.", qrCardX + 270, qrCardY + 105, 460, 22)

        ctx.fillStyle = '#818cf8'
        ctx.font = "bold 14px 'Plus Jakarta Sans', sans-serif"
        ctx.fillText(`Portal Link: apply.talentflow.co/${job.public_link?.split('/apply/')[1] || job._id}`, qrCardX + 270, qrCardY + 205)

        // Draw white container for high-contrast QR rendering
        ctx.fillStyle = '#ffffff'
        ctx.beginPath()
        ctx.roundRect(qrCardX + 35, qrCardY + 30, 200, 200, 12)
        ctx.fill()

        const qrImg = new Image()
        qrImg.crossOrigin = 'anonymous'
        qrImg.onload = () => {
            ctx.drawImage(qrImg, qrCardX + 45, qrCardY + 40, 180, 180)

            const dataUrl = canvas.toDataURL('image/png')
            const linkTag = document.createElement('a')
            linkTag.download = `JobPoster_${job.title.replace(/\s+/g, '_')}.png`
            linkTag.href = dataUrl
            linkTag.click()
            setGeneratingPoster(null)
        }
        qrImg.onerror = () => {
            // Draw offline indicator inside white container
            ctx.strokeStyle = '#dc2626'
            ctx.lineWidth = 1.5
            ctx.strokeRect(qrCardX + 45, qrCardY + 40, 180, 180)
            ctx.fillStyle = '#dc2626'
            ctx.font = "bold 13px sans-serif"
            ctx.fillText("QR Load Offline", qrCardX + 75, qrCardY + 130)

            const dataUrl = canvas.toDataURL('image/png')
            const linkTag = document.createElement('a')
            linkTag.download = `JobPoster_${job.title.replace(/\s+/g, '_')}.png`
            linkTag.href = dataUrl
            linkTag.click()
            setGeneratingPoster(null)
        }
        qrImg.src = `https://api.qrserver.com/v1/create-qr-code/?size=250x250&data=${encodeURIComponent(applyUrl)}`
    }

    const toggleJob = async (jobId) => {
        await api.patch(`/jobs/${jobId}/toggle`)
        fetchJobs()
    }

    const deleteJob = async (jobId) => {
        if (!confirm('Delete this job? All applications will remain.')) return
        await api.delete(`/jobs/${jobId}`)
        fetchJobs()
    }

    if (loading) return <div className="spinner-overlay"><div className="spinner-ring" /><span>Loading jobs...</span></div>

    return (
        <div>
            <div className="page-header">
                <div>
                    <h1>Job Management</h1>
                    <p>{jobs.length} job{jobs.length !== 1 ? 's' : ''} posted</p>
                </div>
                <button className="btn-primary-custom" onClick={() => navigate('/jobs/create')}>
                    <Plus size={16} /> Post Job
                </button>
            </div>

            {jobs.length === 0 ? (
                <div className="card">
                    <div className="empty-state">
                        <div className="empty-state-icon">💼</div>
                        <h4>No jobs posted yet</h4>
                        <p>Create your first job posting to start receiving applications.</p>
                        <button className="btn-primary-custom" onClick={() => navigate('/jobs/create')} style={{ marginTop: 16 }}>
                            <Plus size={15} /> Post Your First Job
                        </button>
                    </div>
                </div>
            ) : (
                <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
                    {jobs.map(job => (
                        <div className="card" key={job._id} style={{ padding: 24 }}>
                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: 16 }}>
                                <div style={{ flex: 1 }}>
                                    <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 8 }}>
                                        <h3 style={{ fontSize: 16, fontWeight: 700, color: 'var(--text-primary)' }}>{job.title}</h3>
                                        <span className={job.is_active ? 'status-badge badge-shortlisted' : 'status-badge'} style={{ padding: '2px 8px', fontSize: 11 }}>
                                            {job.is_active ? 'Active' : 'Closed'}
                                        </span>
                                    </div>
                                    <div style={{ display: 'flex', gap: 16, color: 'var(--text-secondary)', flexWrap: 'wrap' }}>
                                        <span style={{ display: 'flex', alignItems: 'center', gap: 4, fontSize: 13 }}>
                                            <MapPin size={13} style={{ color: 'var(--primary)' }} /> {job.location}
                                        </span>
                                        <span style={{ display: 'flex', alignItems: 'center', gap: 4, fontSize: 13 }}>
                                            <Clock size={13} style={{ color: 'var(--primary)' }} /> {job.experience}
                                        </span>
                                        <span style={{ display: 'flex', alignItems: 'center', gap: 4, fontSize: 13 }}>
                                            {job.employment_type}
                                        </span>
                                        <span style={{ fontSize: 13 }}>📅 Deadline: {job.deadline}</span>
                                    </div>
                                    <div style={{ marginTop: 12, display: 'flex', flexWrap: 'wrap', gap: 4 }}>
                                        {(job.required_skills || []).slice(0, 6).map(s => (
                                            <span key={s} className="skill-tag">{s}</span>
                                        ))}
                                        {(job.required_skills || []).length > 6 && (
                                            <span className="skill-tag" style={{ background: 'rgba(255,255,255,0.05)', color: 'var(--text-secondary)' }}>+{job.required_skills.length - 6}</span>
                                        )}
                                    </div>
                                </div>
                                <div style={{ display: 'flex', gap: 8, flexShrink: 0 }}>
                                    <button
                                        className="btn-ghost"
                                        onClick={() => copyLink(job)}
                                        title="Copy application link"
                                        style={{ fontSize: 12, gap: 5 }}
                                    >
                                        <Copy size={14} />
                                        {copied === job._id ? 'Copied!' : 'Copy Link'}
                                    </button>
                                    <button
                                        className="btn-ghost"
                                        onClick={() => downloadPoster(job)}
                                        disabled={generatingPoster === job._id}
                                        title="Download job poster"
                                        style={{ fontSize: 12, gap: 5 }}
                                    >
                                        <Download size={14} />
                                        {generatingPoster === job._id ? 'Generating...' : 'Poster'}
                                    </button>
                                    <button
                                        className="btn-ghost"
                                        onClick={() => navigate(`/jobs/edit/${job._id}`)}
                                        title="Edit job"
                                        style={{ fontSize: 12, gap: 5 }}
                                    >
                                        <Pencil size={14} />
                                        Edit
                                    </button>
                                    <button
                                        className="btn-ghost"
                                        onClick={() => toggleJob(job._id)}
                                        title={job.is_active ? 'Close job' : 'Reopen job'}
                                    >
                                        {job.is_active ? <ToggleRight size={16} color="#16a34a" /> : <ToggleLeft size={16} />}
                                    </button>
                                    <button
                                        className="btn-ghost"
                                        onClick={() => navigate(`/applicants?job=${job._id}`)}
                                        title="View applicants"
                                    >
                                        <Users size={15} />
                                    </button>
                                    <button
                                        className="btn-ghost"
                                        onClick={() => deleteJob(job._id)}
                                        title="Delete job"
                                        style={{ color: '#dc2626' }}
                                    >
                                        <Trash2 size={15} />
                                    </button>
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    )
}
