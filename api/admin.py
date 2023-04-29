from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User, Title, Genre, Review, Comment, Category, GenreTitle
from .forms import UserChangeForm, UserCreationForm


class UserAdmin(BaseUserAdmin):
    add_form = UserCreationForm
    form = UserChangeForm
    model = User
    list_display = ('username', 'email', 'role')


UserAdmin.fieldsets += ('Custom fields set', {'fields': ('role', 'bio')}),


class ReviewInLine(admin.TabularInline):
    model = Review


class GenreInLine(admin.TabularInline):
    model = GenreTitle


class CommentInLine(admin.TabularInline):
    model = Comment


class TitleAdmin(admin.ModelAdmin):
    model = Title
    inlines = [ReviewInLine, GenreInLine]
    list_display = ('id', 'name', 'category')


class ReviewAdmin(admin.ModelAdmin):
    model = Review
    inlines = [CommentInLine,]
    list_display = ('id', 'text', 'author')


admin.site.register(User, UserAdmin)
admin.site.register(Title, TitleAdmin)
admin.site.register(Category)
admin.site.register(Genre)
admin.site.register(Review, ReviewAdmin)
admin.site.register(Comment)
