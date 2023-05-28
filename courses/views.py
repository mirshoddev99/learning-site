from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.core.cache import cache
from django.db.models import Count
from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.views.generic import ListView, DetailView
from django.views.generic.base import TemplateResponseMixin
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.forms.models import modelform_factory
from courses.forms import ModuleFormSet
from courses.models import Course, Content, Module, Subject
from django.urls import reverse_lazy, reverse
from django.apps import apps
from braces.views import CsrfExemptMixin, JsonRequestResponseMixin
from students.forms import CourseEnrollForm


class Index(View):
    def get(self, request):
        if request.user.is_authenticated:
            return render(request, 'base.html')
        return redirect(reverse('courses:login'))


class ManageCourseListView(ListView):
    model = Course
    template_name = 'courses/manage/course/list.html'

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(owner=self.request.user)


class OwnerMixin:
    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(owner=self.request.user)


class OwnerEditMixin:
    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class OwnerCourseMixin(OwnerMixin, LoginRequiredMixin, PermissionRequiredMixin):
    model = Course
    fields = ['subject', 'title', 'slug', 'overview']

    def get_success_url(self):
        return reverse_lazy('courses:manage_course_list')


class OwnerCourseEditMixin(OwnerCourseMixin, OwnerEditMixin):
    template_name = 'courses/manage/course/form.html'


class CourseCreateView(OwnerCourseEditMixin, CreateView):
    permission_required = 'courses.add_course'


class CourseUpdateView(OwnerCourseEditMixin, UpdateView):
    permission_required = 'courses.change_course'


class CourseDeleteView(OwnerCourseMixin, DeleteView):
    template_name = 'courses/manage/course/delete.html'
    permission_required = 'courses.delete_course'


class ManageCourseListView(OwnerCourseMixin, ListView):
    template_name = 'courses/manage/course/list.html'
    permission_required = 'courses.view_course'


class CourseModuleUpdateView(TemplateResponseMixin, View):
    template_name = 'courses/manage/module/formset.html'
    course = None

    def get_formset(self, data=None):
        return ModuleFormSet(instance=self.course, data=data)

    def dispatch(self, request, pk, *args, **kwargs):
        self.course = get_object_or_404(Course, id=pk, owner=request.user)
        return super().dispatch(request, pk)

    def get(self, request, *args, **kwargs):
        formset = self.get_formset()
        return self.render_to_response({'course': self.course, 'formset': formset})

    def post(self, request, *args, **kwargs):
        formset = self.get_formset(data=request.POST)
        if formset.is_valid():
            formset.save()
            return redirect('courses:manage_course_list')
        return self.render_to_response({'course': self.course, 'formset': formset})


"""
The CourseModuleUpdateView view handles the formset to add, update, and delete modules for a
specific course. This view inherits from the following mixins and views:

• TemplateResponseMixin: This mixin takes charge of rendering templates and returning an
HTTP response. It requires a template_name attribute that indicates the template to be rendered
and provides the render_to_response() method to pass it a context and render the template.

• View: The basic class-based view provided by Django.
In this view, you implement the following methods:
• get_formset(): You define this method to avoid repeating the code to build the formset. You
create a ModuleFormSet object for the given Course object with optional data.

• dispatch(): This method is provided by the View class. It takes an HTTP request and its parameters
and attempts to delegate to a lowercase method that matches the HTTP method used. 
A GET request is delegated to the get() method and a POST request to post(), respectively. In this
method, you use the get_object_or_404() shortcut function to get the Course object for the
given id parameter that belongs to the current user. You include this code in the dispatch()
method because you need to retrieve the course for both GET and POST requests. You save it
into the course attribute of the view to make it accessible to other methods.

• get(): Executed for GET requests. You build an empty ModuleFormSet formset and render it to
the template together with the current Course object using the render_to_response() method
provided by TemplateResponseMixin.

• post(): Executed for POST requests.
• In this method, you perform the following actions:
1. You build a ModuleFormSet instance using the submitted data.
2. You execute the is_valid() method of the formset to validate all of its forms.
3. If the formset is valid, you save it by calling the save() method. At this point, any changes
made, such as adding, updating, or marking modules for deletion, are applied to the
database. Then, you redirect users to the manage_course_list URL. If the formset is
not valid, you render the template to display any errors instead.
"""


