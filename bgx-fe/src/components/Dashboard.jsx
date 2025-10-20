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
    <div className="min-h-screen bg-white">
      {/* Header */}
      <header className="bg-white shadow-soft border-b border-secondary-200 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-2xl font-bold text-secondary-900">🏍️ {t('dashboard.title')}</h1>
              <p className="text-secondary-600 text-sm">{t('dashboard.welcome', { name: user.first_name || user.username })}</p>
            </div>
            <div className="flex gap-3 items-center">
              <LanguageSwitcher />
              <button
                onClick={() => navigate('/')}
                className="px-4 py-2 text-secondary-700 hover:text-secondary-900 font-medium text-sm transition-colors"
              >
                {t('dashboard.home')}
              </button>
              <button
                onClick={handleLogout}
                className="px-4 py-2 bg-primary text-white rounded-lg font-medium text-sm hover:bg-primary-dark transition-colors shadow-sm"
              >
                {t('header.logout')}
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 py-8">
        {/* User Profile Card */}
        <div className="bg-white rounded-xl shadow-soft border border-secondary-200 p-8 mb-6">
          <div className="flex items-start justify-between">
            <div>
              <h2 className="text-2xl font-bold text-secondary-900 mb-2">
                {user.first_name} {user.last_name}
              </h2>
              <p className="text-secondary-600 mb-1 text-sm">
                <span className="font-medium">{t('dashboard.username')}:</span> {user.username}
              </p>
              <p className="text-secondary-600 mb-1 text-sm">
                <span className="font-medium">{t('dashboard.email')}:</span> {user.email}
              </p>
              <div className="mt-3 flex gap-2">
                {user.is_rider && (
                  <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-primary-50 text-primary-700 border border-primary-200">
                    🏍️ {t('dashboard.rider')}
                  </span>
                )}
                {user.is_club_admin && (
                  <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-accent-50 text-accent-700 border border-accent-200">
                    👥 {t('dashboard.clubAdmin')}
                  </span>
                )}
                {user.is_system_admin && (
                  <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-red-50 text-red-700 border border-red-200">
                    ⚙️ {t('dashboard.admin')}
                  </span>
                )}
              </div>
            </div>
            <div className="text-5xl">
              👤
            </div>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="grid md:grid-cols-3 gap-6 mb-6">
          <button
            onClick={() => navigate('/')}
            className="bg-white rounded-xl shadow-soft border border-secondary-200 p-6 hover:border-primary hover:shadow-medium transition-all text-left group"
          >
            <div className="text-3xl mb-3">🏁</div>
            <h3 className="text-lg font-semibold text-secondary-900 group-hover:text-primary mb-2 transition-colors">
              {t('dashboard.viewRaces')}
            </h3>
            <p className="text-secondary-600 text-sm">
              {t('dashboard.viewRacesDesc')}
            </p>
          </button>

          <button
            onClick={() => {
              // TODO: Navigate to user's rider profile if they have one
              navigate('/')
            }}
            className="bg-white rounded-xl shadow-soft border border-secondary-200 p-6 hover:border-primary hover:shadow-medium transition-all text-left group"
          >
            <div className="text-3xl mb-3">📊</div>
            <h3 className="text-lg font-semibold text-secondary-900 group-hover:text-primary mb-2 transition-colors">
              {t('dashboard.myResults')}
            </h3>
            <p className="text-secondary-600 text-sm">
              {t('dashboard.myResultsDesc')}
            </p>
          </button>

          <button
            onClick={() => navigate('/')}
            className="bg-white rounded-xl shadow-soft border border-secondary-200 p-6 hover:border-primary hover:shadow-medium transition-all text-left group"
          >
            <div className="text-3xl mb-3">🏆</div>
            <h3 className="text-lg font-semibold text-secondary-900 group-hover:text-primary mb-2 transition-colors">
              {t('dashboard.championships')}
            </h3>
            <p className="text-secondary-600 text-sm">
              {t('dashboard.championshipsDesc')}
            </p>
          </button>
        </div>

        {/* Account Info */}
        <div className="bg-white rounded-xl shadow-soft border border-secondary-200 p-6">
          <h3 className="text-lg font-semibold text-secondary-900 mb-4">{t('dashboard.accountInfo')}</h3>
          <div className="grid md:grid-cols-2 gap-4 text-sm">
            <div>
              <p className="text-secondary-600 mb-1">{t('dashboard.accountStatus')}</p>
              <p className="font-medium text-secondary-900">
                {user.is_activated ? (
                  <span className="text-success">✓ {t('dashboard.activated')}</span>
                ) : (
                  <span className="text-orange-600">⚠ {t('dashboard.pending')}</span>
                )}
              </p>
            </div>
            <div>
              <p className="text-secondary-600 mb-1">{t('dashboard.memberSince')}</p>
              <p className="font-medium text-secondary-900">
                {new Date(user.date_joined).toLocaleDateString()}
              </p>
            </div>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-secondary-50 border-t border-secondary-200 py-8 mt-16">
        <div className="max-w-7xl mx-auto px-4 text-center">
          <p className="text-sm text-secondary-600">{t('app.footer')}</p>
        </div>
      </footer>
    </div>
  )
}

export default Dashboard

