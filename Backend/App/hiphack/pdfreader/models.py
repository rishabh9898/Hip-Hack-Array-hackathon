import datetime
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.contrib.admin.widgets import AdminDateWidget, AdminTimeWidget, AdminSplitDateTime
from embed_video.fields import EmbedVideoField



# Create your models here.

class Reader(models.Model):
	search = models.CharField("provide a brief one liner about your research.",max_length=50, blank=True, null=True)
	pub_date = models.DateTimeField('date published')
	email=models.EmailField(max_length=200)
	name = models.CharField("Please Enter your Full Name",max_length=50, blank=True, null=True)
	amount = models.IntegerField("Papers you need",default='0', blank=True, null=True)
	
	# export_to_CSV = models.BooleanField(default=False)

	def __str__(self):
		return self.name

	def was_published_recently(self):
		return self.pub_date >= timezone.now() - datetime.timedelta(days=1)

