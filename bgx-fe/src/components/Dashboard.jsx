import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { getUser, logout } from '../utils/auth'
import LanguageSwitcher from './LanguageSwitcher'
import './Dashboard.css'

function Dashboard() {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const [user, setUser] = useState(null)

  useEffect(() => {
    const currentUser = getUser()
    if (!currentUser) {
      // Not logged in, redirect to login
      navigate('/login')
    } else {
      setUser(currentUser)
    }
  }, [navigate])

  const handleLogout = () => {
    logout()
    navigate('/')
  }

  if (!user) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="spinner"></div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-50 to-gray-100">
      {/* Header */}
      <header className="bg-gradient-to-r from-primary-900 via-primary to-primary-400 text-white shadow-large">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-3xl font-bold mb-1">🏍️ {t('dashboard.title')}</h1>
              <p className="text-white/90">{t('dashboard.welcome', { name: user.first_name || user.username })}</p>
            </div>
            <div className="flex gap-3 items-center">
              <LanguageSwitcher />
              <button
                onClick={() => navigate('/')}
                className="px-5 py-2.5 bg-white/10 text-white rounded-lg font-semibold hover:bg-white/20 transition-all backdrop-blur-sm border border-white/30"
              >
                {t('dashboard.home')}
              </button>
              <button
                onClick={handleLogout}
                className="px-5 py-2.5 bg-white/10 text-white rounded-lg font-semibold hover:bg-white/20 transition-all backdrop-blur-sm border border-white/30"
              >
                {t('header.logout')}
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 py-8 -mt-8 relative z-10">
        {/* User Profile Card */}
        <div className="bg-white rounded-2xl shadow-large p-8 mb-6">
          <div className="flex items-start justify-between">
            <div>
              <h2 className="text-2xl font-bold text-gray-900 mb-2">
                {user.first_name} {user.last_name}
              </h2>
              <p className="text-gray-600 mb-1">
                <span className="font-semibold">{t('dashboard.username')}:</span> {user.username}
              </p>
              <p className="text-gray-600 mb-1">
                <span className="font-semibold">{t('dashboard.email')}:</span> {user.email}
              </p>
              <div className="mt-3 flex gap-2">
                {user.is_rider && (
                  <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold bg-blue-100 text-blue-700 border border-blue-200">
                    🏍️ {t('dashboard.rider')}
                  </span>
                )}
                {user.is_club_admin && (
                  <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold bg-purple-100 text-purple-700 border border-purple-200">
                    👥 {t('dashboard.clubAdmin')}
                  </span>
                )}
                {user.is_system_admin && (
                  <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold bg-red-100 text-red-700 border border-red-200">
                    ⚙️ {t('dashboard.admin')}
                  </span>
                )}
              </div>
            </div>
            <div className="text-6xl">
              👤
            </div>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="grid md:grid-cols-3 gap-6 mb-6">
          <button
            onClick={() => navigate('/')}
            className="bg-white rounded-xl shadow-soft p-6 hover:shadow-medium transition-all text-left group"
          >
            <div className="text-4xl mb-3">🏁</div>
            <h3 className="text-xl font-bold text-gray-900 group-hover:text-primary mb-2">
              {t('dashboard.viewRaces')}
            </h3>
            <p className="text-gray-600 text-sm">
              {t('dashboard.viewRacesDesc')}
            </p>
          </button>

          <button
            onClick={() => {
              // TODO: Navigate to user's rider profile if they have one
              navigate('/')
            }}
            className="bg-white rounded-xl shadow-soft p-6 hover:shadow-medium transition-all text-left group"
          >
            <div className="text-4xl mb-3">📊</div>
            <h3 className="text-xl font-bold text-gray-900 group-hover:text-primary mb-2">
              {t('dashboard.myResults')}
            </h3>
            <p className="text-gray-600 text-sm">
              {t('dashboard.myResultsDesc')}
            </p>
          </button>

          <button
            onClick={() => navigate('/')}
            className="bg-white rounded-xl shadow-soft p-6 hover:shadow-medium transition-all text-left group"
          >
            <div className="text-4xl mb-3">🏆</div>
            <h3 className="text-xl font-bold text-gray-900 group-hover:text-primary mb-2">
              {t('dashboard.championships')}
            </h3>
            <p className="text-gray-600 text-sm">
              {t('dashboard.championshipsDesc')}
            </p>
          </button>
        </div>

        {/* Account Info */}
        <div className="bg-white rounded-2xl shadow-soft p-6">
          <h3 className="text-xl font-bold text-gray-900 mb-4">{t('dashboard.accountInfo')}</h3>
          <div className="grid md:grid-cols-2 gap-4 text-sm">
            <div>
              <p className="text-gray-600 mb-1">{t('dashboard.accountStatus')}</p>
              <p className="font-semibold text-gray-900">
                {user.is_activated ? (
                  <span className="text-green-600">✓ {t('dashboard.activated')}</span>
                ) : (
                  <span className="text-orange-600">⚠ {t('dashboard.pending')}</span>
                )}
              </p>
            </div>
            <div>
              <p className="text-gray-600 mb-1">{t('dashboard.memberSince')}</p>
              <p className="font-semibold text-gray-900">
                {new Date(user.date_joined).toLocaleDateString()}
              </p>
            </div>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-gradient-to-r from-secondary-900 to-secondary-800 text-white/70 py-8 mt-16">
        <div className="max-w-7xl mx-auto px-4 text-center">
          <p className="text-sm">{t('app.footer')}</p>
        </div>
      </footer>
    </div>
  )
}

export default Dashboard

