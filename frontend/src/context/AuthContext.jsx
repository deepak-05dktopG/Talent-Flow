import { createContext, useContext, useState, useEffect } from 'react'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
    const [user, setUser] = useState(null)
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        const savedUser = localStorage.getItem('talentflow_user')
        const savedToken = localStorage.getItem('talentflow_token')
        if (savedUser && savedToken) {
            setUser(JSON.parse(savedUser))
        }
        setLoading(false)
    }, [])

    const login = (userData, token) => {
        localStorage.setItem('talentflow_token', token)
        localStorage.setItem('talentflow_user', JSON.stringify(userData))
        setUser(userData)
    }

    const logout = () => {
        localStorage.removeItem('talentflow_token')
        localStorage.removeItem('talentflow_user')
        setUser(null)
    }

    return (
        <AuthContext.Provider value={{ user, loading, login, logout }}>
            {children}
        </AuthContext.Provider>
    )
}

export const useAuth = () => useContext(AuthContext)