class ContentCreateUpdateView(TemplateResponseMixin, View):
    module = None
    model = None
    obj = None
    template_name = 'courses/manage/content/form.html'

    def get_model(self, model_name):
        if model_name in ['text', 'video', 'image', 'file']:
            return apps.get_model(app_label='courses', model_name=model_name)
        return None

    def get_form(self, model, *args, **kwargs):
        Form = modelform_factory(model, exclude=['owner', 'order', 'updated'])
        return Form(*args, **kwargs)

    def dispatch(self, request, module_id, model_name, id=None):
        self.module = get_object_or_404(Module, id=module_id, course__owner=request.user)
        self.model = self.get_model(model_name)
        if id:
            self.obj = get_object_or_404(self.model, id=id, owner=request.user)
        return super().dispatch(request, module_id, model_name, id)

    def get(self, request, module_id, model_name, id=None):
        form = self.get_form(self.model, instance=self.obj)
        return self.render_to_response({'form': form, 'object': self.obj})

    def post(self, request, module_id, model_name, id=None):
        form = self.get_form(self.model, instance=self.obj, data=request.POST, files=request.FILES)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.owner = request.user
            obj.save()
            if not id:
                # new content
                Content.objects.create(module=self.module, item=obj)
            return redirect('courses:module_content_list', self.module.id)

        return self.render_to_response({'form': form, 'object': self.obj})


class ContentDeleteView(View):
    def post(self, request, id):
        content = get_object_or_404(Content, id=id, module__course__owner=request.user)
        module = content.module
        content.item.delete()
        content.delete()
        return redirect('courses:module_content_list', module.id)


class ModuleContentListView(TemplateResponseMixin, View):
    template_name = 'courses/manage/module/content_list.html'

    def get(self, request, module_id):
        module = get_object_or_404(Module, id=module_id, course__owner=request.user)
        return self.render_to_response({'module': module})


class ModuleOrderView(CsrfExemptMixin, JsonRequestResponseMixin, View):
    def post(self, request):
        for id, order in self.request_json.items():
            Module.objects.filter(id=id, course__owner=request.user).update(order=order)
        return self.render_json_response({"saved": "OK"})


class ContentOrderView(CsrfExemptMixin, JsonRequestResponseMixin, View):
    def post(self, request):
        for id, order in self.request_json.items():
            Content.objects.filter(id=id, module__course__owner=request.user).update(order=order)
        return self.render_json_response({"saved": "OK"})


class CourseListView(TemplateResponseMixin, View):
    model = Course
    template_name = 'courses/course/list.html'

    def get(self, request, subject=None):
        if request.user.is_authenticated:
            subjects = cache.get('all_subjects')
            if not subjects:
                subjects = Subject.objects.annotate(
                    total_courses=Count('courses'))
                cache.set('all_subjects', subjects, 60)    # cache expire time is set up 1 sec
            all_courses = Course.objects.annotate(
                total_modules=Count('modules'))

            if subject:
                key = f"subject_{subject}_courses"
                courses = cache.get(key)
                if not courses:
                    courses = all_courses.filter(subject__slug=subject)
                    print(courses)
                    cache.set(key, courses, 60)
            elif not subject:
                # it is impossible to build a new QuerySet using cached QuerySet
                courses = cache.get('all_courses')
                if not courses:
                    courses = all_courses
                    cache.set('all_courses', courses, 60)

            return self.render_to_response({"subjects": subjects, "subject": subject, "courses": courses})
        return redirect(reverse("courses:login"))


class CourseDetailView(DetailView):
    model = Course
    template_name = 'courses/course/detail.html'
    context_object_name = 'object'

    def get_context_data(self, **kwargs):
        contex = super().get_context_data(**kwargs)
        contex['enroll_form'] = CourseEnrollForm(initial={"course": self.object})
        return contex
