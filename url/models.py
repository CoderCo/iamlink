from django.db import models
from django.core.validators import MaxLengthValidator
class URL(models.Model):
    title = models.CharField(
        max_length=100,
        validators=[
            MaxLengthValidator(100)
        ],
        help_text='Название ссылки для индентификации',
        null=True,
    )
    company = models.CharField(
        max_length=50,
        help_text='Домен вида example.ru',
        null=True,
    )
    hash = models.CharField(max_length=10, unique=True)
    url = models.URLField()
    visits = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.url
