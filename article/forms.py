from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Comment


class CommentForm(forms.ModelForm):
	class Meta:
		model = Comment
		fields = ['content']