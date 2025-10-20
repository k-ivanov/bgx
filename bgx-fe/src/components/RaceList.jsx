import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { getRaces } from '../api/api'
import './RaceList.css'

function RaceList({ championshipId }) {
  const navigate = useNavigate()
  const { t } = useTranslation()
  const [races, setRaces] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    if (championshipId) {
      loadRaces()
    }
  }, [championshipId])

  const loadRaces = async () => {
    try {
      setLoading(true)
      setError(null)
      const data = await getRaces({ championships__id: championshipId })
      // Sort by start date
      const sortedRaces = data.sort((a, b) => 
        new Date(a.start_date) - new Date(b.start_date)
      )
      setRaces(sortedRaces)
    } catch (err) {
      setError('Failed to load races')
      console.error('Error loading races:', err)
    } finally {
      setLoading(false)
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
      <span className={`inline-flex items-center px-2 py-1 rounded text-xs font-semibold ${badge.color}`}>
        {t(`race.status.${status}`)}
      </span>
    )
  }

  const formatDateRange = (startDate, endDate) => {
    const start = new Date(startDate)
    const end = new Date(endDate)
    
    if (start.toDateString() === end.toDateString()) {
      return start.toLocaleDateString('en-US', { 
        month: 'short', 
        day: 'numeric', 
        year: 'numeric' 
      })
    }
    
    return `${start.toLocaleDateString('en-US', { 
      month: 'short', 
      day: 'numeric' 
    })} - ${end.toLocaleDateString('en-US', { 
      month: 'short', 
      day: 'numeric', 
      year: 'numeric' 
    })}`
  }

  if (loading) {
    return (
      <div className="race-list">
        <div className="race-list-loading">
          <div className="spinner-small"></div>
          <p>{t('common.loading')}</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="race-list">
        <div className="race-list-error">
          <p>{error}</p>
          <button onClick={loadRaces}>{t('common.retry')}</button>
        </div>
      </div>
    )
  }

  return (
    <div className="race-list">
      <div className="race-list-header">
        <div className="flex items-center gap-3">
          <h2>🏁 {t('race.title')}</h2>
          <span className="race-count">{t('race.count', { count: races.length })}</span>
        </div>
        <button
          onClick={() => navigate(`/championship/${championshipId}/results`)}
          className="px-4 py-2 bg-accent text-white rounded-lg font-semibold hover:bg-accent-dark transition shadow-sm flex items-center gap-2"
        >
          🏆 {t('championship.viewOverallResults')}
        </button>
      </div>

      {races.length === 0 ? (
        <div className="empty-races">
          <p>🏁 {t('race.noRaces')}</p>
        </div>
      ) : (
        <div className="race-table-container">
          <table className="race-table">
            <thead>
              <tr>
                <th className="text-left">{t('race.table.name')}</th>
                <th className="text-left">{t('race.table.location')}</th>
                <th className="text-left">{t('race.table.dates')}</th>
                <th className="text-center">{t('race.table.status')}</th>
                <th className="text-center">{t('race.table.registration')}</th>
                <th className="text-right">{t('race.table.action')}</th>
              </tr>
            </thead>
            <tbody>
              {races.map((race) => (
                <tr 
                  key={race.id} 
                  className="race-row"
                  onClick={() => navigate(`/race/${race.id}`)}
                >
                  <td className="race-name">
                    <div className="font-semibold text-gray-900">{race.name}</div>
                    {race.description && (
                      <div className="text-sm text-gray-500 mt-1 line-clamp-1">{race.description}</div>
                    )}
                  </td>
                  <td className="race-location">
                    <div className="flex items-center text-gray-700">
                      <span className="mr-1">📍</span>
                      {race.location}
                    </div>
                  </td>
                  <td className="race-dates">
                    <div className="text-gray-700">
                      {formatDateRange(race.start_date, race.end_date)}
                    </div>
                    {race.registration_deadline && (
                      <div className="text-xs text-gray-500 mt-1">
                        {t('race.table.deadline')}: {new Date(race.registration_deadline).toLocaleDateString()}
                      </div>
                    )}
                  </td>
                  <td className="race-status text-center">
                    {getStatusBadge(race.status)}
                  </td>
                  <td className="race-registration text-center">
                    {race.registration_open ? (
                      <span className="inline-flex items-center px-2 py-1 rounded text-xs font-semibold bg-green-50 text-green-700 border border-green-200">
                        ✓ {t('race.registration.open')}
                      </span>
                    ) : (
                      <span className="inline-flex items-center px-2 py-1 rounded text-xs font-semibold bg-gray-50 text-gray-500">
                        {t('race.registration.closed')}
                      </span>
                    )}
                  </td>
                  <td className="race-action text-right">
                    <button 
                      className="race-details-btn"
                      onClick={(e) => {
                        e.stopPropagation()
                        navigate(`/race/${race.id}`)
                      }}
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
  )
}

export default RaceList

