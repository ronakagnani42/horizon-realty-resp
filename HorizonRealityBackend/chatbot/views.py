from django.http import JsonResponse
from .chatbot_engine import get_bot_response

def chatbot_response(request):
    user_message = request.GET.get('message')
    response = get_bot_response(user_message)
    return JsonResponse({'response': response})