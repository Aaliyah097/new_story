from django import forms
from .models import *
from mdeditor.fields import MDTextFormField


class TopicForm(forms.ModelForm):
    text = MDTextFormField(required=False)

    class Meta:
        model = Topic
        fields = ('name', 'name_en', 'slug',
                  'description', 'parent',
                  'is_basic',
                  'text', 'more_link')
