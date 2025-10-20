# Language Synchronization Guide

This guide explains how language preferences are synchronized between the BGX Racing Platform frontend (React) and backend (Django).

## Overview

The application uses **cookie-based language synchronization** to ensure consistent language preferences across frontend and backend.

### Cookie Used: `django_language`

- **Set by:** Both frontend and backend
- **Path:** `/` (site-wide)
- **Max Age:** 1 year (31536000 seconds)
- **SameSite:** `Lax` (secure, works across subdomains)

## How It Works

### 1. Language Detection Priority

When the app loads, it detects the user's language in this order:

1. **Django cookie** (`django_language`) - Highest priority
2. **Browser cookie** (set by i18next)
3. **localStorage** (`i18nextLng`)
4. **Browser language** (Accept-Language)
5. **Default:** English (`en`)

### 2. Language Switching Flow

```
User clicks language button (EN/BG)
    ↓
Frontend: i18n.changeLanguage(lng)
    ↓
Frontend: Set django_language cookie
    ↓
Backend API: POST /api/set-language/
    ↓
Backend: Validate & activate language
    ↓
Backend: Set django_language cookie (1 year)
    ↓
Both cookies sync = Language persists
```

### 3. On App Initialization

```javascript
// App.jsx
useEffect(() => {
  syncLanguageOnInit().then(() => {
    // Load app data after language is synced
  })
}, [])
```

The `syncLanguageOnInit()` function:
1. Checks `django_language` cookie
2. If not found, calls `/api/get-language/`
3. Syncs frontend with backend language
4. Sets cookie for future visits

## Implementation Details

### Frontend (React)

#### API Client Configuration (`api/api.js`)

```javascript
const api = axios.create({
  baseURL: 'http://localhost:8000/api',
  withCredentials: true, // Enable cookie sending/receiving
})

// Add Accept-Language header to all requests
api.interceptors.request.use((config) => {
  const language = getLanguageFromCookie() || 'en'
  config.headers['Accept-Language'] = language
  return config
})
```

#### i18next Configuration (`i18n/config.js`)

```javascript
i18n.init({
  detection: {
    order: ['djangoCookie', 'cookie', 'localStorage', 'navigator'],
    lookupCookie: 'django_language',
    caches: ['localStorage', 'cookie'],
    cookieOptions: { path: '/', sameSite: 'lax' }
  }
})
```

#### Language Utilities (`utils/languageSync.js`)

- `syncLanguageOnInit()` - Initialize language on app load
- `changeLanguage(lng)` - Change language and sync with backend
- `getLanguageFromCookie()` - Read django_language cookie
- `setLanguageCookie(lng)` - Write django_language cookie
- `getCurrentLanguage()` - Get active language

#### Language Switcher (`components/LanguageSwitcher.jsx`)

```javascript
const changeLanguage = async (lng) => {
  // Change frontend
  await i18n.changeLanguage(lng)
  
  // Sync with backend
  await setApiLanguage(lng)
}
```

### Backend (Django)

#### Settings (`bgx_api/settings.py`)

```python
MIDDLEWARE = [
    'django.middleware.locale.LocaleMiddleware',  # Language detection
    # ...
]

LANGUAGES = [
    ('en', 'English'),
    ('bg', 'Български'),
]

LOCALE_PATHS = [BASE_DIR / 'locale']

# Enable cookie credentials
CORS_ALLOW_CREDENTIALS = True
SESSION_COOKIE_SAMESITE = 'Lax'
```

#### API Endpoints (`bgx_api/views.py`)

**Set Language:**
```python
@csrf_exempt
@require_POST
def set_language(request):
    lang_code = data.get('language', 'en')
    translation.activate(lang_code)
    
    response = JsonResponse({'status': 'success', 'language': lang_code})
    response.set_cookie(
        'django_language',
        lang_code,
        max_age=365 * 24 * 60 * 60,  # 1 year
        path='/',
        samesite='Lax'
    )
    return response
```

**Get Language:**
```python
def get_language(request):
    current_language = translation.get_language()
    return JsonResponse({'language': current_language})
```

## Testing

### Test Language Synchronization

1. **Open browser DevTools** → Application → Cookies
2. **Click EN button:**
   - Check cookie: `django_language=en`
   - Check localStorage: `i18nextLng=en`
