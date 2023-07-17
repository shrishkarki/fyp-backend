from django.db import models
from django.utils.text import slugify
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.utils import timezone

from PIL import Image as PILImage

from .utils import unique_slug_generator
from accounts.models import Account


class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(max_length=255, unique=True, null=True, blank=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now_add=True,null=True,blank=True)

    # customize save method to automatically create slug
    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['-modified_at', '-created_at']




class Blog(models.Model):
    title = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True, null=True, blank=True)
    author = models.ForeignKey(Account, on_delete=models.CASCADE)
    pub_date = models.DateTimeField('date published', auto_now_add=True)
    body = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    class Meta:
        ordering = ['-pub_date']

    def __str__(self):
        return self.title

@receiver(post_save, sender=Blog)
def add_modified_date_to_category(sender, instance, **kwargs):
    instance.category.modified_at = timezone.now()
    instance.category.save()

class Image(models.Model):
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='images/', null=True, blank=True)
    
    def __str__(self):
        return self.image.__str__()

    # compress image when saving
    def save(self, *args, **kwargs):
        super(Image, self).save(*args, **kwargs)

        img = PILImage.open(self.image.path)
        height, width = img.size

        img = img.resize((width//2, height//2), PILImage.ANTIALIAS)
        img.save(self.image.path, optimize=True, quality=95)
        print(img.size)




# Model for the post comments
class Comment(models.Model):
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE, related_name='comments')
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='comments')
    comment = models.CharField(max_length=200)
    commented_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['commented_at']

    def __str__(self):
        return self.comment


# Model for the post likes
class Like(models.Model):
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE, related_name='likes')
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    liked_at = models.DateTimeField(auto_now_add=True)

    # a user can only like a post once
    class Meta:
        unique_together = ('blog', 'account')
        ordering = ['-liked_at']

    def __str__(self):
        return self.account.username


# signal to create slug after saving the blog
@receiver(post_save, sender=Blog)
def create_slug(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = unique_slug_generator(instance)
        instance.save()
