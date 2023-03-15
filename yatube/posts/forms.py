from django.forms import ModelForm
from posts.models import Post


class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = ('group', 'text', 'image')
        labels = {'group': 'Группа',
                  'text': 'Текст'}
        help_texts = {"text": "Обязательное поле!",
                      "group": "Необязательное поле!", }
