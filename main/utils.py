import json

from django.db.models import prefetch_related_objects, Q
from mptt.templatetags.mptt_tags import cache_tree_children
from .models import *


class Progress:
    def __init__(self, user: User = None):
        self.queryset = Topic.objects.filter(is_basic=True).order_by('name')
        self.user = user

    def _get_already_learned(self, topic: Topic) -> int:
        return topic.get_descendants(include_self=True).filter(learned_by_users__in=[self.user]).count()

    def _get_learn_length_for_basic_topic(self, topic: Topic) -> int:
        return topic.get_descendant_count() + 1

    def result(self) -> (list, int):
        result = []

        for topic in self.queryset:
            topic_dict = topic.to_dict()

            have_to_learn_amount = self._get_learn_length_for_basic_topic(topic)
            learned_already = self._get_already_learned(topic)

            try:
                topic_dict['progress'] = int(learned_already / have_to_learn_amount * 100)
            except Exception as e:
                topic_dict['progress'] = 0

            result.append(topic_dict)

        return result, int(sum([t['progress'] for t in result]) / len(result))


class TOC:
    def __init__(self, user: User = None):
        self._result = Topic.objects.all()
        self.user = user

    def filter(self, filter_params: dict = False) -> None:
        if filter_params:
            self._filter_result(filter_params)

    def one(self, slug: str) -> None:
        self._get_topic_by_slug(slug)

    def previous(self, slug: str):
        self._result = Topic.objects.prefetch_related('attachments').get(slug=slug).parent

    def current(self, slug: str):
        pass

    def next(self, slug: str):
        self._result = Topic.objects.prefetch_related('attachments').get(slug=slug).get_children().first()

    def children(self, slug: str):
        self._get_topics_from_current(slug)

    def result(self, serialized: bool = False, is_full: bool = True):
        if serialized:
            try:
                return self._serialize_result(is_full=is_full)
            except TypeError:
                return self._result.to_dict()
        return self._result

    # Second Important Function
    def _get_topic_by_slug(self, topic_slug: str) -> None:
        topic = Topic.objects.prefetch_related('attachments').get(slug=topic_slug)
        if not topic:
            raise Topic.DoesNotExist(f'Тема {topic_slug} не найдена')

        self._result = topic

    # Third Important Function
    def _get_topics_from_current(self, topic_slug: str) -> None:
        self._result = Topic.objects.filter(slug=topic_slug)

    # First Important Function
    def _serialize_result(self, is_full: bool = True) -> list:
        root_nodes = self._result
        dicts = []
        for n in root_nodes:
            dicts.append(self._recursive_node_to_dict(n, is_full=is_full))
        return dicts

    # Fourth Important Function
    def _filter_result(self, filter_params: dict) -> None:
        if type(self._result) != list:
            self._result = self._result.filter(
                Q(name__icontains=filter_params) |
                Q(name_en__icontains=filter_params) |
                Q(description__icontains=filter_params) |
                Q(text__icontains=filter_params)
            )
        else:
            pass

    # Fifth Important Function
    def _recursive_node_to_dict(self, node: Topic, is_full: bool = True) -> dict:
        result = {
            'id': node.pk,
            'text': node.name,
            'name_en': '',  # node.name_en,
            'description': '',  # node.description,
            'slug': node.slug,
            'content': '',  # node.text if is_full else None,
            'more_link': '',  # node.more_link,
            'attachments': [],  # [a.to_dict() for a in node.attachments.all()] if is_full else [],
            'data': node.slug,
            'state': {
                'opened': True,
                'disabled': False,
                'selected': False
            },
            'is_basic': node.is_basic
        }

        if self.user:
            result['a_attr'] = {'style': 'text-decoration: line-through'} if self.user in node.learned_by_users.all() else {}

        if not is_full:
            has_basic = node.get_descendants(include_self=False).filter(is_basic=True).\
                                                    count() != 0

            result['state']['opened'] = True if has_basic else False

            children = [self._recursive_node_to_dict(c, is_full=is_full) for c in node.get_children()] if has_basic else []

        else:
            children = [self._recursive_node_to_dict(c, is_full=is_full) for c in node.get_children()]

        if node.get_descendant_count() != 0:
            result['children'] = children
            result['icon'] = '/static/img/folder.png'
        else:
            result['children'] = []
            result['icon'] = '/static/img/file.png'


        return result


class CommentModel:
    def __init__(self):
        self.queryset = Comment.objects.all().prefetch_related('answers')

    def get_all_by_topic(self, topic_slug: str):
        return self.queryset.filter(topic__slug=topic_slug).prefetch_related('answers')

    def get_by_id(self, pk) -> Comment:
        try:
            return self.queryset.get(id=pk)
        except Comment.DoesNotExist:
            raise Exception(f'Комментария с id {pk} не существует')

    @staticmethod
    def hide_answer_by_id(answer_id: int):
        try:
            answer = Answer.objects.get(id=answer_id)
            answer.text = '<span style="color: #858383">---Комментарий удален модератором---</span><br><br>'
            answer.save()
        except Answer.DoesNotExist:
            raise Exception(f"Ответ с id {answer_id} не найден")

    @staticmethod
    def hide_comment_by_id(comment_id: int):
        try:
            comment = Comment.objects.get(id=comment_id)
            comment.text = '<span style="color: #858383">---Комментарий удален модератором---</span><br><br>'
            comment.save()
        except Comment.DoesNotExist:
            raise Exception(f"Комментарий с id {comment_id} не найден")

    @staticmethod
    def create_comment(topic_id, author_id, text) -> None:
        try:
            Comment.objects.create(
                topic_id=topic_id,
                author_id=author_id,
                text=text
            )
        except Exception as e:
            raise Exception(str(e))

    @staticmethod
    def create_answer(comment_id, author_id, text) -> None:
        try:
            Answer.objects.create(
                comment_id=comment_id,
                author_id=author_id,
                text=text
            )
        except Exception as e:
            raise Exception(str(e))


class BookmarksManager:
    def __init__(self, request: dict, **kwargs):
        self._session = request.session
        self.bookmarks: dict = self._session.get('bookmarks')
        if not self.bookmarks:
            self.bookmarks = self._session['bookmarks'] = {}

    def add_bookmark(self, topic_slug: str, topic_name: str):
        if topic_slug not in self.bookmarks:
            self.bookmarks[topic_slug] = topic_name
            self._save()

    def remove_bookmark(self, topic_slug: str):
        if topic_slug in self.bookmarks:
            del self.bookmarks[topic_slug]
            self._save()

    def _clear(self):
        del self._session['bookmarks']
        self._session.modified = True

    def _save(self):
        self._session['bookmarks'] = self.bookmarks
        self._session.modified = True

    def __len__(self):
        return len(self.bookmarks)

