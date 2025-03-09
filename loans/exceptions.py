from rest_framework.views import exception_handler
from rest_framework.response import Response

def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)
    
    if response is not None:
        response.data = {
            'error': True,
            'message': response.data,
        }
    else:
        return Response({'error': True, 'message': 'An unexpected error occurred.'}, status=500)
    
    return response