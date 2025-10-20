import { useState, useEffect } from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import ChampionshipSelector from './components/ChampionshipSelector'
import RaceList from './components/RaceList'
import RaceDetail from './components/RaceDetail'
import Register from './components/Register'
import Activate from './components/Activate'
import LanguageSwitcher from './components/LanguageSwitcher'
import { getChampionships } from './api/api'
import { syncLanguageOnInit } from './utils/languageSync'
import './App.css'

function HomePage() {
  const { t } = useTranslation()
  const [championships, setChampionships] = useState([])
  const [selectedChampionship, setSelectedChampionship] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
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
        <div className="flex justify-between items-center max-w-7xl mx-auto px-4">
          <div>
            <h1>🏍️ {t('app.title')}</h1>
            <p>{t('app.subtitle')}</p>
          </div>
          <div className="flex gap-3 items-center">
            <LanguageSwitcher />
            <button
              onClick={() => window.location.href = '/register'}
              className="px-4 py-2 bg-primary text-white rounded-lg font-semibold hover:bg-primary-dark transition shadow-sm"
            >
              {t('header.register')}
            </button>
            <button
              onClick={() => window.location.href = '/activate'}
              className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg font-semibold hover:bg-gray-50 transition"
            >
              {t('header.activate')}
            </button>
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
        <Route path="/register" element={<Register />} />
        <Route path="/activate" element={<Activate />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Router>
  )
}

export default App

