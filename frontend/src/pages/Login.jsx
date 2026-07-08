import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { useAuth } from '../context/AuthContext'
import api from '../api/client'
import { Zap, Mail, Lock, AlertCircle } from 'lucide-react'

export default function Login() {
    const { login } = useAuth()
    const navigate = useNavigate()
    const [error, setError] = useState('')
    const [loading, setLoading] = useState(false)
    const { register, handleSubmit, formState: { errors } } = useForm()

    const onSubmit = async (data) => {
        setLoading(true)
        setError('')
        try {
            const resp = await api.post('/auth/login', data)
            const token = resp.data.access_token
            // Decode user info from token (simple base64 decode)
            const payload = JSON.parse(atob(token.split('.')[1]))
            login({ email: payload.email, company_name: payload.company_name }, token)
            navigate('/dashboard')
        } catch (err) {
            setError(err.response?.data?.detail || 'Login failed. Check your credentials.')
        } finally {
            setLoading(false)
        }
    }

    return (
        <div className="auth-page">
            <div className="auth-card">
                <div style={{ textAlign: 'center', marginBottom: 28 }}>
                    <div style={{ display: 'inline-flex', alignItems: 'center', justifyContent: 'center', width: 52, height: 52, background: 'linear-gradient(135deg, #2563eb, #818cf8)', borderRadius: 14, marginBottom: 14 }}>
                        <Zap size={24} color="white" />
                    </div>
                    <h1 style={{ fontSize: 22, fontWeight: 700, color: '#0f172a' }}>Welcome back</h1>
                    <p style={{ fontSize: 13.5, color: '#64748b', marginTop: 4 }}>Sign in to your TalentFlow dashboard</p>
                </div>

                {error && (
                    <div className="alert-banner alert-error" style={{ marginBottom: 16 }}>
                        <AlertCircle size={16} /> {error}
                    </div>
                )}

                <form onSubmit={handleSubmit(onSubmit)}>
                    <div style={{ marginBottom: 16 }}>
                        <label className="form-label-custom">Email Address</label>
                        <div style={{ position: 'relative' }}>
                            <Mail size={15} style={{ position: 'absolute', left: 12, top: '50%', transform: 'translateY(-50%)', color: '#94a3b8' }} />
                            <input
                                {...register('email', { required: 'Email is required' })}
                                type="email"
                                className="form-control-custom"
                                placeholder="hr@company.com"
                                style={{ paddingLeft: 36 }}
                            />
                        </div>
                        {errors.email && <p style={{ color: '#dc2626', fontSize: 12, marginTop: 4 }}>{errors.email.message}</p>}
                    </div>

                    <div style={{ marginBottom: 24 }}>
                        <label className="form-label-custom">Password</label>
                        <div style={{ position: 'relative' }}>
                            <Lock size={15} style={{ position: 'absolute', left: 12, top: '50%', transform: 'translateY(-50%)', color: '#94a3b8' }} />
                            <input
                                {...register('password', { required: 'Password is required' })}
                                type="password"
                                className="form-control-custom"
                                placeholder="••••••••"
                                style={{ paddingLeft: 36 }}
                            />
                        </div>
                        {errors.password && <p style={{ color: '#dc2626', fontSize: 12, marginTop: 4 }}>{errors.password.message}</p>}
                    </div>

                    <button
                        type="submit"
                        className="btn-primary-custom"
                        style={{ width: '100%', justifyContent: 'center', padding: '11px', fontSize: 14 }}
                        disabled={loading}
                    >
                        {loading ? 'Signing in...' : 'Sign In'}
                    </button>
                </form>

                <p style={{ textAlign: 'center', marginTop: 20, fontSize: 13.5, color: '#64748b' }}>
                    Don't have an account? <Link to="/register" style={{ color: '#2563eb', fontWeight: 600 }}>Create account</Link>
                </p>
            </div>
        </div>
    )
}
