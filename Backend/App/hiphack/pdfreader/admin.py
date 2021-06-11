from django.contrib import admin
from .models import Reader
from import_export.admin import ImportExportModelAdmin
from .forms import CreateForm
from import_export.admin import ImportExportModelAdmin
# class ReaderAdmin(admin.ModelAdmin):
#     fieldsets = [
#         (None,               {'fields': ['name']}),
#         ('Date information', {'fields': ['pub_date']}),
#     ]


# Register your models here.


# Register your models here.

class CreateAdmin(admin.ModelAdmin):
   list_display = ['search','name','amount','pub_date']
   form = CreateForm
   list_filter = ['name']
   search_fields = ['name','email']

# admin.site.register(CreateAdmin)

# @admin.register(UserDetail)

# class usrdet(ImportExportModelAdmin):
# 	pass

# admin.site.register(SmartMC,CreateAdmin)
@admin.register(Reader)
class usrdet(ImportExportModelAdmin):
	pass