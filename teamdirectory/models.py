from django.db import models
from django.utils.text import slugify


# Create your models here.
class Person(models.Model):
    id = models.IntegerField(primary_key=True, auto_created=True, unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.CharField(max_length=200)
    title = models.CharField(max_length=100)
    linkedin_url = models.CharField(max_length=200, null=True)
    github_url = models.CharField(max_length=200, null=True)
    twitter_url = models.CharField(max_length=200, null=True)
    image = models.CharField(max_length=500)
    slug = models.SlugField(max_length=100, blank=True)

    def save(self, *args, **kwargs):
        if not self.pk:
            slug = slugify(self.first_name + self.last_name)
        super(Person, self, *args, **kwargs)

    def __repr__(self):
        return "<id: %r, Title: %r, Name:<%r %r>, Email: %r ImgUrl: %r>" % (
            self.id, self.title, self.first_name, self.last_name, self.email, self.image)
