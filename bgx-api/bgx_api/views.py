from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db import connection


@api_view(['GET'])
def health_check(request):
    """
    Health check endpoint that verifies:
    - API is running
    - Database connection is working
    """
    try:
        # Test database connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        
        return Response({
            'status': 'healthy',
            'message': 'API is running and database connection is established',
            'database': 'connected'
        })
    except Exception as e:
        return Response({
            'status': 'unhealthy',
            'message': 'Database connection failed',
            'error': str(e)
        }, status=503)

