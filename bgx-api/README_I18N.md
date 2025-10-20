# Internationalization (i18n) in BGX API

## Quick Start

### 1. Set Language (Frontend Integration)

The frontend can set the user's language preference:

```javascript
// In your API client (api.js)
export const setLanguage = async (language) => {
  const response = await api.post('/set-language/', { language })
  return response.data
}

// Usage
await setLanguage('bg') // Bulgarian
await setLanguage('en') // English
```

### 2. Language Detection

The Django backend automatically detects language from:
1. **Cookie** (`django_language`) - Set by `/api/set-language/` endpoint
2. **Accept-Language header** - Sent by browser/API client
3. **Session** - For authenticated users
4. **Default** - Falls back to English

### 3. Using Translations in API Responses

All API responses that use `gettext()` or `_()` will be automatically translated based on the active language.

## API Endpoints

### Set Language

**POST** `/api/set-language/`

```bash
curl -X POST http://localhost:8000/api/set-language/ \
  -H "Content-Type: application/json" \
  -d '{"language": "bg"}'
```

Response:
```json
{
  "status": "success",
  "language": "bg",
  "message": "Language set to bg"
}
```

Sets a cookie that persists for 1 year.

### Get Current Language

**GET** `/api/get-language/`

```bash
curl http://localhost:8000/api/get-language/
```

Response:
```json
{
  "language": "en",
  "supported_languages": ["en", "bg"]
}
```

## Frontend Integration

### Option 1: Using Accept-Language Header

```javascript
// In your API client setup
import axios from 'axios'
import i18n from '../i18n/config'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000/api'
})

// Add interceptor to include language header
api.interceptors.request.use((config) => {
  const lang = i18n.language || 'en'
  config.headers['Accept-Language'] = lang
  return config
})
```

### Option 2: Using Set Language Endpoint

```javascript
// When user switches language in frontend
import { useTranslation } from 'react-i18next'
import { setLanguage as setApiLanguage } from './api/api'

function LanguageSwitcher() {
  const { i18n } = useTranslation()
  
  const changeLanguage = async (lng) => {
    // Change frontend language
    await i18n.changeLanguage(lng)
    
    // Sync with backend
    try {
      await setApiLanguage(lng)
    } catch (error) {
      console.error('Failed to set API language:', error)
    }
  }
  
  return (
    <button onClick={() => changeLanguage('bg')}>
      Switch to Bulgarian
    </button>
  )
}
```

## Translated Content

### Currently Translated:

- ✅ Authentication messages (registration, activation)
- ✅ Permission error messages
- ✅ Model field verbose names
- ✅ Status choices (upcoming, active, completed, etc.)
- ✅ Category names (expert, profi, junior, etc.)
- ✅ Common field labels

### Example Translated Messages:

**English:**
- "Registration successful! Please use the activation code to activate your account."
- "You don't have permission to update this race."
- "This race has reached maximum participants."

**Bulgarian:**
- "Успешна регистрация! Моля използвай кода за активация за да активираш акаунта си."
- "Нямаш права да актуализираш това състезание."
- "Това състезание е достигнало максималния брой участници."

## Development Workflow

### Adding New Translatable Strings

1. **Mark strings in Python code:**
```python
from django.utils.translation import gettext as _

return Response({
    'message': _("Your message here")
})
```

2. **Extract new strings:**
```bash
make makemessages
```

3. **Translate in `locale/bg/LC_MESSAGES/django.po`:**
```po
msgid "Your message here"
msgstr "Твоето съобщение тук"
```

4. **Compile translations:**
```bash
make compilemessages
```

5. **Restart server:**
```bash
make restart-api
```

## Testing

### Test Bulgarian Translations

```bash
# Set language to Bulgarian
curl -X POST http://localhost:8000/api/set-language/ \
  -H "Content-Type: application/json" \
  -d '{"language": "bg"}'

# Test any API endpoint
curl -H "Cookie: django_language=bg" \
  http://localhost:8000/api/races/
```

### Test with Accept-Language Header

```bash
curl -H "Accept-Language: bg" \
  http://localhost:8000/api/championships/
```

## File Structure

```
bgx-api/
├── locale/
│   ├── bg/
│   │   └── LC_MESSAGES/
│   │       ├── django.po   # Bulgarian translations (editable)
│   │       └── django.mo   # Compiled (auto-generated)
│   └── en/
│       └── LC_MESSAGES/
│           └── django.po   # English (source)
├── bgx_api/
│   ├── settings.py         # i18n configuration
│   ├── urls.py             # language switching endpoints
│   └── views.py            # set_language, get_language
├── Makefile.i18n           # i18n management commands
└── I18N_GUIDE.md           # Detailed guide
```

## Makefile Commands

```bash
# Extract translatable strings
make makemessages

# Compile translation files
make compilemessages

# Do both
make update-translations

# Show translation statistics
make -f Makefile.i18n stats
```

## Common Issues

### Translations not showing?

1. **Check if .mo files exist:**
   ```bash
   ls bgx-api/locale/bg/LC_MESSAGES/django.mo
   ```

2. **Compile translations:**
   ```bash
   make compilemessages
   ```

3. **Restart server:**
   ```bash
   make restart-api
   ```

### Language not switching?

1. **Check cookie is set:**
   ```bash
   curl -v http://localhost:8000/api/set-language/ \
     -d '{"language":"bg"}' | grep Set-Cookie
   ```

2. **Check Accept-Language header:**
   ```bash
   curl -H "Accept-Language: bg" http://localhost:8000/api/races/
   ```

## Best Practices

1. **Always translate user-facing messages**
2. **Use lazy translation for model fields**
3. **Keep translations in .po files, not in code**
4. **Test both languages before deploying**
5. **Sync frontend and backend language selection**

## Resources

- Django i18n: https://docs.djangoproject.com/en/4.2/topics/i18n/
- Full guide: See `I18N_GUIDE.md`
- Translation commands: `make -f Makefile.i18n help`

