import datetime
from django.db import models
from django.utils import timezone
# Create your models here.

class Reader(models.Model):
	search = models.CharField("provide a brief one liner about your research.",max_length=50, blank=True, null=True)
	pub_date = models.DateTimeField('date published')
	email=models.EmailField(max_length=200)
	name = models.CharField("Enter your full name please !", max_length = 100 , blank= True , null = False)
	
	# export_to_CSV = models.BooleanField(default=False)

	def __str__(self):
		return self.name

	def was_published_recently(self):
		return self.pub_date >= timezone.now() - datetime.timedelta(days=1)
