import { useState, useEffect } from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import ChampionshipSelector from './components/ChampionshipSelector'
import RaceList from './components/RaceList'
import RaceDetail from './components/RaceDetail'
import ChampionshipResults from './components/ChampionshipResults'
import RiderDetail from './components/RiderDetail'
import Login from './components/Login'
import Dashboard from './components/Dashboard'
import LanguageSwitcher from './components/LanguageSwitcher'
import { getChampionships } from './api/api'
import { syncLanguageOnInit } from './utils/languageSync'
import { isAuthenticated, getUser, logout } from './utils/auth'
import './App.css'

function HomePage() {
  const { t } = useTranslation()
  const [championships, setChampionships] = useState([])
  const [selectedChampionship, setSelectedChampionship] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [isLoggedIn, setIsLoggedIn] = useState(false)
  const [currentUser, setCurrentUser] = useState(null)

  useEffect(() => {
    // Check authentication status
    setIsLoggedIn(isAuthenticated())
    setCurrentUser(getUser())
    
    // Sync language on app init
    syncLanguageOnInit().then(() => {
      loadChampionships()
    })
  }, [])

  const loadChampionships = async () => {
    try {
      setLoading(true)
      const data = await getChampionships()
      setChampionships(data)
      // Auto-select first championship if available
      if (data.length > 0) {
        setSelectedChampionship(data[0])
      }
    } catch (err) {
      setError('Failed to load championships')
      console.error('Error loading championships:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleChampionshipChange = (championship) => {
    setSelectedChampionship(championship)
  }

  const handleLogout = () => {
    logout()
    setIsLoggedIn(false)
    setCurrentUser(null)
    // Optionally reload page to reset state
    window.location.reload()
  }

  if (loading) {
    return (
      <div className="app">
        <div className="loading">
          <div className="spinner"></div>
          <p>{t('common.loading')}</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="app">
        <div className="error">
          <h2>⚠️ {t('common.error')}</h2>
          <p>{error}</p>
          <button onClick={loadChampionships}>{t('common.retry')}</button>
        </div>
      </div>
    )
  }

  return (
    <div className="app">
      <header className="app-header">
        <div className="flex justify-between items-center max-w-7xl mx-auto">
          <div>
            <h1>🏍️ {t('app.title')}</h1>
          </div>
          <div className="flex gap-3 items-center">
            <LanguageSwitcher />
            
            {isLoggedIn ? (
              // Logged in state
              <>
                <span className="text-secondary-600 text-sm font-medium hidden sm:inline">
                  {t('header.welcome', { name: currentUser?.username || 'User' })}
                </span>
                <button
                  onClick={handleLogout}
                  className="px-4 py-2 text-secondary-700 hover:text-secondary-900 font-medium text-sm transition-colors"
                >
                  {t('header.logout')}
                </button>
              </>
            ) : (
              // Not logged in state
              <button
                onClick={() => window.location.href = '/login'}
                className="px-4 py-2 bg-primary text-white rounded-lg font-medium text-sm hover:bg-primary-dark transition-colors shadow-sm"
              >
                {t('header.login')}
              </button>
            )}
          </div>
        </div>
      </header>

      <main className="app-main">
        <ChampionshipSelector
          championships={championships}
          selectedChampionship={selectedChampionship}
          onSelect={handleChampionshipChange}
        />

        {selectedChampionship && (
          <RaceList championshipId={selectedChampionship.id} />
        )}
      </main>

      <footer className="app-footer">
        <p>{t('app.footer')}</p>
      </footer>
    </div>
  )
}

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/race/:raceId" element={<RaceDetail />} />
        <Route path="/championship/:championshipId/results" element={<ChampionshipResults />} />
        <Route path="/rider/:riderId" element={<RiderDetail />} />
        <Route path="/login" element={<Login />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Router>
  )
}

export default App

