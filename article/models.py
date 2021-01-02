from django.db import models
from django.utils import timezone
from django.utils.html import format_html
from django.urls import reverse
from django.core.mail import EmailMessage
from ckeditor.fields import RichTextField
from ckeditor_uploader.fields import RichTextUploadingField
from account.models import User
from extensions.utils import jalali_converter

# Create your managers here.
class ArticleManager(models.Manager):
	def published(self):
		return self.filter(status='p')


class CategoryManager(models.Manager):
	def active(self):
		return self.filter(status=True)


class CommentManager(models.Manager):
	def active(self):
		return self.filter(status=True)


# Create your models here.
class IpAddress(models.Model):
	pub_date = models.DateTimeField('زمان اولین بازدید')
	ip_address = models.GenericIPAddressField(verbose_name='آدرس')

	class Meta:
		verbose_name = "آی‌پی"
		verbose_name_plural = "آی‌پی ها"
		ordering = ['pub_date']

	def __str__(self):
		return self.ip_address


class Category(models.Model):
	title = models.CharField(max_length=200, verbose_name="عنوان دسته‌بندی")
	slug = models.SlugField(max_length=100, unique=True, verbose_name="آدرس دسته‌بندی")
	status = models.BooleanField(default=True, verbose_name="آیا نمایش داده شود؟")
	position = models.IntegerField(verbose_name="پوزیشن")

	class Meta:
		verbose_name = "دسته‌بندی"
		verbose_name_plural = "دسته‌بندی ها"
		ordering = ['position']

	def __str__(self):
		return self.title

	objects = CategoryManager()

	def save(self, *args, **kwargs):
		if not self.status:
			for article in self.articles.published():
				article.status = 'd'
				article.save()
		super(Category, self).save(*args, **kwargs)


class Article(models.Model):
	STATUS_CHOICES = (
		('d', 'پیش‌نویس'),		 # draft
		('p', "منتشر شده"),		 # publish
	)

	author = models.ForeignKey(User, null=True, on_delete=models.SET_NULL, related_name='articles', verbose_name="نویسنده")
	title = models.CharField(max_length=200, verbose_name="عنوان مقاله")
	slug = models.SlugField(max_length=100, unique=True, verbose_name="آدرس مقاله")
	category = models.ForeignKey(Category, null=True, on_delete=models.SET_NULL, verbose_name="دسته‌بندی", related_name="articles")
	description = RichTextUploadingField(verbose_name="محتوا")
	thumbnails = models.ImageField(upload_to="images/article", verbose_name="تصویر ۶۴۰x۳۶۰ مقاله")
	thumbnail = models.ImageField(upload_to="images/article", verbose_name="تصویر مقاله")
	publish = models.DateTimeField(default=timezone.now, verbose_name="زمان انتشار")
	created = models.DateTimeField(auto_now_add=True)
	updated = models.DateTimeField(auto_now=True)
	status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='d', verbose_name="وضعیت")
	hits = models.ManyToManyField(IpAddress, through="ArticleHit", blank=True, related_name='hits', verbose_name='بازدیدها')

	class Meta:
		verbose_name = "مقاله"
		verbose_name_plural = "مقالات"
		ordering = ['-publish']

	objects = ArticleManager()

	def __str__(self):
		return self.title

	def jpublish(self):
		return jalali_converter(self.publish)
	jpublish.short_description = "زمان انتشار"

	def thumbnail_tag(self):
		return format_html("<img width=100 height=75 style='border-radius: 5px;' src='{}'>".format(self.thumbnails.url))
	thumbnail_tag.short_description = "عکس"

	def preview_url(self):
		return format_html("<a href='{}' target='blank'>پیش‌نمایش</a>".format(reverse("article:preview-detail", kwargs={'slug': self.slug})))
	preview_url.short_description = "پیش‌نمایش"

	def save(self, *args, **kwargs):
		if self.status == "d":
			for comment in self.comments.active():
				comment.status = False
				comment.save()
		super(Article, self).save(*args, **kwargs)


class Comment(models.Model):
	article = models.ForeignKey(Article, null=True, on_delete=models.SET_NULL, related_name="comments", verbose_name="مقاله")
	user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL, related_name="comments", verbose_name="کاربر")
	content = RichTextField(verbose_name="دیدگاه")
	author = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name="answers", verbose_name="پاسخ‌دهنده")
	answer = RichTextField(blank=True, verbose_name="پاسخ")
	created = models.DateTimeField(auto_now_add=True)
	updated = models.DateTimeField(auto_now=True)
	status = models.BooleanField(default=False, verbose_name="تایید")

	class Meta:
		verbose_name = "دیدگاه"
		verbose_name_plural = "دیدگاه‌ها"
		ordering = ['-created']

	objects = CommentManager()

	def save(self, *args, **kwargs):
		if self.article and self.user and self.content and not self.author and not self.answer and not self.status:
			email = EmailMessage(
				"دیدگاه جدید",
				"<p style='direction: rtl;text-align: right;'>سلام، دیدگاه جدیدی برای مقاله ات هست: <a href='https://silicium.ir/admin/article/comment/?article__author__id__exact={}&status__exact=0'>مشاهده</a></p>".format(self.article.author.pk),
				to=[self.article.author.email]
			)
			email.content_subtype = "html"
			email.send()
		elif self.article and self.user and self.content and self.status and (not self.author or not self.answer):
			email = EmailMessage(
				"دیدگاه شما تایید شد (:",
				"<p style='direction: rtl;text-align: right;'>سلام، دیدگاه شما که مدتی قبل برامون نوشته بودید، تایید شد: <a href='https://silicium.ir{}'>مشاهده</a><br>ممنون از دیدگاهتون</p>".format(reverse("article:detail", kwargs={'slug': self.article.slug})),
				to=[self.user.email]
			)
			email.content_subtype = "html"
			email.send()
		elif self.article and self.user and self.content and self.status and self.author and self.answer:
			email = EmailMessage(
				"به دیدگاه شما پاسخ دادیم (:",
				"<p style='direction: rtl;text-align: right;'>سلام، دیدگاه شما که مدتی قبل برامون نوشته بودید، تایید شد و بهش پاسخ دادیم: <a href='https://silicium.ir{}'>مشاهده</a><br>ممنون از دیدگاهتون</p>".format(reverse("article:detail", kwargs={'slug': self.article.slug})),
				to=[self.user.email]
			)
			email.content_subtype = "html"
			email.send()
		super(Comment, self).save(*args, **kwargs)


class ArticleHit(models.Model):
	article = models.ForeignKey(Article, on_delete=models.CASCADE)
	ip_address = models.ForeignKey(IpAddress, on_delete=models.CASCADE)
	created = models.DateTimeField(auto_now_add=True)