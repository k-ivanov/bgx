import { useTranslation } from 'react-i18next'
import { setLanguage as setApiLanguage } from '../api/api'
import './LanguageSwitcher.css'

function LanguageSwitcher() {
  const { i18n } = useTranslation()

  const changeLanguage = async (lng) => {
    try {
      // Change language in frontend
      await i18n.changeLanguage(lng)
      
      // Sync with backend API
      await setApiLanguage(lng)
      
      console.log(`Language changed to: ${lng}`)
    } catch (error) {
      console.error('Failed to change language:', error)
      // Still change frontend language even if backend sync fails
      await i18n.changeLanguage(lng)
    }
  }

  return (
    <div className="language-switcher">
      <button
        onClick={() => changeLanguage('en')}
        className={`lang-btn ${i18n.language === 'en' ? 'active' : ''}`}
        title="English"
      >
        EN
      </button>
      <span className="lang-divider">|</span>
      <button
        onClick={() => changeLanguage('bg')}
        className={`lang-btn ${i18n.language === 'bg' ? 'active' : ''}`}
        title="Български"
      >
        BG
      </button>
    </div>
  )
}

export default LanguageSwitcher

