import i18n from 'i18next'
import { initReactI18next } from 'react-i18next'
import LanguageDetector from 'i18next-browser-languagedetector'

import enTranslations from './locales/en.json'
import bgTranslations from './locales/bg.json'

// Custom language detector that also checks Django cookie
const djangoCookieDetector = {
  name: 'djangoCookie',
  lookup() {
    // Check for Django's language cookie
    const cookies = document.cookie.split(';')
    for (let cookie of cookies) {
      const [name, value] = cookie.trim().split('=')
      if (name === 'django_language') {
        return value
      }
    }
    return null
  },
  cacheUserLanguage(lng) {
    // Set cookie for Django (will be synced with backend)
    document.cookie = `django_language=${lng};path=/;max-age=31536000;SameSite=Lax`
  }
}

i18n
  .use(LanguageDetector) // Detect user language
  .use(initReactI18next) // Passes i18n down to react-i18next
  .init({
    resources: {
      en: {
        translation: enTranslations
      },
      bg: {
        translation: bgTranslations
      }
    },
    fallbackLng: 'en',
    interpolation: {
      escapeValue: false // React already escapes values
    },
    detection: {
      order: ['djangoCookie', 'cookie', 'localStorage', 'navigator'],
      lookupCookie: 'django_language',
      lookupLocalStorage: 'i18nextLng',
      caches: ['localStorage', 'cookie'],
      cookieOptions: { path: '/', sameSite: 'lax' }
    }
  })

// Register custom detector
const languageDetector = i18n.services.languageDetector
languageDetector.addDetector(djangoCookieDetector)

export default i18n

