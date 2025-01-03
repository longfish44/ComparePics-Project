from django.contrib import admin
from .models import CompareImageModels
from .models import apiModels
from .models import documentModels
from .models import csvModels

admin.site.register(CompareImageModels)

admin.site.register(apiModels)

admin.site.register(documentModels)

admin.site.register(csvModels)
