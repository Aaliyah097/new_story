from main.models import (
    Comment as CommentTable,
    Answer as AnswerTable
)
from django.db.models import QuerySet


class Comment:
    def __init__(self):
        self.queryset = CommentTable.objects.all().prefetch_related('answers')

    def get_all_by_topic(self, topic_slug: str) -> QuerySet[CommentTable]:
        return self.queryset.filter(topic__slug=topic_slug).prefetch_related('answers')

    def get_by_id(self, pk: int) -> CommentTable | None:
        try:
            return self.queryset.get(id=pk)
        except CommentTable.DoesNotExist:
            return None

    @staticmethod
    def hide_answer_by_id(answer_id: int) -> None:
        try:
            answer = AnswerTable.objects.get(id=answer_id)
            answer.text = '<span style="color: #858383">---Комментарий удален модератором---</span><br><br>'
            answer.save()
        except AnswerTable.DoesNotExist:
            raise Exception(f"Ответ с id {answer_id} не найден")

    @staticmethod
    def hide_comment_by_id(comment_id: int) -> None:
        try:
            comment = CommentTable.objects.get(id=comment_id)
            comment.text = '<span style="color: #858383">---Комментарий удален модератором---</span><br><br>'
            comment.save()
        except CommentTable.DoesNotExist:
            raise Exception(f"Комментарий с id {comment_id} не найден")

    @staticmethod
    def create_comment(topic_id: int, author_id: int, text: str) -> None:
        if 'style' in text:
            raise Exception('Ключевое слово "style" недопустимо, спасибо.')
        try:
            CommentTable.objects.create(
                topic_id=topic_id,
                author_id=author_id,
                text=text
            )
        except Exception as e:
            raise Exception(str(e))

    @staticmethod
    def create_answer(comment_id: int, author_id: int, text: str) -> None:
        try:
            AnswerTable.objects.create(
                comment_id=comment_id,
                author_id=author_id,
                text=text
            )
        except Exception as e:
            raise Exception(str(e))
