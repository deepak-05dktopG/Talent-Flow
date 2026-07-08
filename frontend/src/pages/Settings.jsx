import { useState } from 'react'
import { useAuth } from '../context/AuthContext'
import { Building2, Mail, Save, CheckCircle, Key } from 'lucide-react'

export default function Settings() {
    const { user } = useAuth()
    const [saved, setSaved] = useState(false)

    const handleSave = () => {
        setSaved(true)
        setTimeout(() => setSaved(false), 2000)
    }

    return (
        <div>
            <div className="page-header">
                <div>
                    <h1>Settings</h1>
                    <p>Manage your account preferences</p>
                </div>
            </div>

            {saved && <div className="alert-banner alert-success" style={{ marginBottom: 20 }}><CheckCircle size={16} /> Settings saved!</div>}

            <div className="card" style={{ padding: 24, marginBottom: 16 }}>
                <h3 style={{ fontSize: 15, fontWeight: 800, marginBottom: 18, color: 'var(--text-primary)', fontFamily: 'Outfit, sans-serif' }}>Company Information</h3>
                <div style={{ marginBottom: 14 }}>
                    <label className="form-label-custom">Company Name</label>
                    <div style={{ position: 'relative' }}>
                        <Building2 size={15} style={{ position: 'absolute', left: 12, top: '50%', transform: 'translateY(-50%)', color: '#94a3b8' }} />
                        <input defaultValue={user?.company_name || ''} className="form-control-custom" style={{ paddingLeft: 36 }} />
                    </div>
                </div>
                <div style={{ marginBottom: 20 }}>
                    <label className="form-label-custom">Email Address</label>
                    <div style={{ position: 'relative' }}>
                        <Mail size={15} style={{ position: 'absolute', left: 12, top: '50%', transform: 'translateY(-50%)', color: '#94a3b8' }} />
                        <input defaultValue={user?.email || ''} className="form-control-custom" style={{ paddingLeft: 36 }} readOnly />
                    </div>
                </div>
                <button className="btn-primary-custom" onClick={handleSave}>
                    <Save size={15} /> Save Changes
                </button>
            </div>

            <div className="card" style={{ padding: 24, marginBottom: 16 }}>
                <h3 style={{ fontSize: 15, fontWeight: 800, marginBottom: 8, color: 'var(--text-primary)', fontFamily: 'Outfit, sans-serif' }}>Change Password</h3>
                <p style={{ fontSize: 13.5, color: 'var(--text-secondary)', marginBottom: 16 }}>Update your account password</p>
                <div style={{ marginBottom: 14 }}>
                    <label className="form-label-custom">Current Password</label>
                    <input type="password" className="form-control-custom" placeholder="••••••••" />
                </div>
                <div style={{ marginBottom: 14 }}>
                    <label className="form-label-custom">New Password</label>
                    <input type="password" className="form-control-custom" placeholder="••••••••" />
                </div>
                <div style={{ marginBottom: 20 }}>
                    <label className="form-label-custom">Confirm New Password</label>
                    <input type="password" className="form-control-custom" placeholder="••••••••" />
                </div>
                <button className="btn-primary-custom" onClick={handleSave}>
                    <Key size={15} /> Update Password
                </button>
            </div>

            <div className="card" style={{ padding: 24 }}>
                <h3 style={{ fontSize: 15, fontWeight: 800, marginBottom: 8, color: 'var(--text-primary)', fontFamily: 'Outfit, sans-serif' }}>Integrations</h3>
                <p style={{ fontSize: 13.5, color: 'var(--text-secondary)' }}>Configure API integrations via the <code>.env</code> file in the backend directory. Supported integrations:</p>
                <ul style={{ marginTop: 12, paddingLeft: 18, fontSize: 14, color: 'var(--text-primary)', lineHeight: 2 }}>
                    <li>🤖 <strong>Groq AI</strong> – Resume analysis and interview questions (set <code>GROQ_API_KEY</code>)</li>
                    <li>📧 <strong>Resend</strong> – Email notifications (set <code>RESEND_API_KEY</code>)</li>
                    <li>☁️ <strong>Cloudinary</strong> – Resume file storage (set <code>CLOUDINARY_*</code> keys)</li>
                    <li>🗄️ <strong>MongoDB</strong> – Cloud database (set <code>MONGO_URI</code>)</li>
                </ul>
            </div>
        </div>
    )
}
