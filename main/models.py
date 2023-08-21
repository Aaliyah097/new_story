import datetime

from django.db import models
from mptt.models import MPTTModel, TreeForeignKey
from ckeditor.fields import RichTextField
from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.contrib.auth.models import User


class Topic(MPTTModel):
    name = models.CharField(verbose_name='Название',
                            max_length=150)
    name_en = models.CharField(verbose_name='Название (en)',
                               max_length=150,
                               default=None, blank=True, null=True)
    description = models.CharField(verbose_name='Описание',
                                   max_length=500,
                                   default=None, blank=True, null=True)
    slug = models.SlugField(max_length=150,
                            unique=True,
                            db_index=True,
                            default=None, null=True)
    parent: 'Topic' = TreeForeignKey('self',
                                     on_delete=models.CASCADE,
                                     null=True, blank=True,
                                     related_name='children')
    text = RichTextField(verbose_name='Текст',
                         null=True, blank=True, default=None)
    more_link = models.CharField(verbose_name='Подробнее',
                                 max_length=500,
                                 default=None, blank=True, null=True)
    is_basic = models.BooleanField(verbose_name='Базовая тема',
                                   default=False, blank=True, null=True)
    created_at: datetime.datetime = models.DateTimeField(verbose_name='Дата создания',
                                                         auto_now=True,
                                                         blank=True, null=True)
    learned_by_users = models.ManyToManyField(User, verbose_name='Изучено пользователями',
                                              related_name='learned_by_users')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'name_en': self.name_en,
            'description': self.description,
            'slug': self.slug,
            'parent': self.parent.to_dict() if self.parent else [],
            'text': self.text,
            'more_link': self.more_link,
            'created_at': str(self.created_at.date())
        }

    def __str__(self):
        return self.name

    class MPTTMeta:
        order_insertion_by = ['name']

    class Meta:
        verbose_name = 'Тема'
        verbose_name_plural = 'Темы'
        db_table = 'topics'
        unique_together = ('name', 'parent')


class Attachment(models.Model):
    topic = models.ForeignKey(Topic, verbose_name='Топик',
                              on_delete=models.CASCADE,
                              related_name='attachments')
    name = models.CharField(verbose_name='Название',
                            max_length=150,
                            default=None, blank=True, null=True)
    file = models.FileField(verbose_name='Файл',
                            default=None, blank=True, null=True,
                            upload_to=f"attachments/files/")
    image = models.ImageField(verbose_name='Изображение',
                              default=None, blank=True, null=True,
                              upload_to=f"attachments/images/")

    def to_dict(self):
        return {
            'id': self.pk,
            'name': self.name,
            'file': self.file.path if self.file else None,
            'image': self.image.path if self.image else None
        }

    def __str__(self):
        return f"Приложение {self.name if self.name else self.id} к теме {self.topic.name}"

    class Meta:
        verbose_name = 'Приложение'
        verbose_name_plural = 'Приложения'
        db_table = 'attachments'


@receiver(post_delete, sender=Attachment)
def delete_files(sender, instance, **kwargs):
    try:
        instance.file.delete(False)
    except AttributeError:
        pass
    try:
        instance.image.delete(False)
    except AttributeError:
        pass


class Comment(models.Model):
    topic = models.ForeignKey(Topic, verbose_name='Тема',
                              on_delete=models.CASCADE,
                              related_name='comments',
                              default=None, blank=True, null=True)
    author = models.ForeignKey(User, verbose_name='Автор',
                               on_delete=models.CASCADE,
                               related_name='author_comments',
                               default=None, blank=True, null=True)
    text = models.TextField(verbose_name='Текст',
                            default=None, blank=True, null=True)
    created_at = models.DateTimeField(verbose_name='Дата создания',
                                      auto_now_add=True,
                                      blank=True, null=True)

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        db_table = 'comments'
        ordering = ['created_at']


class Answer(models.Model):
    comment = models.ForeignKey(Comment, verbose_name='Комментарий',
                                on_delete=models.CASCADE,
                                related_name='answers',
                                default=None, blank=True, null=True)
    author = models.ForeignKey(User, verbose_name='Автор',
                               on_delete=models.CASCADE,
                               related_name='author_comment_answers',
                               default=None, blank=True, null=True)
    text = models.TextField(verbose_name='Текст',
                            default=None, blank=True, null=True)
    created_at = models.DateTimeField(verbose_name='Дата создания',
                                      auto_now_add=True,
                                      blank=True, null=True)

    class Meta:
        verbose_name = 'Ответ'
        verbose_name_plural = 'Ответы'
        db_table = 'answers'
        ordering = ['created_at']


class Gallery(models.Model):
    cat = models.CharField(verbose_name='Категория',
                           max_length=150,
                           unique=True)
    created_at = models.DateTimeField(verbose_name='Дата создания',
                                      auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name='Дата обновления',
                                      auto_now=True)

    def __str__(self):
        return self.cat

    class Meta:
        verbose_name = 'Галлерея'
        verbose_name_plural = 'Галлерея'
        db_table = 'gallery'
        ordering = ['-updated_at']


class Artifact(models.Model):
    gallery: Gallery = models.ForeignKey(Gallery, verbose_name='Галлерея',
                                         on_delete=models.CASCADE,
                                         related_name='artifacts')
    name = models.CharField(verbose_name='Название',
                            max_length=150,
                            default=None, blank=True, null=True)
    description = models.TextField(verbose_name='Описание',
                                   default=None, blank=True, null=True)

    file = models.FileField(verbose_name='Файл',
                            default=None, blank=True, null=True,
                            upload_to=f"artifacts/files/")
    image = models.ImageField(verbose_name='Изображение',
                              default=None, blank=True, null=True,
                              upload_to=f"artifacts/images/")

    def to_dict(self):
        return {
            'id': self.pk,
            'name': self.name,
            'file': self.file.path if self.file else None,
            'image': self.image.path if self.image else None
        }

    def __str__(self):
        return f"Артефакт {self.name if self.name else self.id} из галлереи {self.gallery.cat}"

    class Meta:
        verbose_name = 'Артефакт'
        verbose_name_plural = 'Артефакты'
        db_table = 'artifacts'


@receiver(post_delete, sender=Artifact)
def delete_files(sender, instance, **kwargs):
    try:
        instance.file.delete(False)
    except AttributeError:
        pass
    try:
        instance.image.delete(False)
    except AttributeError:
        pass
