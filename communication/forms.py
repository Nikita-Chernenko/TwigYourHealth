from django import forms
from django.core.exceptions import ValidationError

from communication.models import Message
from communication.utils import _user_belong_to_chat


class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['text', 'chat', 'author']

    # def __init__(self, *args, **kwargs):
    #     self.author = kwargs.pop('author', None)
    #     super(MessageForm, self).__init__(*args, **kwargs)
    #
    # def clean(self):
    #     author = self.author
    #     chat = self.cleaned_data['chat']
    #     if not _user_belong_to_chat(author, chat):
    #         raise ValidationError("User doesn't belong to the chat")
    #
    # def save(self, commit=True):
    #     obj = super(MessageForm, self).save(commit=False)
    #     obj.author = self.author
    #     if commit:
    #         obj.save()
    #     return obj
