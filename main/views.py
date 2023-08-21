from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.views.decorators.cache import cache_page
from django.views.decorators.http import require_http_methods
from django.http import HttpResponse
from django.contrib import messages

import json

from .forms import *
from . import utils

from main.comments.comment import Comment
from main.comments.forms import CommentForm


@require_http_methods(['GET'])
@cache_page(60*60)
def get_tree(request):
    if request.user.is_authenticated:
        toc = utils.TOC(user=request.user)
    else:
        toc = utils.TOC()

    return HttpResponse(
        status=200,
        content=json.dumps(toc.result(serialized=True, is_full=False)),
        content_type='application/json',
    )


@require_http_methods(['GET'])
def index(request):
    toc = utils.TOC()
    context = {
        'topics': toc.result(),
    }
    return render(request, 'index.html', context)


@require_http_methods(['GET'])
def get_topic_via_slug(request, slug):
    toc = utils.TOC()
    toc.one(slug)

    result = toc.result()

    route = ''.join(['',
                     f'<a href="/topic/{result.parent.slug}/">{result.parent.name}</a>/' if result.parent else '',
                     result.name]
                    )

    comments = Comment().get_all_by_topic(slug)
    amount = comments.count()
    for comment in comments:
        amount += comment.answers.count()

    context = {
        'topic': toc.result(),
        'route': route,
        'comments': comments,
        'form': CommentForm(request.POST),
        'comments_amount': amount,
        'is_learned': True if request.user in toc.result().learned_by_users.all() else False,
    }
    return render(request, 'topic.html', context)


@login_required
@require_http_methods(['POST'])
def set_topic_learned(request, slug):
    try:
        topic = Topic.objects.get(slug=slug)
        topic.learned_by_users.add(request.user)
        topic.save()
        messages.info(request, 'Тема отмечена Выученной.')
    except Exception as e:
        messages.error(request, 'Ой-ой, что-то пошло не так...' + str(e))

    return redirect('/topic/' + slug + '/')


@login_required
@require_http_methods(['POST'])
def set_topic_not_learned(request, slug):
    try:
        topic = Topic.objects.get(slug=slug)
        topic.learned_by_users.remove(request.user)
        topic.save()
        messages.info(request, 'Тема отмечена Не выученной.')
    except Exception as e:
        messages.error(request, 'Ой-ой, что-то пошло не так...' + str(e))

    return redirect('/topic/' + slug + '/')


@require_http_methods(['GET'])
def get_current_topic(request, slug):
    toc = utils.TOC()
    toc.one(slug)

    return HttpResponse(
        status=200,
        content=json.dumps(toc.result(serialized=True)),
        content_type='application/json',
    )


@require_http_methods(['GET'])
def get_more_tree(request, slug):
    if request.user.is_authenticated:
        toc = utils.TOC(user=request.user)
    else:
        toc = utils.TOC()

    toc.children(slug)
    return HttpResponse(
        status=200,
        content=json.dumps(toc.result(serialized=True)),
        content_type='application/json'
    )


@require_http_methods(['GET'])
def search_content(request):
    data = request.GET.get('q', None)

    toc = utils.TOC()
    toc.filter(data)

    context = {
        'content': toc.result(),
    }

    return render(request, 'content.html', context)


@require_http_methods(['GET'])
def personal_data_view(request):
    context = {}
    return render(request, 'policy.html', context)


@require_http_methods(['GET'])
def get_next_topic(request, current_slug: str):
    toc = utils.TOC()
    toc.next(current_slug)
    result = toc.result()

    if not result:
        return get_topic_via_slug(request, current_slug)

    return redirect('/topic/' + result.slug + '/')


@require_http_methods(['GET'])
def get_previous_topic(request, current_slug: str):
    toc = utils.TOC()
    toc.previous(current_slug)

    result = toc.result()

    if not result:
        return get_topic_via_slug(request, current_slug)

    return redirect('/topic/' + result.slug + '/')


@login_required
@require_http_methods(['GET'])
def profile(request):
    progress = utils.Progress(request.user)

    data, total_rate = progress.result()

    context = {
        'basic_topics': data,
        'total_rate': total_rate,
    }
    return render(request, 'profile.html', context)
