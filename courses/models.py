from django.contrib.auth.models import User
from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.template.loader import render_to_string

from .fields import OrderField


class Subject(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)

    class Meta:
        ordering = ['title']

    def __str__(self):
        return self.title


class Course(models.Model):
    owner = models.ForeignKey(User, related_name='courses_created', on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, related_name='courses', on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    overview = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    students = models.ManyToManyField(User, related_name='courses_joined', blank=True)

    class Meta:
        ordering = ['-created']

    def __str__(self):
        return self.title


class Module(models.Model):
    course = models.ForeignKey(Course, related_name='modules', on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    order = OrderField(blank=True, for_fields=['course'], default=False)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.order} {self.title}"


"""There is one to many relationship between Module and Course. 
"Each Course instance can have many Module instances related to them"""

"""
These are the initial Subject, Course, and Module models. The Course model fields are as follows:
• owner: The instructor who created this course.
• subject: The subject that this course belongs to. It is a ForeignKey field that points to the Subject model.
• title: The title of the course.
• slug: The slug of the course. This will be used in URLs later.
• overview: A TextField column to store an overview of the course.
• created: The date and time when the course was created. It will be automatically set by Django
when creating new objects because of auto_now_add=True.

Each course is divided into several modules. Therefore, the Module model contains a ForeignKey field
that points to the Course model.
"""


class Content(models.Model):
    module = models.ForeignKey(Module, related_name='contents', on_delete=models.CASCADE)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE,
                                     limit_choices_to={'model__in': ('text', 'video', 'image', 'file')})
    object_id = models.PositiveIntegerField()
    item = GenericForeignKey('content_type', 'object_id')
    order = OrderField(blank=True, for_fields=['module'], default=False)

    class Meta:
        ordering = ['order']


class ItemBase(models.Model):
    owner = models.ForeignKey(User, related_name='%(class)s_related', on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

    def __str__(self):
        return self.title

    def render(self):
        return render_to_string(
            f'courses/content/{self._meta.model_name}.html',
            {'item': self})


class Text(ItemBase):
    content = models.TextField()


class File(ItemBase):
    file = models.FileField(upload_to='files')


class Image(ItemBase):
    file = models.FileField(upload_to='images')


class Video(ItemBase):
    url = models.URLField()


"""
                            -----Abstract models-----

An abstract model is a base class in which you define the fields you want to include in all child models.
Django doesn’t create any database tables for abstract models. 
A database table is created for each child
model, including the fields inherited from the abstract class and the ones defined in the child model.
To mark a model as abstract, you need to include abstract=True in its Meta class. 
Django will recognize
that it is an abstract model and will not create a database table for it. 
To create child models, you just
need to subclass the abstract model.
"""
