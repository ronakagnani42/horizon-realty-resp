from .models import Service

def services_processor(request):
    """
    Context processor to make services available in all templates
    """
    footer_services = Service.objects.all()
    return {
        'footer_services': footer_services
    }