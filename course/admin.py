from django.contrib import admin
from .models import Category, Course, Video

# Register your models here.
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('position', 'title','status')
    list_filter = (['status'])
    search_fields = ('title',)


class CourseAdmin(admin.ModelAdmin):
	list_display = ('title', 'category', 'thumbnail_tag','slug', 'author', 'jpublish', 'status')
	list_filter = ('publish','status', 'author', 'category',)
	search_fields = ('title', 'description')
	prepopulated_fields = {'slug': ('title',)}
	ordering = ['position']


class VideoAdmin(admin.ModelAdmin):
	list_display = ('position', 'course', 'title', 'jpublish', 'status')
	list_filter = ('publish','status', 'course')
	search_fields = ('title', 'description')
	ordering = ['position']


admin.site.register(Category, CategoryAdmin)
admin.site.register(Course, CourseAdmin)
admin.site.register(Video, VideoAdmin)