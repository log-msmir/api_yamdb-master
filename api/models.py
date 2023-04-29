from django.db import models
from django.contrib.auth.models import AbstractUser

from .validators import role_validator, ascii_validator, score_validator


class User(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Администратор'),
        ('moderator', 'Модератор'),
        ('user', 'Пользователь')
    )
    username = models.CharField(max_length=50, unique=True, validators=[ascii_validator])
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=50, default='user', validators=[role_validator],
                            choices=ROLE_CHOICES)
    bio = models.TextField(blank=True, null=True)
    first_name = models.CharField(max_length=50, blank=True, null=True)
    last_name = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        verbose_name_plural = 'Пользователи'
        verbose_name = 'Пользователь'

    def __str__(self) -> str:
        return self.username


class Title(models.Model):
    name = models.CharField(max_length=255)
    year = models.IntegerField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    category = models.ForeignKey('Category', on_delete=models.SET_NULL, null=True)
    genre = models.ManyToManyField('Genre', through='GenreTitle')

    class Meta:
        verbose_name_plural = 'Произведения'
        verbose_name = 'Произведение'

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(validators=[ascii_validator])

    class Meta:
        verbose_name_plural = 'Категории'
        verbose_name = 'Категория'

    def __str__(self) -> str:
        return self.name


class Genre(models.Model):
    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(validators=[ascii_validator])

    class Meta:
        verbose_name_plural = 'Жанры'
        verbose_name = 'Жанр'

    def __str__(self) -> str:
        return self.name


class GenreTitle(models.Model):
    title = models.ForeignKey('Title', on_delete=models.CASCADE)
    genre = models.ForeignKey('Genre', on_delete=models.PROTECT)


class Review(models.Model):
    SCORE_CHOICE = (
        (1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5'),
        (6, '6'), (7, '7'), (8, '8'), (9, '9'), (10, '10')
    )

    title = models.ForeignKey('Title', on_delete=models.CASCADE, related_name='reviews')
    text = models.TextField()
    author = models.ForeignKey('User', on_delete=models.CASCADE, related_name='reviews')
    score = models.PositiveIntegerField(choices=SCORE_CHOICE, validators=[score_validator])
    pub_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Ревью'
        verbose_name = 'Ревью'
        unique_together = ('title', 'author')

    def __str__(self):
        return str(self.title)


class Comment(models.Model):
    review = models.ForeignKey('Review', on_delete=models.CASCADE, related_name='comments')
    text = models.TextField()
    author = models.ForeignKey('User', on_delete=models.CASCADE, related_name='comments')
    pub_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Комментарии'
        verbose_name = 'Комментарий'

    def __str__(self) -> str:
        return self.text


# @receiver(post_save, sender=Title)
# def set_default_for_title(sender, instance, **kwargs):
#     if not instance.category:
#         category, created = Category.objects.get_or_create(name='Без категории',
#                             slug='no-category')
#         instance.category = category
#     if not instance.genre.count():
#         genre, created = Genre.objects.get_or_create(name='Без жанра', slug='no-genre')
#         instance.genre.add(genre)
#         instance.save()
