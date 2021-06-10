from django.db import models

# Create your models here.

class Reader(models.Model):
	name = models.CharField("Please Enter your Full Name",max_length=50, blank=True, null=True)
	pub_date = models.DateTimeField('date published')
	email=models.EmailField(max_length=200)
	
	# export_to_CSV = models.BooleanField(default=False)

	def __str__(self):
		return self.name