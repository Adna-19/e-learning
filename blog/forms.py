from django import forms 
from .models import Post

class PostForm(forms.ModelForm):
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    for field_name in self.fields.keys():
      self.fields[field_name].widget.attrs.update({
        'class': 'form-control',
        'style': 'width: 44rem;'
      })

  class Meta:
    model = Post
    fields = ['category', 'title', 'image', 'content', 'summary', 'status', 'date_published', 'tags']