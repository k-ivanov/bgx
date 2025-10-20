import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { getRace, getRaceDayResults, getRaceResults } from '../api/api'
import './RaceDetail.css'

const CATEGORIES = [
  'expert',
  'profi',
  'junior',
  'standard',
  'standard_junior',
  'seniors_40',
  'seniors_50',
  'women',
]

function RaceDetail() {
  const { raceId } = useParams()
  const navigate = useNavigate()
  const { t } = useTranslation()
  
  const [race, setRace] = useState(null)
  const [selectedCategory, setSelectedCategory] = useState('expert')
  const [results, setResults] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    loadRaceData()
  }, [raceId])

  useEffect(() => {
    if (race) {
      loadResults()
    }
  }, [selectedCategory, race])

  const loadRaceData = async () => {
    try {
      setLoading(true)
      setError(null)
      const raceData = await getRace(raceId)
      setRace(raceData)
    } catch (err) {
      setError(t('common.error'))
      console.error('Error loading race:', err)
    } finally {
      setLoading(false)
    }
  }

  const loadResults = async () => {
    try {
      // Try to get overall race results first
      const raceResults = await getRaceResults(raceId, selectedCategory)
      setResults(raceResults)
    } catch (err) {
      console.error('Error loading results:', err)
      setResults([])
    }
  }

  const getStatusBadge = (status) => {
    const badges = {
      'upcoming': { color: 'bg-blue-100 text-blue-800' },
      'ongoing': { color: 'bg-orange-100 text-orange-800' },
      'completed': { color: 'bg-green-100 text-green-800' },
      'cancelled': { color: 'bg-red-100 text-red-800' },
    }
    const badge = badges[status] || { color: 'bg-gray-100 text-gray-800' }
    
    return (
      <span className={`inline-block px-3 py-1 rounded-md text-xs font-semibold uppercase ${badge.color}`}>
        {t(`race.status.${status}`)}
      </span>
    )
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="spinner-large mb-4"></div>
          <p className="text-xl text-gray-700">{t('common.loading')}</p>
        </div>
      </div>
    )
  }

  if (error || !race) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="bg-white rounded-lg p-8 max-w-md text-center shadow-lg">
          <h2 className="text-2xl font-bold text-red-600 mb-4">⚠️ {t('common.error')}</h2>
          <p className="text-gray-700 mb-6">{error || t('race.notFound')}</p>
          <button
            onClick={() => navigate('/')}
            className="px-6 py-2 bg-primary text-white rounded-md hover:bg-primary-dark transition"
          >
            ← {t('race.backToChampionships')}
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <button
            onClick={() => navigate('/')}
            className="text-primary hover:text-primary-dark mb-4 inline-flex items-center transition font-medium"
          >
            ← {t('race.backToChampionships')}
          </button>
          <div className="flex justify-between items-start">
            <div className="flex-1">
              <h1 className="text-3xl font-bold text-gray-900 mb-2">{race.name}</h1>
              <div className="flex flex-wrap gap-4 text-gray-600">
                <span className="flex items-center">
                  <span className="mr-2">📍</span>
                  {race.location}
                </span>
                <span className="flex items-center">
                  <span className="mr-2">📅</span>
                  {new Date(race.start_date).toLocaleDateString()} - {new Date(race.end_date).toLocaleDateString()}
                </span>
              </div>
            </div>
            <div>{getStatusBadge(race.status)}</div>
          </div>
          {race.description && (
            <p className="mt-4 text-gray-600">{race.description}</p>
          )}
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 py-8">
        {/* Category Selector */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6">
          <h2 className="text-xl font-bold text-gray-900 mb-4">{t('race.selectCategory')}</h2>
          <div className="grid grid-cols-2 sm:grid-cols-4 md:grid-cols-8 gap-3">
            {CATEGORIES.map((category) => (
              <button
                key={category}
                onClick={() => setSelectedCategory(category)}
                className={`px-4 py-3 rounded-lg font-semibold transition-all ${
                  selectedCategory === category
                    ? 'bg-primary text-white shadow-sm'
                    : 'bg-gray-50 text-gray-700 hover:bg-gray-100 border border-gray-200'
                }`}
              >
                {t(`category.${category}`)}
              </button>
            ))}
          </div>
        </div>

        {/* Results Table */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
          <div className="px-6 py-4 bg-gray-50 border-b border-gray-200">
            <h2 className="text-xl font-bold text-gray-900">
              {t('race.results')} - {t(`category.${selectedCategory}`)}
            </h2>
          </div>

          {results.length === 0 ? (
            <div className="p-12 text-center text-gray-500">
              <p className="text-lg">🏁 {t('race.noResults')}</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50 border-b-2 border-gray-200">
                  <tr>
                    <th className="px-6 py-4 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
                      {t('race.table.position')}
                    </th>
                    <th className="px-6 py-4 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
                      {t('race.table.rider')}
                    </th>
                    <th className="px-6 py-4 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
                      {t('race.table.club')}
                    </th>
                    <th className="px-6 py-4 text-center text-xs font-semibold text-gray-600 uppercase tracking-wider">
                      {t('race.table.points')}
                    </th>
                    <th className="px-6 py-4 text-center text-xs font-semibold text-gray-600 uppercase tracking-wider">
                      {t('race.table.time')}
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200">
                  {results.map((result, index) => (
                    <tr
                      key={result.id}
                      className={`hover:bg-gray-50 transition ${
                        index < 3 ? 'bg-yellow-50' : ''
                      }`}
                    >
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center">
                          {result.overall_position <= 3 && (
                            <span className="text-2xl mr-2">
                              {result.overall_position === 1 && '🥇'}
                              {result.overall_position === 2 && '🥈'}
                              {result.overall_position === 3 && '🥉'}
                            </span>
                          )}
                          <span className="text-lg font-bold text-gray-900">
                            {result.overall_position}
                          </span>
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <button
                          onClick={() => navigate(`/rider/${result.rider}`)}
                          className="text-sm font-semibold text-primary hover:text-primary-dark transition text-left"
                        >
                          {result.rider_name || 'Unknown Rider'}
                        </button>
                      </td>
                      <td className="px-6 py-4">
                        <div className="text-sm text-gray-600">
                          {result.rider_club || '-'}
                        </div>
                      </td>
                      <td className="px-6 py-4 text-center">
                        <span className="inline-flex items-center px-3 py-1 rounded-md text-sm font-semibold bg-blue-50 text-blue-700 border border-blue-200">
                          {result.total_points} pts
                        </span>
                      </td>
                      <td className="px-6 py-4 text-center text-sm text-gray-600">
                        {result.total_time || '-'}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </main>
    </div>
  )
}

export default RaceDetail

