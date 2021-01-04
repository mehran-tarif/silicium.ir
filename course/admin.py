from django.contrib import admin
from .models import Category, Course, Video
from account.models import User

# Register your models here.
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('position', 'title','status')
    list_filter = (['status'])
    search_fields = ('title',)


class CourseAdmin(admin.ModelAdmin):
	def formfield_for_foreignkey(self, db_field, request, **kwargs):
		if db_field.name == "author":
			kwargs["queryset"] = User.objects.filter(is_staff=True)
		return super().formfield_for_foreignkey(db_field, request, **kwargs)

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