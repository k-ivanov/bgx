/**
 * Language Synchronization Utility
 * Syncs language preferences between frontend (i18next) and backend (Django)
 */

import i18n from '../i18n/config'
import { setLanguage as setApiLanguage, getLanguage as getApiLanguage } from '../api/api'

/**
 * Get language from Django cookie
 */
export const getLanguageFromCookie = () => {
  const cookies = document.cookie.split(';')
  for (let cookie of cookies) {
    const [name, value] = cookie.trim().split('=')
    if (name === 'django_language') {
      return value
    }
  }
  return null
}

/**
 * Set language in Django cookie
 */
export const setLanguageCookie = (language) => {
  document.cookie = `django_language=${language};path=/;max-age=31536000;SameSite=Lax`
}

/**
 * Sync language preference on app initialization
 * Priority: Django cookie > localStorage > browser language > default (en)
 */
export const syncLanguageOnInit = async () => {
  try {
    // Check Django cookie first
    const cookieLang = getLanguageFromCookie()
    
    if (cookieLang && (cookieLang === 'en' || cookieLang === 'bg')) {
      // Use cookie language if valid
      if (i18n.language !== cookieLang) {
        await i18n.changeLanguage(cookieLang)
      }
      console.log(`Language synced from cookie: ${cookieLang}`)
      return cookieLang
    }
    
    // Otherwise, get backend preference
    try {
      const response = await getApiLanguage()
      const backendLang = response.language
      
      if (backendLang && i18n.language !== backendLang) {
        await i18n.changeLanguage(backendLang)
        setLanguageCookie(backendLang)
        console.log(`Language synced from backend: ${backendLang}`)
      }
      
      return backendLang
    } catch (error) {
      // Backend not available, use frontend default
      console.log('Backend language sync failed, using frontend default')
      const currentLang = i18n.language || 'en'
      setLanguageCookie(currentLang)
      return currentLang
    }
  } catch (error) {
    console.error('Language sync error:', error)
    return i18n.language || 'en'
  }
}

/**
 * Change language and sync with backend
 */
export const changeLanguage = async (language) => {
  try {
    // Validate language
    if (!['en', 'bg'].includes(language)) {
      console.error(`Invalid language: ${language}`)
      return false
    }
    
    // Change frontend language
    await i18n.changeLanguage(language)
    
    // Set cookie locally
    setLanguageCookie(language)
    
    // Sync with backend
    try {
      await setApiLanguage(language)
      console.log(`Language synced: ${language}`)
    } catch (error) {
      console.warn('Failed to sync language with backend:', error)
      // Continue anyway, language is set in frontend
    }
    
    return true
  } catch (error) {
    console.error('Failed to change language:', error)
    return false
  }
}

/**
 * Get current active language
 */
export const getCurrentLanguage = () => {
  return i18n.language || getLanguageFromCookie() || 'en'
}

