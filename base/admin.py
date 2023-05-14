from django.contrib import admin
from . import models

# Register your models here.
admin.site.register(models.Herd)
admin.site.register(models.Cow)
admin.site.register(models.Bull)
admin.site.register(models.Bovine)
admin.site.register(models.Class)
admin.site.register(models.Enrollment)
admin.site.register(models.Pedigree)