3. **Click BG button:**
   - Check cookie: `django_language=bg`
   - Check localStorage: `i18nextLng=bg`
4. **Refresh page:**
   - Language should persist
5. **Check API requests:**
   - Headers should include `Accept-Language: bg` (or `en`)
6. **Close and reopen browser:**
   - Language should still be `bg` (cookie persists)

### Test API Responses

```bash
# Set language to Bulgarian
curl -X POST http://localhost:8000/api/set-language/ \
  -H "Content-Type: application/json" \
  -d '{"language": "bg"}' \
  -c cookies.txt \
  -v

# Check cookie is set
grep django_language cookies.txt

# Test API with cookie
curl http://localhost:8000/api/championships/ \
  -b cookies.txt

# Or with Accept-Language header
curl -H "Accept-Language: bg" \
  http://localhost:8000/api/championships/
```

## Cookie Details

### Frontend Cookie (i18next)

- **Name:** `i18nextLng`
- **Purpose:** Frontend language state
- **Set by:** i18next library
- **Used by:** React components

### Backend Cookie (Django)

- **Name:** `django_language`
- **Purpose:** Backend language preference
- **Set by:** Django `/api/set-language/` endpoint
- **Used by:** Django LocaleMiddleware

### Synchronization

Both cookies work together:
- Frontend reads both cookies (priority to `django_language`)
- Backend reads `django_language` cookie
- Language switcher updates both simultaneously

## Troubleshooting

### Language not syncing?

1. **Check cookies are enabled in browser**
2. **Verify CORS credentials:**
   ```javascript
   withCredentials: true  // in axios config
   ```
3. **Check Django settings:**
   ```python
   CORS_ALLOW_CREDENTIALS = True
   ```

### Cookie not persisting?

1. **Check SameSite attribute:** Should be `Lax` or `None`
2. **Check cookie path:** Should be `/` (root)
3. **Check domain:** Should match frontend domain
4. **Check HTTPS:** For production, use `Secure` flag

### API not receiving language?

1. **Check Accept-Language header is sent**
2. **Check LocaleMiddleware is in MIDDLEWARE**
3. **Check cookie is included in request:**
   ```javascript
   withCredentials: true
   ```

### Language resets on page refresh?

1. **Check cookie max-age:** Should be 1 year
2. **Check localStorage:** Should persist `i18nextLng`
3. **Check syncLanguageOnInit() is called on app load**

## Best Practices

### ✅ Do

- Always use `changeLanguage()` from `utils/languageSync.js`
- Check cookies in DevTools when debugging
- Test language persistence across page refreshes
- Sync language on app initialization
- Handle API errors gracefully (fallback to frontend language)

### ❌ Don't

- Don't bypass the sync utilities
- Don't manually set cookies (use the utilities)
- Don't forget to await async language changes
- Don't assume cookie is always available (handle fallbacks)

## Architecture Diagram

```
┌─────────────────────────────────────────────┐
│           User Action (Click EN/BG)         │
└────────────────────┬────────────────────────┘
                     │
    ┌────────────────┴───────────────────┐
    │                                    │
    ▼                                    ▼
┌─────────────┐                  ┌──────────────┐
│   Frontend  │                  │   Backend    │
│   (React)   │                  │   (Django)   │
└─────────────┘                  └──────────────┘
    │                                    │
    │ 1. i18n.changeLanguage(lng)       │
    │                                    │
    │ 2. setLanguageCookie(lng)         │
    │                                    │
    │ 3. POST /api/set-language/        │
    │ ───────────────────────────────>  │
    │                                    │
    │                            4. Activate lang
    │                            5. Set cookie
    │                                    │
    │ <─────────────────────────────────│
    │    6. Response + Cookie            │
    │                                    │
    ▼                                    ▼
┌─────────────┐                  ┌──────────────┐
│ Cookie Set  │                  │  Cookie Set  │
│ UI Updated  │                  │  Lang Active │
└─────────────┘                  └──────────────┘
```

## Summary

✅ **Cookie:** `django_language` stores preference (1 year)  
✅ **Priority:** Cookie > localStorage > browser > default  
✅ **Sync:** Automatic on load, manual on change  
✅ **API:** Includes `Accept-Language` header  
✅ **Persistence:** Survives page refresh and browser restart  
✅ **Fallback:** Frontend language if backend unavailable  

The language preference is now **fully synchronized** between frontend and backend! 🌍🔄

