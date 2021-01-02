from django.urls import path, include
from .views import ArticleList, ArticleDetail, CategoryList, ArticlePreview

app_name = 'article'

urlpatterns = [
	path('articles/', ArticleList.as_view(), name='list'),
	path('articles/<slug:slug>/', ArticleDetail.as_view(), name='detail'),
	path('articles/<slug:slug>/success/', ArticleDetail.as_view(), name='detail-success'),
	path('category/<slug:slug>', CategoryList.as_view(), name="category"),
	path('preview/<slug:slug>/', ArticlePreview.as_view(), name='preview-detail'),
]