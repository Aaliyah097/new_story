from django.db.models import Q
from .models import *


class Progress:
    """Manage user's learning progress base on learned topics"""

    def __init__(self, user: User = None):
        self.queryset = Topic.objects.filter(is_basic=True).order_by('name')
        self.user = user

    def _get_already_learned(self, topic: Topic) -> int:
        return topic.get_descendants(include_self=True).filter(learned_by_users__in=[self.user]).count()

    @staticmethod
    def _get_learn_length_for_basic_topic(topic: Topic) -> int:
        return topic.get_descendant_count() + 1

    def result(self) -> (list, int):
        result = []

        for topic in self.queryset:
            topic_dict = topic.to_dict()

            have_to_learn_amount = self._get_learn_length_for_basic_topic(topic)
            learned_already = self._get_already_learned(topic)

            try:
                topic_dict['progress'] = int(learned_already / have_to_learn_amount * 100)
            except (ZeroDivisionError, KeyError, TypeError, AttributeError):
                topic_dict['progress'] = 0

            result.append(topic_dict)

        return result, int(sum([t['progress'] for t in result]) / len(result))


class TOC:
    """Tree-catalog navigation"""

    def __init__(self, user: User = None):
        self._result = Topic.objects.all()
        self.user = user

    def filter(self, filter_params: dict = False) -> None:
        if filter_params:
            self._filter_result(filter_params)

    @staticmethod
    def get_by_slug(slug: str) -> Topic | None:
        try:
            return Topic.objects.get(slug=slug)
        except Topic.DoesNotExist:
            return None

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

    def _get_topic_by_slug(self, topic_slug: str) -> None:
        topic = Topic.objects.prefetch_related('attachments').get(slug=topic_slug)
        if not topic:
            raise Topic.DoesNotExist(f'Тема {topic_slug} не найдена')

        self._result = topic

    def _get_topics_from_current(self, topic_slug: str) -> None:
        self._result = Topic.objects.filter(slug=topic_slug)

    def _serialize_result(self, is_full: bool = True) -> list:
        root_nodes = self._result
        dicts = []
        for n in root_nodes:
            dicts.append(self._recursive_node_to_dict(n, is_full=is_full))
        return dicts

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

    def _recursive_node_to_dict(self, node: Topic, is_full: bool = True) -> dict:
        result = {
            'id': node.pk,
            'text': node.name,
            'name_en': '',
            'description': '',
            'slug': node.slug,
            'content': '',
            'more_link': '',
            'attachments': [],
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

