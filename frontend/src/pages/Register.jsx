import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { useAuth } from '../context/AuthContext'
import api from '../api/client'
import { Zap, Building2, Mail, Lock, AlertCircle, CheckCircle } from 'lucide-react'

export default function Register() {
    const { login } = useAuth()
    const navigate = useNavigate()
    const [error, setError] = useState('')
    const [loading, setLoading] = useState(false)
    const { register, handleSubmit, formState: { errors } } = useForm()

    const onSubmit = async (data) => {
        setLoading(true)
        setError('')
        try {
            const resp = await api.post('/auth/register', data)
            const token = resp.data.access_token
            const payload = JSON.parse(atob(token.split('.')[1]))
            login({ email: payload.email, company_name: payload.company_name }, token)
            navigate('/dashboard')
        } catch (err) {
            setError(err.response?.data?.detail || 'Registration failed. Please try again.')
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
                    <h1 style={{ fontSize: 22, fontWeight: 700, color: '#0f172a' }}>Create your account</h1>
                    <p style={{ fontSize: 13.5, color: '#64748b', marginTop: 4 }}>Set up your HR recruitment workspace</p>
                </div>

                {error && (
                    <div className="alert-banner alert-error" style={{ marginBottom: 16 }}>
                        <AlertCircle size={16} /> {error}
                    </div>
                )}

                <form onSubmit={handleSubmit(onSubmit)}>
                    <div style={{ marginBottom: 14 }}>
                        <label className="form-label-custom">Company Name</label>
                        <div style={{ position: 'relative' }}>
                            <Building2 size={15} style={{ position: 'absolute', left: 12, top: '50%', transform: 'translateY(-50%)', color: '#94a3b8' }} />
                            <input
                                {...register('company_name', { required: 'Company name is required', minLength: { value: 2, message: 'Too short' } })}
                                type="text"
                                className="form-control-custom"
                                placeholder="Acme Inc."
                                style={{ paddingLeft: 36 }}
                            />
                        </div>
                        {errors.company_name && <p style={{ color: '#dc2626', fontSize: 12, marginTop: 4 }}>{errors.company_name.message}</p>}
                    </div>

                    <div style={{ marginBottom: 14 }}>
                        <label className="form-label-custom">Work Email</label>
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
                                {...register('password', { required: 'Password is required', minLength: { value: 6, message: 'Min 6 characters' } })}
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
                        {loading ? 'Creating Account...' : 'Create Account'}
                    </button>
                </form>

                <p style={{ textAlign: 'center', marginTop: 20, fontSize: 13.5, color: '#64748b' }}>
                    Already have an account? <Link to="/login" style={{ color: '#2563eb', fontWeight: 600 }}>Sign in</Link>
                </p>
            </div>
        </div>
    )
}
