from django.shortcuts import render
from django.views.decorators.http import require_http_methods

from main.models import Gallery


@require_http_methods(['GET'])
def gallery(request):
    context = {
        'gallery': Gallery.objects.all().prefetch_related('artifacts'),
    }

    return render(request, 'gallery.html', context)
