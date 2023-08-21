import json

from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import redirect
from django.views.decorators.http import require_http_methods
from .bookmark import Bookmarks
from main.utils import TOC


@require_http_methods(['GET'])
def bookmarks(request):
    bookmarks_manager = Bookmarks(request)

    print(bookmarks_manager.bookmarks)
    return HttpResponse(
        status=200,
        content=json.dumps(bookmarks_manager.bookmarks)
    )


@require_http_methods(['POST'])
def add_bookmark(request, topic_slug):
    toc = TOC()
    toc.one(topic_slug)

    result = toc.result()

    bookmarks_manager = Bookmarks(request)
    bookmarks_manager.add_bookmark(result.slug, result.name)

    messages.info(request, 'Тема добавлена в Закладки.')

    return redirect('/topic/' + topic_slug)


@require_http_methods(['POST'])
def remove_bookmark(request, topic_slug):

    bookmarks_manager = Bookmarks(request)
    bookmarks_manager.remove_bookmark(topic_slug)

    return HttpResponse(
        status=200
    )
