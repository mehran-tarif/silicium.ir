from django.contrib import admin
from .models import Article, Category, Comment, IpAddress
from .actions import make_published, make_draft
from account.models import User

# Register your models here.
class CategoryAdmin(admin.ModelAdmin):
	list_display = ('position', 'title','slug','status')
	list_filter = (['status'])
	search_fields = ('title', 'slug')
	prepopulated_fields = {'slug': ('title',)}


class ArticleAdmin(admin.ModelAdmin):
	def formfield_for_foreignkey(self, db_field, request, **kwargs):
		if db_field.name == "author":
			kwargs["queryset"] = User.objects.filter(is_staff=True)
		return super().formfield_for_foreignkey(db_field, request, **kwargs)


	list_display = ('title', 'preview_url', 'thumbnail_tag','slug', 'author', 'jpublish', 'status')
	list_filter = ('publish','status', 'author')
	search_fields = ('title', 'description')
	prepopulated_fields = {'slug': ('title',)}
	ordering = ['-status', '-publish']
	actions = [make_published, make_draft]


class CommentAdmin(admin.ModelAdmin):
	list_display = ('article', 'user','content', 'author', 'answer', 'status')
	list_filter = ('article__author', 'status')
	search_fields = ('content',)
	ordering = ['-status', '-created']


admin.site.register(Article, ArticleAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(IpAddress)