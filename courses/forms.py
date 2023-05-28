from django.forms.models import inlineformset_factory
from .models import Course, Module

ModuleFormSet = inlineformset_factory(Course, Module, fields=['title', 'description'], extra=1, can_delete=True)

"""This is the ModuleFormSet formset. You build it using the inlineformset_factory() function provided
by Django. Inline formsets are a small abstraction on top of formsets that simplify working with
related objects. This function allows you to build a model formset dynamically for the Module objects
related to a Course object.

You use the following parameters to build the formset:
• fields: The fields that will be included in each form of the formset.
• extra: Allows you to set the number of empty extra forms to display in the formset.
• can_delete: If you set this to True, Django will include a Boolean field for each form that will
be rendered as a checkbox input. It allows you to mark the objects that you want to delete."""