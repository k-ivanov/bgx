from django.http import JsonResponse
from django.utils import translation
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
import json


def health_check(request):
    """Health check endpoint"""
    return JsonResponse({'status': 'healthy', 'service': 'bgx-api'})


@csrf_exempt
@require_POST
def set_language(request):
    """
    Set the user's language preference
    Accepts: POST /api/set-language/
    Body: {"language": "en" or "bg"}
    """
    try:
        data = json.loads(request.body)
        lang_code = data.get('language', 'en')
        
        # Validate language code
        supported_languages = ['en', 'bg']
        if lang_code not in supported_languages:
            return JsonResponse({
                'error': 'Unsupported language',
                'supported': supported_languages
            }, status=400)
        
        # Activate the language
        translation.activate(lang_code)
        
        # Set language in session if available
        if hasattr(request, 'session'):
            request.session[translation.LANGUAGE_SESSION_KEY] = lang_code
        
        response = JsonResponse({
            'status': 'success',
            'language': lang_code,
            'message': f'Language set to {lang_code}'
        })
        
        # Set language cookie
        response.set_cookie(
            'django_language',
            lang_code,
            max_age=365 * 24 * 60 * 60,  # 1 year
            path='/',
            samesite='Lax'
        )
        
        return response
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def get_language(request):
    """
    Get the current language
    """
    current_language = translation.get_language()
    return JsonResponse({
        'language': current_language,
        'supported_languages': ['en', 'bg']
    })
