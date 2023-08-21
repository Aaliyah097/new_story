from ckeditor.widgets import CKEditorWidget
from django import forms
from main.models import Comment


class CommentForm(forms.ModelForm):
    text = forms.CharField(widget=CKEditorWidget(),
                           label='Текст',
                           required=True)

    class Meta:
        model = Comment
        fields = ('text', )
