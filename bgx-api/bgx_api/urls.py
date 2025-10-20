"""
URL configuration for bgx_api project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import routers
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
from .views import health_check, set_language, get_language

# Import viewsets
from accounts.views import UserViewSet
from clubs.views import ClubViewSet
from riders.views import RiderViewSet
from championships.views import ChampionshipViewSet
from races.views import RaceViewSet, RaceDayViewSet, RaceParticipationViewSet
from results.views import (
    RaceDayResultViewSet, RaceResultViewSet,
    ChampionshipResultViewSet, ClubResultViewSet
)

# Create router and register viewsets
router = routers.DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'clubs', ClubViewSet, basename='club')
router.register(r'riders', RiderViewSet, basename='rider')
router.register(r'championships', ChampionshipViewSet, basename='championship')
router.register(r'races', RaceViewSet, basename='race')
router.register(r'race-days', RaceDayViewSet, basename='raceday')
router.register(r'race-participations', RaceParticipationViewSet, basename='raceparticipation')
router.register(r'results/race-day-results', RaceDayResultViewSet, basename='racedayresult')
router.register(r'results/race-results', RaceResultViewSet, basename='raceresult')
router.register(r'results/championship-results', ChampionshipResultViewSet, basename='championshipresult')
router.register(r'results/club-standings', ClubResultViewSet, basename='clubresult')

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # Health check
    path('health/', health_check, name='health_check'),
    
    # Language switching
    path('api/set-language/', set_language, name='set_language'),
    path('api/get-language/', get_language, name='get_language'),
    
    # Authentication endpoints
    path('api/auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/auth/register/', UserViewSet.as_view({'post': 'create'}), name='user_register'),
    
    # API endpoints
    path('api/', include(router.urls)),
    
    # Browsable API auth
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    
    # API Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]

# Serve static and media files in development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

