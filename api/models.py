from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save
from django.dispatch import receiver

from .validators import role_validator, ascii_validator



class User(AbstractUser):
    username = models.CharField(max_length=50, unique=True, validators=[ascii_validator])
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=50, default='user', validators=[role_validator])
    bio = models.TextField(blank=True, null=True)
    first_name = models.CharField(max_length=50, blank=True, null=True)
    last_name = models.CharField(max_length=50, blank=True, null=True)
    
    def __str__(self) -> str:
        return self.username
    


class Title(models.Model):
    name = models.CharField(max_length=255)
    year = models.PositiveIntegerField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    category  = models.ForeignKey('Category', on_delete=models.SET_NULL, null=True)
    genre = models.ManyToManyField('Genre', through='GenreTitle')
    
    
    def __str__(self) -> str:
        return self.name
   
   
class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(validators=[ascii_validator])
    
    def __str__(self) -> str:
        return self.name


class Genre(models.Model):
    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(validators=[ascii_validator])
      
    def __str__(self) -> str:
        return self.name
    
    
class GenreTitle(models.Model):
    title = models.ForeignKey('Title', on_delete=models.CASCADE)
    genre = models.ForeignKey('Genre', on_delete=models.SET_DEFAULT, default=20)


class Review(models.Model):
    title = models.ForeignKey('Title', on_delete=models.CASCADE, related_name='reviews')
    text = models.TextField()
    author = models.ForeignKey('User', on_delete=models.CASCADE, related_name='reviews')
    score = models.PositiveIntegerField()
    pub_date = models.DateTimeField(auto_now_add=True)
    
    def __str__(self) -> str:
        return self.title
    
    class Meta:
        unique_together = ('title', 'author')
    

class Comment(models.Model):
    review = models.ForeignKey('Review', on_delete=models.CASCADE, related_name='comments')
    text = models.TextField()
    author = models.ForeignKey('User', on_delete=models.CASCADE, related_name='comments')
    pub_date = models.DateTimeField(auto_now_add=True)
    
    def __str__(self) -> str:
        return self.text




@receiver(post_save, sender=Title)
def set_default_for_title(sender, instance, **kwargs):
    if not instance.category:
        category, created = Category.objects.get_or_create(name='Без категории', slug='no-category')
        instance.category = category
    if not instance.genre.count():
        genre, created = Genre.objects.get_or_create(name='Без жанра', slug='no-genre')
        instance.genre.add(genre)
        instance.save()