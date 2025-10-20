import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { getRider, getRiderResults, getRiderChampionshipResults } from '../api/api'
import './RiderDetail.css'

function RiderDetail() {
  const { riderId } = useParams()
  const navigate = useNavigate()
  const { t } = useTranslation()
  
  const [rider, setRider] = useState(null)
  const [raceResults, setRaceResults] = useState([])
  const [championshipResults, setChampionshipResults] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [activeTab, setActiveTab] = useState('races') // 'races' or 'championships'

  useEffect(() => {
    loadRiderData()
  }, [riderId])

  const loadRiderData = async () => {
    try {
      setLoading(true)
      setError(null)
      
      // Load rider info
      const riderData = await getRider(riderId)
      setRider(riderData)
      
      // Load race results
      const raceResultsData = await getRiderResults(riderId)
      setRaceResults(raceResultsData)
      
      // Load championship results
      const championshipResultsData = await getRiderChampionshipResults(riderId)
      setChampionshipResults(championshipResultsData)
      
    } catch (err) {
      setError(t('common.error'))
      console.error('Error loading rider:', err)
    } finally {
      setLoading(false)
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

  if (error || !rider) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="bg-white rounded-lg p-8 max-w-md text-center shadow-lg">
          <h2 className="text-2xl font-bold text-red-600 mb-4">⚠️ {t('common.error')}</h2>
          <p className="text-gray-700 mb-6">{error || t('rider.notFound')}</p>
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
            onClick={() => navigate(-1)}
            className="text-primary hover:text-primary-dark mb-4 inline-flex items-center transition font-medium"
          >
            ← {t('common.back')}
          </button>
          
          <div className="flex items-start gap-6">
            {/* Avatar */}
            <div className="flex-shrink-0">
              <div className="w-24 h-24 rounded-full bg-gradient-to-br from-primary to-primary-dark flex items-center justify-center text-white text-3xl font-bold shadow-lg">
                {rider.first_name[0]}{rider.last_name[0]}
              </div>
            </div>
            
            {/* Rider Info */}
            <div className="flex-1">
              <h1 className="text-3xl font-bold text-gray-900 mb-2">
                {rider.first_name} {rider.last_name}
              </h1>
              
              <div className="flex flex-wrap gap-4 text-gray-600">
                {rider.club_name && (
                  <span className="flex items-center">
                    <span className="mr-2">🏁</span>
                    {rider.club_name}
                  </span>
                )}
                
                {rider.license_number && (
                  <span className="flex items-center">
                    <span className="mr-2">🎫</span>
                    {t('rider.license')}: {rider.license_number}
                  </span>
                )}
                
                {rider.is_licensed && (
                  <span className="inline-flex items-center px-2 py-1 rounded text-xs font-semibold bg-green-50 text-green-700 border border-green-200">
                    ✓ {t('rider.licensed')}
                  </span>
                )}
              </div>
              
              {rider.bio && (
                <p className="mt-4 text-gray-600">{rider.bio}</p>
              )}
            </div>
            
            {/* Stats */}
            <div className="flex gap-4">
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 text-center">
                <div className="text-2xl font-bold text-blue-700">{raceResults.length}</div>
                <div className="text-xs text-blue-600">{t('rider.totalRaces')}</div>
              </div>
              <div className="bg-purple-50 border border-purple-200 rounded-lg p-4 text-center">
                <div className="text-2xl font-bold text-purple-700">{championshipResults.length}</div>
                <div className="text-xs text-purple-600">{t('rider.championships')}</div>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Tabs */}
      <div className="max-w-7xl mx-auto px-4 mt-6">
        <div className="bg-white rounded-lg shadow-sm border border-gray-200">
          <div className="border-b border-gray-200">
            <nav className="flex">
              <button
                onClick={() => setActiveTab('races')}
                className={`px-6 py-4 text-sm font-semibold transition ${
                  activeTab === 'races'
                    ? 'text-primary border-b-2 border-primary'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                🏁 {t('rider.raceResults')} ({raceResults.length})
              </button>
              <button
                onClick={() => setActiveTab('championships')}
                className={`px-6 py-4 text-sm font-semibold transition ${
                  activeTab === 'championships'
                    ? 'text-primary border-b-2 border-primary'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                🏆 {t('rider.championshipStandings')} ({championshipResults.length})
              </button>
            </nav>
          </div>

          {/* Race Results Tab */}
          {activeTab === 'races' && (
            <div className="p-6">
              {raceResults.length === 0 ? (
                <div className="text-center py-12 text-gray-500">
                  <p className="text-lg">🏁 {t('rider.noRaceResults')}</p>
                </div>
              ) : (
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead className="bg-gray-50 border-b-2 border-gray-200">
                      <tr>
                        <th className="px-6 py-4 text-left text-xs font-semibold text-gray-600 uppercase">
                          {t('race.table.name')}
                        </th>
                        <th className="px-6 py-4 text-left text-xs font-semibold text-gray-600 uppercase">
                          {t('category.title')}
                        </th>
                        <th className="px-6 py-4 text-center text-xs font-semibold text-gray-600 uppercase">
                          {t('race.table.position')}
                        </th>
                        <th className="px-6 py-4 text-center text-xs font-semibold text-gray-600 uppercase">
                          {t('race.table.points')}
                        </th>
                        <th className="px-6 py-4 text-center text-xs font-semibold text-gray-600 uppercase">
                          {t('race.table.time')}
                        </th>
                        <th className="px-6 py-4 text-right text-xs font-semibold text-gray-600 uppercase">
                          {t('race.table.action')}
                        </th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-200">
                      {raceResults.map((result) => (
                        <tr key={result.id} className="hover:bg-gray-50 transition">
                          <td className="px-6 py-4">
                            <div className="text-sm font-semibold text-gray-900">
                              {result.race_name}
                            </div>
                          </td>
                          <td className="px-6 py-4">
                            <span className="inline-flex items-center px-2 py-1 rounded text-xs font-semibold bg-gray-100 text-gray-700">
                              {t(`category.${result.category}`)}
                            </span>
                          </td>
                          <td className="px-6 py-4 text-center">
                            <div className="flex items-center justify-center">
                              {result.overall_position <= 3 && (
                                <span className="text-xl mr-2">
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
                          <td className="px-6 py-4 text-center">
                            <span className="inline-flex items-center px-3 py-1 rounded-md text-sm font-semibold bg-blue-50 text-blue-700 border border-blue-200">
                              {result.total_points} pts
                            </span>
                          </td>
                          <td className="px-6 py-4 text-center text-sm text-gray-600">
                            {result.total_time || '-'}
                          </td>
                          <td className="px-6 py-4 text-right">
                            <button
                              onClick={() => navigate(`/race/${result.race}`)}
                              className="text-primary hover:text-primary-dark font-medium text-sm"
                            >
                              {t('race.viewDetails')} →
                            </button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          )}

          {/* Championship Results Tab */}
          {activeTab === 'championships' && (
            <div className="p-6">
              {championshipResults.length === 0 ? (
                <div className="text-center py-12 text-gray-500">
                  <p className="text-lg">🏆 {t('rider.noChampionshipResults')}</p>
                </div>
              ) : (
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead className="bg-gray-50 border-b-2 border-gray-200">
                      <tr>
                        <th className="px-6 py-4 text-left text-xs font-semibold text-gray-600 uppercase">
                          {t('championship.title')}
                        </th>
                        <th className="px-6 py-4 text-left text-xs font-semibold text-gray-600 uppercase">
                          {t('category.title')}
                        </th>
                        <th className="px-6 py-4 text-center text-xs font-semibold text-gray-600 uppercase">
                          {t('championship.totalPoints')}
                        </th>
                        <th className="px-6 py-4 text-center text-xs font-semibold text-gray-600 uppercase">
                          {t('championship.racesParticipated')}
                        </th>
                        <th className="px-6 py-4 text-right text-xs font-semibold text-gray-600 uppercase">
                          {t('race.table.action')}
                        </th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-200">
                      {championshipResults.map((result) => (
                        <tr key={result.id} className="hover:bg-gray-50 transition">
                          <td className="px-6 py-4">
                            <div className="text-sm font-semibold text-gray-900">
                              {result.championship_name}
                            </div>
                            {result.championship_status === 'completed' && result.lowest_score_dropped > 0 && (
                              <div className="text-xs text-gray-500 mt-1">
                                {t('championship.dropped')}: {result.lowest_score_dropped} pts
                              </div>
                            )}
                          </td>
                          <td className="px-6 py-4">
                            <span className="inline-flex items-center px-2 py-1 rounded text-xs font-semibold bg-gray-100 text-gray-700">
                              {t(`category.${result.category}`)}
                            </span>
                          </td>
                          <td className="px-6 py-4 text-center">
                            <span className="inline-flex items-center px-4 py-2 rounded-md text-base font-bold bg-blue-50 text-blue-700 border-2 border-blue-200">
                              {result.total_points} pts
                            </span>
                          </td>
                          <td className="px-6 py-4 text-center text-sm text-gray-600">
                            {result.races_participated} {t('championship.races')}
                          </td>
                          <td className="px-6 py-4 text-right">
                            <button
                              onClick={() => navigate(`/championship/${result.championship}/results`)}
                              className="text-primary hover:text-primary-dark font-medium text-sm"
                            >
                              {t('championship.viewStandings')} →
                            </button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default RiderDetail

