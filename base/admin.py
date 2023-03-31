from django.contrib import admin
from . import models

# Register your models here.
admin.site.register(models.Trait)
admin.site.register(models.Correlation)
admin.site.register(models.Herd)
admin.site.register(models.Cow)
admin.site.register(models.Bull)
admin.site.register(models.TraitsList)
admin.site.register(models.Class)
admin.site.register(models.Enrollment)
admin.site.register(models.Resource)
admin.site.register(models.StaticDataClass)
