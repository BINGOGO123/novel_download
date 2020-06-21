from django.contrib import admin

# Register your models here.

from .models import SearchToken,DownloadCache,SearchCache

admin.site.register(SearchToken)
admin.site.register(DownloadCache)
admin.site.register(SearchCache)
