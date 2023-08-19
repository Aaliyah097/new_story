from django.contrib import admin
from django.urls import reverse
from django_mptt_admin.admin import DjangoMpttAdmin
from .models import *
from mptt.admin import DraggableMPTTAdmin, TreeRelatedFieldListFilter
from .forms import TopicForm
from django.utils.html import mark_safe
from mdeditor.widgets import MDEditorWidget

# Register your models here.


class AnswerInline(admin.TabularInline):
    model = Answer


class ArtifactInline(admin.TabularInline):
    model = Artifact


@admin.register(Artifact)
class ArtifactAdmin(admin.ModelAdmin):
    list_display = ['gallery', 'name']

    list_filter = ['gallery__cat', ]


@admin.register(Gallery)
class GalleryAdmin(admin.ModelAdmin):
    list_display = ['cat', 'updated_at', 'created_at']
    list_filter = ['cat', ]

    inlines = [ArtifactInline, ]


@admin.register(Comment)
class CommentAnswer(admin.ModelAdmin):
    list_display = ('id', 'author', 'topic', 'text', 'created_at')
    inlines = [AnswerInline, ]


@admin.register(Attachment)
class AttachmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_topic_name', 'name',
                    'file', 'image')

    search_fields = ['name', ]

    def get_topic_name(self, obj):
        change_url = reverse("admin:main_topic_change", args=(obj.id,))

        return mark_safe(
            f'<a href="{change_url}" target="_blank">{obj.topic.name}</a>'
        )

    get_topic_name.short_description = 'Топик'


class AttachmentInline(admin.TabularInline):
    model = Attachment


@admin.register(Topic)
class TopicAdmin(DraggableMPTTAdmin):
    search_fields = ('name', 'name_en')

    list_display = ('id',
                    'tree_actions', 'indented_title',
                    'name_en', 'description', 'is_basic',
                    'get_more_link', 'get_text')

    prepopulated_fields = {'slug': ('name',)}
    form = TopicForm
    list_filter = (
        ('parent', TreeRelatedFieldListFilter),
    )
    inlines = [AttachmentInline, ]

    formfield_overrides = {
        models.TextField: {'widget': MDEditorWidget}
    }

    def get_more_link(self, obj):
        return mark_safe(
            f'<a href="{obj.more_link}" target="_blank">Подбробнее</a>'
        ) if obj.more_link else None
    
    get_more_link.short_description = 'Подробнее'

    def get_text(self, obj):
        return mark_safe(
            f"{obj.text[:50]}..."
        )

    get_text.short_description = 'Текст'

