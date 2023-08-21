import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import redirect
from django.views.decorators.http import require_http_methods

from main.comments.forms import CommentForm
from .comment import Comment
from main.utils import TOC


@login_required
@require_http_methods(['POST'])
def create_comment(request, topic_slug: str, *args, **kwargs):
    form = CommentForm(request.POST)

    if not form.is_valid():
        messages.error(request, 'Хмм... пустой комментарий?')
        return redirect('/topic/' + topic_slug)

    text = form.cleaned_data['text']
    parent_comment_id = request.POST.get('parent', None)

    if parent_comment_id and parent_comment_id != "":
        comment = Comment().get_by_id(parent_comment_id)
        if not comment:
            messages.error(request, 'Не удалось создать ответ. Базовый комментарий не обнаружен')
            return redirect('/topic/' + topic_slug)
        try:
            Comment.create_answer(
                comment_id=comment.id,
                author_id=request.user.id,
                text=text
            )
        except Exception as e:
            messages.error(request, 'Не удалось создать ответ...' + str(e))
            return redirect('/topic/' + topic_slug)
    else:
        topic = TOC.get_by_slug(slug=topic_slug)
        if not topic:
            messages.error(request, 'Не удалость найти статью ' + topic_slug)
        try:
            Comment.create_comment(
                topic_id=topic.id,
                author_id=request.user.id,
                text=text
            )
            messages.info(request, 'Спасибо, что поделились своим мнением!')
        except Exception as e:
            messages.error(request, 'Произошла непредвиденная ошибка... ' + str(e))

    return redirect('/topic/' + topic_slug)


@login_required
@require_http_methods(['POST'])
def hide_comment(request, pk):
    try:
        Comment.hide_comment_by_id(pk)
    except Exception as e:
        return HttpResponse(
            status=500,
            content=json.dumps(str(e))
        )

    return HttpResponse(
        status=200
    )


@login_required
@require_http_methods(['POST'])
def delete_answer(request, pk):
    if not request.user.is_superuser:
        return HttpResponse(
            status=401,
            content=json.dumps("Недостаточно прав")
        )
    try:
        Comment.hide_answer_by_id(pk)
    except Exception as e:
        return HttpResponse(
            status=500,
            content=json.dumps(str(e))
        )

    return HttpResponse(
        status=200
    )
