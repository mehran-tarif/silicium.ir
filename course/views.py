from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.views.generic import ListView, DetailView
from .models import Category, Course, Video

# Create your views here.
class CategoryList(ListView):
	queryset = Category.objects.active()
	template_name = 'course/list.html'


class CourseList(ListView):
	template_name = 'course/course.html'

	def get_queryset(self):
		global course
		slug = self.kwargs.get('slug')
		course = get_object_or_404(Course.objects.active(), slug=slug)
		return course.videos.active()

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['course'] = course
		return context


class VideoDetail(DetailView):
	template_name = 'course/detail.html'

	def get_object(self):
		slug = self.kwargs.get('slug')
		position = self.kwargs.get('position')
		return get_object_or_404(Video.objects.active(), course__slug=slug, position=position)

	def get_context_data(self, **kwargs):
		# before this i used user
		ip_address = self.request.user.ip_address
		# if user.is_autenticated and ...
		if ip_address not in self.object.hits.all():
			self.object.hits.add(ip_address)

		context = super(VideoDetail, self).get_context_data(**kwargs)
		# suggested articles
		slug = self.kwargs.get('slug')
		position = self.kwargs.get('position')
		next_video = Video.objects.filter(course__slug=slug, position=position + 1, status=True).first()
		if next_video:
			context['next_video'] = next_video
		prev_video = Video.objects.filter(course__slug=slug, position=position - 1, status=True).first()
		if prev_video:
			context['prev_video'] = prev_video
		return context