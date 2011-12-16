from django import forms
from models import Comment, Freggie

class FreggieForm(forms.ModelForm):
    class Meta:
        model = Freggie
        fields = ('freggie','freggie_other','quantity', 'text', 'photo' )


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)