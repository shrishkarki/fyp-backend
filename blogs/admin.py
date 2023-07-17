from django.contrib import admin

from .models import Category, Blog, Image, Comment, Like

# Register your models here.
admin.site.register([Category, Blog, Image, Comment, Like])
