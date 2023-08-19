from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import render, redirect
from django.views import View
from django.views.decorators.cache import cache_page
from django.views.decorators.http import require_http_methods
from django.http import HttpResponse
from django.contrib import messages
from django.http import HttpResponseRedirect


import json
from mptt.templatetags.mptt_tags import cache_tree_children

from .forms import *
from . import utils
from .models import Topic, Gallery, Artifact

# Create your views here.


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
        'bookmarks': utils.BookmarksManager(request).bookmarks
    }
    return render(request, 'index.html', context)


@require_http_methods(['GET'])
def get_topic_via_slug(request, slug):
    toc = utils.TOC()
    toc.one(slug)

    result = toc.result()
    route = ''
    route += f'<a href="/topic/{result.parent.slug}/">{result.parent.name}</a>/' if result.parent else ''
    route += result.name

    comments = utils.CommentModel().get_all_by_topic(slug)
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
        'bookmarks': utils.BookmarksManager(request).bookmarks
    }
    return render(request, 'topic.html', context)


@require_http_methods(['POST'])
def set_topic_learned(request, slug):
    if not request.user.is_authenticated:
        return redirect('/accounts/google/login/')

    try:
        topic = Topic.objects.get(slug=slug)
        topic.learned_by_users.add(request.user)
        topic.save()
        messages.info(request, 'Тема отмечена Выученной.')
    except Exception as e:
        messages.error(request, 'Ой-ой, что-то пошло не так...')

    return redirect('/topic/' + slug + '/')


@require_http_methods(['POST'])
def set_topic_not_learned(request, slug):
    if not request.user.is_authenticated:
        return redirect('/accounts/google/login/')

    try:
        topic = Topic.objects.get(slug=slug)
        topic.learned_by_users.remove(request.user)
        topic.save()
        messages.info(request, 'Тема отмечена Не выученной.')
    except Exception as e:
        messages.error(request, 'Ой-ой, что-то пошло не так...')

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
    try:
        data = request.GET['q']
    except AttributeError:
        data = None

    toc = utils.TOC()
    toc.filter(data)

    context = {
        'content': toc.result(),
        'bookmarks': utils.BookmarksManager(request).bookmarks
    }

    return render(request, 'content.html', context)


@require_http_methods(['GET'])
def personal_data_view(request):
    context = {
        'bookmarks': utils.BookmarksManager(request).bookmarks
    }
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


@require_http_methods(['GET'])
def profile(request):
    if not request.user.is_authenticated:
        return redirect('/accounts/google/login/')

    progress = utils.Progress(request.user)

    data, total_rate = progress.result()

    context = {
        'basic_topics': data,
        'total_rate': total_rate,
        'bookmarks': utils.BookmarksManager(request).bookmarks
    }
    return render(request, 'profile.html', context)


class CommentView(View):
    def post(self, request, topic_slug: str, *args, **kwargs):
        if request.user.is_authenticated:
            form = CommentForm(request.POST)

            if form.is_valid():
                text = form.cleaned_data['text']

                parent_comment_id = request.POST.get('parent', None)
                if parent_comment_id != "":
                    try:
                        comment = utils.CommentModel().get_by_id(parent_comment_id)

                        try:
                            utils.CommentModel.create_answer(
                                comment_id=comment.id,
                                author_id=request.user.id,
                                text=text
                            )
                        except Exception as e:
                            messages.error(request, 'Не удалось создать ответ...')
                            return redirect('/topic/' + topic_slug)
                    except Exception as e:
                        messages.error(request, 'Не удалось создать ответ. Базовый комментарий не обнаружен')
                        return redirect('/topic/' + topic_slug)
                else:
                    if 'style' in text:
                        messages.error(request, 'Ключевое слово "style" недопустимо, спасибо.')
                        return redirect('/topic/' + topic_slug)
                    try:
                        topic = Topic.objects.get(slug=topic_slug)

                        try:
                            utils.CommentModel.create_comment(
                                topic_id=topic.id,
                                author_id=request.user.id,
                                text=text
                            )
                            messages.info(request, 'Спасибо, что поделились своим мнением!')
                        except Exception as e:
                            messages.error(request, 'Произошла непредвиденная ошибка... ' + str(e))

                    except Topic.DoesNotExist:
                        messages.error(request, 'Не удалость найти статью ' + topic_slug)
            else:
                messages.error(request, 'Хмм... пустой комментарий?')
        else:
            messages.error(request, 'Отказно в доступе')

        return redirect('/topic/' + topic_slug)


@require_http_methods(['POST'])
def hide_comment(request, pk):
    if request.user.is_superuser:
        try:
            utils.CommentModel.hide_comment_by_id(pk)
        except Exception as e:
            return HttpResponse(
                status=500,
                content=json.dumps(str(e))
            )
    else:
        return HttpResponse(
            status=401,
            content=json.dumps("Недостаточно прав")
        )
    return HttpResponse(
        status=200
    )


@require_http_methods(['POST'])
def delete_answer(request, pk):
    if request.user.is_superuser:
        try:
            utils.CommentModel.hide_answer_by_id(pk)
        except Exception as e:
            return HttpResponse(
                status=500,
                content=json.dumps(str(e))
            )
    else:
        return HttpResponse(
            status=401,
            content=json.dumps("Недостаточно прав")
        )
    return HttpResponse(
        status=200
    )


@require_http_methods(['GET'])
def gallery(request):
    context = {
        'gallery': Gallery.objects.all().prefetch_related('artifacts'),
        'bookmarks': utils.BookmarksManager(request).bookmarks
    }

    return render(request, 'gallery.html', context)


@require_http_methods(['GET'])
def bookmarks(request):
    bookmarks_manager = utils.BookmarksManager(request)

    return HttpResponse(
        status=200,
        content=bookmarks_manager.bookmarks
    )


def add_bookmark(request, topic_slug):
    toc = utils.TOC()
    toc.one(topic_slug)

    result = toc.result()

    bookmarks_manager = utils.BookmarksManager(request)
    bookmarks_manager.add_bookmark(result.slug, result.name)

    messages.info(request, 'Тема добавлена в Закладки.')

    return redirect('/topic/' + topic_slug)


def remove_bookmark(request, topic_slug):

    bookmarks_manager = utils.BookmarksManager(request)
    bookmarks_manager.remove_bookmark(topic_slug)

    return HttpResponse(
        status=200
    )
