import random
from django.urls import reverse
from django.shortcuts import get_object_or_404
from django.views.generic import ListView, DetailView
from django.views.generic.edit import FormMixin
from account.mixins import SuperUserAccessMixin
from .models import Article, IpAddress, Category
from .forms import CommentForm

# Create your views here.
class ArticleList(ListView):
	queryset = Article.objects.published()
	template_name = 'article/list.html'
	paginate_by = 12


class CategoryList(ListView):
	paginate_by = 12
	template_name = 'article/list.html'

	def get_queryset(self):
		global category
		slug = self.kwargs.get('slug')
		category = get_object_or_404(Category.objects.active(), slug=slug)
		return category.articles.published()

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['category'] = category
		return context


class ArticleDetail(FormMixin, DetailView):
	queryset = Article.objects.published()
	template_name = 'article/detail.html'
	form_class = CommentForm

	def get_success_url(self):
		return reverse('article:detail-success', kwargs={'slug': self.object.slug})

	def get_context_data(self, **kwargs):
		# before this i used user
		ip_address = self.request.user.ip_address
		# if user.is_autenticated and ...
		if ip_address not in self.object.hits.all():
			self.object.hits.add(ip_address)

		context = super(ArticleDetail, self).get_context_data(**kwargs)
		context['form'] = CommentForm(initial={'article': self.object})
		# suggested articles
		items = Article.objects.published().exclude(pk=self.object.pk).order_by("-publish")[:10]
		items = list(items)
		random_items = None
		if len(items) >= 3:
			random_items = random.sample(items, 3)
		elif len(items) >= 2:
			random_items = random.sample(items, 2)
		elif len(items) >= 1:
			random_items = random.sample(items, 1)
		context['items'] = random_items
		return context

	def post(self, request, *args, **kwargs):
		self.object = self.get_object()
		form = self.get_form()
		if form.is_valid():
			return self.form_valid(form)
		else:
			return self.form_invalid(form)

	def form_valid(self, form):
		if self.request.user.is_authenticated:
			self.obj = form.save(commit=False)
			self.obj.article = self.object
			self.obj.user = self.request.user
			self.obj.status = False
			form.save()
		return super(ArticleDetail, self).form_valid(form)


class ArticlePreview(SuperUserAccessMixin, DetailView):
	template_name = 'article/detail.html'

	def get_object(self):
		slug = self.kwargs.get('slug')
		return get_object_or_404(Article, slug=slug)

	def get_context_data(self, **kwargs):
		context = super(ArticlePreview, self).get_context_data(**kwargs)
		context['preview'] = True
		return context