import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { login, getCurrentUser } from '../api/api'
import { saveTokens, saveUser, isAuthenticated } from '../utils/auth'
import Register from './Register'
import Activate from './Activate'
import './Login.css'

function Login() {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const [activeTab, setActiveTab] = useState('login') // 'login', 'register', 'activate'
  const [activationCode, setActivationCode] = useState('')

  // Redirect to dashboard if already logged in
  useEffect(() => {
    if (isAuthenticated()) {
      navigate('/dashboard', { replace: true })
    }
  }, [navigate])

  // Login form state
  const [loginData, setLoginData] = useState({
    username: '',
    password: '',
  })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const handleLoginChange = (e) => {
    setLoginData({
      ...loginData,
      [e.target.name]: e.target.value
    })
  }

  const handleLoginSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError(null)

    try {
      // Login and get tokens
      const response = await login(loginData.username, loginData.password)
      
      // Save tokens
      saveTokens(response.access, response.refresh)
      
      // Get user info
      const userInfo = await getCurrentUser()
      saveUser(userInfo)
      
      // Redirect to dashboard
      navigate('/dashboard')
    } catch (err) {
      console.error('Login error:', err)
      if (err.response?.data) {
        if (err.response.data.detail) {
          setError(err.response.data.detail)
        } else if (err.response.data.non_field_errors) {
          setError(err.response.data.non_field_errors[0])
        } else {
          setError('Invalid username or password')
        }
      } else {
        setError('Login failed. Please try again.')
      }
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center p-4 bg-gradient-to-b from-gray-50 to-gray-100">
      <div className="bg-white rounded-2xl shadow-large max-w-4xl w-full overflow-hidden">
        {/* Tabs */}
        <div className="flex border-b border-gray-200 bg-gray-50">
          <button
            onClick={() => setActiveTab('login')}
            className={`flex-1 py-4 px-6 font-semibold transition-all ${
              activeTab === 'login'
                ? 'bg-white text-primary border-b-2 border-primary'
                : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
            }`}
          >
            🔐 {t('auth.login.tab')}
          </button>
          <button
            onClick={() => setActiveTab('register')}
            className={`flex-1 py-4 px-6 font-semibold transition-all ${
              activeTab === 'register'
                ? 'bg-white text-primary border-b-2 border-primary'
                : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
            }`}
          >
            ✨ {t('auth.register.tab')}
          </button>
          <button
            onClick={() => setActiveTab('activate')}
            className={`flex-1 py-4 px-6 font-semibold transition-all ${
              activeTab === 'activate'
                ? 'bg-white text-primary border-b-2 border-primary'
                : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
            }`}
          >
            🎯 {t('auth.activate.tab')}
          </button>
        </div>

        {/* Content */}
        <div className="p-8">
          {/* Login Tab */}
          {activeTab === 'login' && (
            <div>
              <div className="text-center mb-8">
                <h1 className="text-3xl font-bold text-gray-900 mb-2">{t('auth.login.title')}</h1>
                <p className="text-gray-600">{t('auth.login.subtitle')}</p>
              </div>

              {error && (
                <div className="bg-red-50 border-l-4 border-red-500 p-4 mb-6">
                  <p className="text-sm text-red-800">{error}</p>
                </div>
              )}

              <form onSubmit={handleLoginSubmit} className="max-w-md mx-auto space-y-4">
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                    {t('auth.login.username')}
                  </label>
                  <input
                    type="text"
                    name="username"
                    value={loginData.username}
                    onChange={handleLoginChange}
                    required
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent"
                  />
                </div>

                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                    {t('auth.login.password')}
                  </label>
                  <input
                    type="password"
                    name="password"
                    value={loginData.password}
                    onChange={handleLoginChange}
                    required
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent"
                  />
                </div>

                <button
                  type="submit"
                  disabled={loading}
                  className="w-full py-3 bg-gradient-to-r from-primary to-primary-400 text-white rounded-lg font-semibold hover:shadow-lg transition shadow-[0_4px_15px_-3px_rgba(37,99,235,0.3)] disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {loading ? t('auth.login.signingIn') : t('auth.login.signIn')}
                </button>
              </form>

              <div className="mt-6 text-center">
                <button
                  onClick={() => navigate('/')}
                  className="text-gray-500 hover:text-gray-700 text-sm"
                >
                  ← {t('common.back')}
                </button>
              </div>

              <div className="mt-8 pt-6 border-t border-gray-200 text-center">
                <p className="text-sm text-gray-600">
                  {t('auth.login.noAccount')}{' '}
                  <button
                    onClick={() => setActiveTab('register')}
                    className="text-primary font-semibold hover:underline"
                  >
                    {t('auth.login.registerHere')}
                  </button>
                </p>
              </div>
            </div>
          )}

          {/* Register Tab */}
          {activeTab === 'register' && (
            <div className="login-tab-content">
              <Register 
                embedded={true} 
                onSuccess={(code) => {
                  setActivationCode(code)
                  setActiveTab('activate')
                }} 
              />
            </div>
          )}

          {/* Activate Tab */}
          {activeTab === 'activate' && (
            <div className="login-tab-content">
              <Activate embedded={true} initialCode={activationCode} />
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default Login

