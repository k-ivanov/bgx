# Internationalization Guide for BGX API

This guide explains how to use and manage translations in the BGX Racing Platform API.

## Supported Languages

- **English (en)** - Default language
- **Bulgarian (bg)** - Bulgarian translations

## Configuration

### Settings (bgx_api/settings.py)

```python
LANGUAGE_CODE = 'en'

LANGUAGES = [
    ('en', 'English'),
    ('bg', 'Български'),
]

LOCALE_PATHS = [
    BASE_DIR / 'locale',
]

USE_I18N = True
USE_L10N = True
```

### Middleware

`LocaleMiddleware` is added to detect and set the language based on:
1. Session key (if user is authenticated)
2. Cookie (`django_language`)
3. Accept-Language header
4. Default language setting

## API Endpoints

### Set Language

**POST** `/api/set-language/`

Set the user's preferred language.

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

### Get Current Language

**GET** `/api/get-language/`

Get the current active language.

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

## Using Translations in Code

### In Python Code (Views, Models, etc.)

```python
from django.utils.translation import gettext as _

# Simple translation
message = _("Registration successful!")

# Lazy translation (for class attributes)
from django.utils.translation import gettext_lazy as _

class MyModel(models.Model):
    name = models.CharField(_("name"), max_length=100)
```

### In Serializers

```python
from rest_framework import serializers
from django.utils.translation import gettext as _

class MySerializer(serializers.Serializer):
    def validate(self, data):
        if not data.get('field'):
            raise serializers.ValidationError(
                _("This field is required")
            )
        return data
```

### In Views

```python
from rest_framework.response import Response
from django.utils.translation import gettext as _

def my_view(request):
    return Response({
        'message': _("Account activated successfully!")
    })
```

## Managing Translations

### 1. Extract Translatable Strings

After adding `_()` or `gettext()` in your code:

```bash
# Using Docker
make -f Makefile.i18n makemessages

# Or manually
docker-compose exec bgx-api python manage.py makemessages -l bg
```

This updates `locale/bg/LC_MESSAGES/django.po` with new strings.

### 2. Translate Strings

Edit `locale/bg/LC_MESSAGES/django.po`:

```po
msgid "Registration successful!"
msgstr "Успешна регистрация!"
```

### 3. Compile Translations

```bash
# Using Docker
make -f Makefile.i18n compilemessages

# Or manually
docker-compose exec bgx-api python manage.py compilemessages
```

This creates `django.mo` binary files.

### 4. Restart Server

```bash
make restart-api
```

## Translation Workflow

```
1. Mark strings for translation in code:
   message = _("Hello")

2. Extract strings:
   make -f Makefile.i18n makemessages

3. Translate in .po file:
   msgid "Hello"
   msgstr "Здравей"

4. Compile translations:
   make -f Makefile.i18n compilemessages

5. Restart server:
   make restart-api
```

## Common Translation Patterns

### Model Fields

```python
from django.db import models
from django.utils.translation import gettext_lazy as _

class Race(models.Model):
    name = models.CharField(_("name"), max_length=200)
    location = models.CharField(_("location"), max_length=200)
    status = models.CharField(
        _("status"),
        max_length=20,
        choices=[
            ('upcoming', _('upcoming')),
            ('ongoing', _('ongoing')),
            ('completed', _('completed')),
        ]
    )
```

### Error Messages

```python
from django.utils.translation import gettext as _
from rest_framework.exceptions import PermissionDenied

if not user.has_permission():
    raise PermissionDenied(_("You don't have permission to update this race."))
```

### Response Messages

```python
from django.utils.translation import gettext as _

return Response({
    'message': _("Account activated successfully!"),
    'user': serializer.data
})
```

### Email/Notifications

```python
from django.utils.translation import gettext as _

subject = _("Welcome to BGX Racing Platform")
message = _("Thank you for registering!")
```

## Testing Translations

### Test with Different Languages

```bash
# Test Bulgarian
curl -X POST http://localhost:8000/api/set-language/ \
  -H "Content-Type: application/json" \
  -d '{"language": "bg"}'

# Then make API calls to see translated responses

# Test English
curl -X POST http://localhost:8000/api/set-language/ \
  -H "Content-Type: application/json" \
  -d '{"language": "en"}'
```

### Test with Accept-Language Header

```bash
curl -H "Accept-Language: bg" http://localhost:8000/api/races/
```

## Translation Files

### Structure

```
bgx-api/
├── locale/
│   ├── bg/
│   │   └── LC_MESSAGES/
│   │       ├── django.po   # Source translation file
│   │       └── django.mo   # Compiled translation file
│   └── en/
│       └── LC_MESSAGES/
│           └── django.po
```

### .po File Format

```po
# Comment
msgid "English text"
msgstr "Bulgarian text"

# With context
msgctxt "button"
msgid "Submit"
msgstr "Изпрати"

# Plural forms
msgid "%(count)d race"
msgid_plural "%(count)d races"
msgstr[0] "%(count)d състезание"
msgstr[1] "%(count)d състезания"
```

## Frontend Integration

The frontend can detect the user's language preference and send the appropriate `Accept-Language` header:

```javascript
// In your API client
const language = localStorage.getItem('i18nextLng') || 'en'

axios.defaults.headers.common['Accept-Language'] = language
```

Or set via the set-language endpoint:

```javascript
await api.post('/set-language/', { language: 'bg' })
```

## Best Practices

1. **Always use lazy translation for model fields and class attributes**
   ```python
   from django.utils.translation import gettext_lazy as _
   ```

2. **Use regular gettext in views and functions**
   ```python
   from django.utils.translation import gettext as _
   ```

3. **Mark all user-facing strings for translation**
   - Error messages
   - Success messages
   - Field labels
   - Help text
   - Email content

4. **Don't translate**
   - URLs (use `i18n_patterns` if needed)
   - Internal logs
   - Technical error messages for developers

5. **Keep translations consistent**
   - Use the same translation for the same term
   - Maintain a glossary for technical terms

6. **Update translations regularly**
   - Run `makemessages` after adding new strings
   - Review translations before deployment

## Troubleshooting

### Translations not showing up?

1. Check if .mo files are compiled:
   ```bash
   ls -la bgx-api/locale/bg/LC_MESSAGES/
   ```

2. Restart the server:
   ```bash
   make restart-api
   ```

3. Clear Django cache if applicable

### New strings not extracted?

Make sure you're using `_()` or `gettext()`:
```python
# Wrong
message = "Hello"

# Correct
message = _("Hello")
```

### Language not switching?

Check:
1. LocaleMiddleware is in MIDDLEWARE
2. Cookie/session is set correctly
3. Accept-Language header is sent

## Resources

- [Django i18n Documentation](https://docs.djangoproject.com/en/4.2/topics/i18n/)
- [Translation Tutorial](https://docs.djangoproject.com/en/4.2/topics/i18n/translation/)
- [GNU gettext utilities](https://www.gnu.org/software/gettext/)

