from django.contrib.auth import get_user_model
from django.db import models
from django.core.exceptions import ValidationError

User = get_user_model()


class Group(models.Model):
    title = models.CharField('Имя', max_length=200)
    slug = models.SlugField('url', unique=True)
    description = models.TextField('Описание')

    class Meta:
        verbose_name = 'Группа'
        verbose_name_plural = 'Группы'

    def __str__(self):
        return self.title


class Post(models.Model):

    text = models.TextField('Текст')
    pub_date = models.DateTimeField('Опубликовано', auto_now_add=True)
    author = models.ForeignKey(
        User,
        verbose_name='Автор',
        on_delete=models.CASCADE,
        related_name='posts'
    )
    group = models.ForeignKey(
        Group,
        verbose_name='Группа',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='posts'
    )
    image = models.ImageField(
        'Картинка',
        upload_to='posts/',
        blank=True
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'

    def __str__(self):
        # return str(self.text)[:30] + '...'
        return str(self.text)[:15]


class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        verbose_name='Пост',
        on_delete=models.CASCADE,
        related_name='comments'
    )
    author = models.ForeignKey(
        User,
        verbose_name='Автор',
        on_delete=models.CASCADE,
        related_name='comments'
    )
    text = models.TextField('Текст')
    created = models.DateTimeField('Опубликовано', auto_now_add=True)

    class Meta:
        ordering = ('-created',)
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self):
        return str(self.text)[:15]


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        verbose_name='Пользователь',
        on_delete=models.CASCADE,
        related_name='follower'
    )
    author = models.ForeignKey(
        User,
        verbose_name='Автор',
        on_delete=models.CASCADE,
        related_name='following'
    )

    def clean(self):
        super().clean()
        if self.user == self.author:
            raise ValidationError('user==author')

    def validate_unique(self, exclude=None):
        super().validate_unique()
        if self.author.following.all().filter(
            user=self.user
        ).exists():
            raise ValidationError('user->author exists')

    def is_model_valid(self):
        """
        Проверяет соответствует ли модель условиям
        Пройдёт ли валидацию перед сохранением
        """
        try:
            self.full_clean()
            return True
        except ValidationError:
            return False

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'

    def __str__(self):
        return str(f'{self.user.username}->{self.author.username}')
