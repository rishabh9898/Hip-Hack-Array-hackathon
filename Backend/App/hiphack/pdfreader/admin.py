from django.contrib import admin
from .models import Reader


class ReaderAdmin(admin.ModelAdmin):
    fieldsets = [
        (None,               {'fields': ['name']}),
        ('Date information', {'fields': ['pub_date']}),
    ]

admin.site.register(Reader,ReaderAdmin)

# Register your models here.
