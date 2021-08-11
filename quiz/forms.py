from django.forms.models import inlineformset_factory
from django import forms
from .models import Question, Answer, Quiz

class QuizForm(forms.ModelForm):
  class Meta:
    model = Quiz
    fields = ['title', 'score']
    widgets = {
      'title': forms.TextInput(attrs={'class': 'form-control'}),
      'score': forms.TextInput(attrs={'class': 'form-control'})
    }

class QuestionForm(forms.ModelForm):
  class Meta:
    model = Question
    fields = ['text']
    widgets = {
      'text': forms.Textarea(attrs={
        'class': 'form-control w-50 mx-auto', 
        'placeholder': 'Add new Question here...',
        'rows': "5",
        'cols': "40"
      }),
    }

AnswersFormSet = inlineformset_factory(Question, Answer, fields=['text', 'is_correct'], extra=4)