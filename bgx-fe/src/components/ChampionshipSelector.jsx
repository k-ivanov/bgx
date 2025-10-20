import { useTranslation } from 'react-i18next'
import './ChampionshipSelector.css'

function ChampionshipSelector({ championships, selectedChampionship, onSelect }) {
  const { t } = useTranslation()
  const handleChange = (e) => {
    const championshipId = parseInt(e.target.value)
    const championship = championships.find(c => c.id === championshipId)
    if (championship) {
      onSelect(championship)
    }
  }

  const getStatusBadge = (status) => {
    const badges = {
      'upcoming': { color: 'bg-blue-100 text-blue-800' },
      'active': { color: 'bg-green-100 text-green-800' },
      'completed': { color: 'bg-gray-100 text-gray-800' },
    }
    const badge = badges[status] || { color: 'bg-gray-100 text-gray-800' }
    
    return (
      <span className={`inline-flex items-center px-2 py-1 rounded text-xs font-semibold ${badge.color}`}>
        {t(`championship.status.${status}`)}
      </span>
    )
  }

  if (championships.length === 0) {
    return (
      <div className="championship-selector">
        <div className="empty-state">
          <p className="text-gray-500">📅 {t('championship.noChampionships')}</p>
        </div>
      </div>
    )
  }

  return (
    <div className="championship-selector">
      <div className="flex items-center justify-between gap-4">
        <div className="flex items-center gap-3 flex-1">
          <label htmlFor="championship-select" className="text-sm font-semibold text-gray-700 whitespace-nowrap">
            🏆 {t('championship.select')}:
          </label>
          <select
            id="championship-select"
            value={selectedChampionship?.id || ''}
            onChange={handleChange}
            className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent bg-white text-gray-900 font-medium cursor-pointer"
          >
            <option value="" disabled>{t('championship.selectPlaceholder')}</option>
            {championships.map((championship) => (
              <option key={championship.id} value={championship.id}>
                {championship.name} ({championship.year})
              </option>
            ))}
          </select>
        </div>
        
        {selectedChampionship && (
          <div className="flex items-center gap-3">
            {getStatusBadge(selectedChampionship.status)}
            <span className="text-sm text-gray-500 whitespace-nowrap">
              {new Date(selectedChampionship.start_date).toLocaleDateString()} - {new Date(selectedChampionship.end_date).toLocaleDateString()}
            </span>
          </div>
        )}
      </div>
    </div>
  )
}

export default ChampionshipSelector

