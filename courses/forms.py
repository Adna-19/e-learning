from django.forms.models import inlineformset_factory
from django import forms
from .models import Course, Module

class ModuleForm(forms.ModelForm):
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    for field_name in self.fields.keys():
      self.fields[field_name].widget.attrs.update({
        'class': 'form-control'
      })
      
  class Meta:
    model = Module
    fields = ['title', 'summary']