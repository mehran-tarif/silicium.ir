from django.urls import path, include
from .views import CategoryList, CourseList, VideoDetail

app_name = 'course'

urlpatterns = [
    path('', CategoryList.as_view(), name='list'),
	path('<slug:slug>', CourseList.as_view(), name="course"),
    path('<slug:slug>/<int:position>/', VideoDetail.as_view(), name='detail'),
]