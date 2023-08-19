from ckeditor.widgets import CKEditorWidget
from django import forms
from ckeditor_uploader.widgets import CKEditorUploadingWidget
from ckeditor.fields import RichTextFormField
from .models import *
from mdeditor.fields import MDTextField
from mdeditor.fields import MDTextFormField


class TopicForm(forms.ModelForm):
    # text = forms.CharField(widget=CKEditorWidget(),
    #                        label='Текст',
    #                        required=False)

    #text = MDTextField()

    #text = forms.CharField(widget=CKEditorWidget(),
                           # label='Текст',
                           # required=False)
    text = MDTextFormField(required=False)

    class Meta:
        model = Topic
        fields = ('name', 'name_en', 'slug',
                  'description', 'parent',
                  'is_basic',
                  'text', 'more_link')


class CommentForm(forms.ModelForm):
    text = forms.CharField(widget=CKEditorWidget(),
                           label='Текст',
                           required=True)

    class Meta:
        model = Comment
        fields = ('text', )

