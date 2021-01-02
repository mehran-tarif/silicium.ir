from django.db import models
from django.utils import timezone
from django.utils.html import format_html
from ckeditor.fields import RichTextField
from ckeditor_uploader.fields import RichTextUploadingField
from account.models import User
from extensions.utils import jalali_converter
from article.models import IpAddress

# Create your models here.
class CategoryManager(models.Manager):
	def active(self):
		return self.filter(status=True)

class CourseManager(models.Manager):
	def active(self):
		return self.filter(status=True)

class VideoManager(models.Manager):
	def active(self):
		return self.filter(status=True)


# Create your models here.
class Category(models.Model):
	title = models.CharField(max_length=200, verbose_name="عنوان دسته‌بندی")
	status = models.BooleanField(default=True, verbose_name="آیا نمایش داده شود؟")
	position = models.IntegerField(verbose_name="پوزیشن")

	class Meta:
		verbose_name = "دسته‌بندی"
		verbose_name_plural = "دسته‌بندی ها"
		ordering = ['position']

	def __str__(self):
		return self.title

	def save(self, *args, **kwargs):
		if not self.status:
			for course in self.courses.active():
				course.status = False
				course.save()
		super(Category, self).save(*args, **kwargs)

	objects = CategoryManager()


class Course(models.Model):
	author = models.ForeignKey(User, null=True, on_delete=models.SET_NULL, related_name='courses', verbose_name="مدرس")
	title = models.CharField(max_length=200, verbose_name="عنوان دوره")
	slug = models.SlugField(max_length=100, unique=True, verbose_name="آدرس دوره")
	category = models.ForeignKey(Category, null=True, on_delete=models.SET_NULL, verbose_name="دسته‌بندی", related_name="courses")
	description = RichTextUploadingField(verbose_name="توضیحات")
	address = models.URLField(verbose_name="لینک یوتیوب")
	thumbnails = models.ImageField(upload_to="images/course", verbose_name="تصویر ۶۴۰x۳۶۰ مقاله")
	thumbnail = models.ImageField(upload_to="images/course", verbose_name="تصویر دوره")
	publish = models.DateTimeField(default=timezone.now, verbose_name="زمان انتشار")
	created = models.DateTimeField(auto_now_add=True)
	updated = models.DateTimeField(auto_now=True)
	position = models.IntegerField(verbose_name="پوزیشن")
	status = models.BooleanField(default=True, verbose_name="آیا نمایش داده شود؟")

	class Meta:
		verbose_name = "دوره"
		verbose_name_plural = "دوره ها"
		ordering = ['position']

	objects = CourseManager()

	def __str__(self):
		return self.title

	def save(self, *args, **kwargs):
		if not self.status:
			for video in self.videos.active():
				video.status = False
				video.save()
		super(Course, self).save(*args, **kwargs)

	def jpublish(self):
		return jalali_converter(self.publish)
	jpublish.short_description = "زمان انتشار"

	def thumbnail_tag(self):
		return format_html("<img width=100 height=75 style='border-radius: 5px;' src='{}'>".format(self.thumbnails.url))
	thumbnail_tag.short_description = "عکس"


class Video(models.Model):
	position = models.IntegerField(verbose_name="شماره جلسه", unique=True)
	title = models.CharField(max_length=200, verbose_name="عنوان جلسه")
	course = models.ForeignKey(Course, null=True, on_delete=models.SET_NULL, verbose_name="دوره", related_name="videos")
	description = RichTextUploadingField(verbose_name="توضیحات")
	iframe = models.TextField(verbose_name="آی‌فریم یوتیوب")
	address = models.URLField(verbose_name="لینک یوتیوب")
	publish = models.DateTimeField(default=timezone.now, verbose_name="زمان انتشار")
	created = models.DateTimeField(auto_now_add=True)
	updated = models.DateTimeField(auto_now=True)
	status = models.BooleanField(default=True, verbose_name="آیا نمایش داده شود؟")
	hits = models.ManyToManyField(IpAddress, through="VideoHit", blank=True, related_name='video_hits', verbose_name='بازدیدها')

	class Meta:
		verbose_name = "ویدیو"
		verbose_name_plural = "ویدیوها"
		ordering = ['position']

	objects = VideoManager()

	def __str__(self):
		return self.title

	def jpublish(self):
		return jalali_converter(self.publish)
	jpublish.short_description = "زمان انتشار"


class VideoHit(models.Model):
	video = models.ForeignKey(Video, on_delete=models.CASCADE)
	ip_address = models.ForeignKey(IpAddress, on_delete=models.CASCADE)
	created = models.DateTimeField(auto_now_add=True)