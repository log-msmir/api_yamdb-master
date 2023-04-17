from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User, Title, Genre
from .forms import UserChangeForm, UserCreationForm


class UserAdmin(UserAdmin):
    add_form = UserCreationForm
    form = UserChangeForm
    model = User
    
    
admin.site.register(User, UserAdmin)
admin.site.register(Title)
admin.site.register(Genre)


