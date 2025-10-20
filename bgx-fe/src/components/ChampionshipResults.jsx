import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { getRaces, getChampionships } from '../api/api'
import axios from 'axios'
import './ChampionshipResults.css'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api'

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

function ChampionshipResults() {
  const { championshipId } = useParams()
  const navigate = useNavigate()
  const { t } = useTranslation()
  
  const [championship, setChampionship] = useState(null)
  const [selectedCategory, setSelectedCategory] = useState('expert')
  const [results, setResults] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    loadChampionshipData()
  }, [championshipId])

  useEffect(() => {
    if (championship) {
      loadResults()
    }
  }, [selectedCategory, championship])

  const loadChampionshipData = async () => {
    try {
      setLoading(true)
      setError(null)
      const championships = await getChampionships()
      const champ = championships.find(c => c.id === parseInt(championshipId))
      setChampionship(champ)
    } catch (err) {
      setError(t('common.error'))
      console.error('Error loading championship:', err)
    } finally {
      setLoading(false)
    }
  }

  const loadResults = async () => {
    try {
      // Get overall championship results
      const response = await axios.get(
        `${API_BASE_URL}/results/championship-results/`,
        { 
          params: { 
            championship: championshipId,
            category: selectedCategory 
          },
          withCredentials: true 
        }
      )
      // Handle both paginated and non-paginated responses
      const data = Array.isArray(response.data) ? response.data : response.data.results || []
      // Sort by total points (highest first)
      const sortedData = data.sort((a, b) => (b.total_points || 0) - (a.total_points || 0))
      setResults(sortedData)
    } catch (err) {
      console.error('Error loading results:', err)
      setResults([])
    }
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

  if (error || !championship) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="bg-white rounded-lg p-8 max-w-md text-center shadow-lg">
          <h2 className="text-2xl font-bold text-red-600 mb-4">⚠️ {t('common.error')}</h2>
          <p className="text-gray-700 mb-6">{error || t('championship.notFound')}</p>
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
              <h1 className="text-3xl font-bold text-gray-900 mb-2">
                🏆 {championship.name} - {t('championship.overallStandings')}
              </h1>
              <div className="flex flex-wrap gap-4 text-gray-600">
                <span className="flex items-center">
                  <span className="mr-2">📅</span>
                  {championship.year}
                </span>
                <span className="flex items-center">
                  <span className="mr-2">📍</span>
                  {new Date(championship.start_date).toLocaleDateString()} - {new Date(championship.end_date).toLocaleDateString()}
                </span>
              </div>
            </div>
          </div>
          {championship.description && (
            <p className="mt-4 text-gray-600">{championship.description}</p>
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
              {t('championship.standings')} - {t(`category.${selectedCategory}`)}
            </h2>
            <p className="text-sm text-gray-600 mt-1">
              {t('championship.overallDescription')}
            </p>
            {championship.status === 'completed' && (
              <div className="mt-2 p-2 bg-blue-50 border border-blue-200 rounded">
                <p className="text-xs text-blue-800">
                  ℹ️ {t('championship.dropLowestScoreRule')}
                </p>
              </div>
            )}
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
                      {t('championship.totalPoints')}
                    </th>
                    <th className="px-6 py-4 text-center text-xs font-semibold text-gray-600 uppercase tracking-wider">
                      {t('championship.racesParticipated')}
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200">
                  {results.map((result, index) => (
                    <tr
                      key={result.rider_id || index}
                      className={`hover:bg-gray-50 transition ${
                        index < 3 ? 'bg-yellow-50' : ''
                      }`}
                    >
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center">
                          {index + 1 <= 3 && (
                            <span className="text-2xl mr-2">
                              {index + 1 === 1 && '🥇'}
                              {index + 1 === 2 && '🥈'}
                              {index + 1 === 3 && '🥉'}
                            </span>
                          )}
                          <span className="text-lg font-bold text-gray-900">
                            {index + 1}
                          </span>
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <div className="text-sm font-semibold text-gray-900">
                          {result.rider_name || 'Unknown Rider'}
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <div className="text-sm text-gray-600">
                          {result.rider_club || '-'}
                        </div>
                      </td>
                      <td className="px-6 py-4 text-center">
                        <div className="flex flex-col items-center gap-1">
                          <span className="inline-flex items-center px-4 py-2 rounded-md text-base font-bold bg-blue-50 text-blue-700 border-2 border-blue-200">
                            {result.total_points || 0} pts
                          </span>
                          {result.lowest_score_dropped > 0 && (
                            <span className="text-xs text-gray-500">
                              ({t('championship.dropped')}: {result.lowest_score_dropped} pts)
                            </span>
                          )}
                        </div>
                      </td>
                      <td className="px-6 py-4 text-center">
                        <span className="text-sm text-gray-600">
                          {result.races_participated || 0} {t('championship.races')}
                        </span>
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

export default ChampionshipResults

