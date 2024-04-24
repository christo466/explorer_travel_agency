from django.apps import AppConfig
from django.contrib import admin

class ExplorerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'userapp'
    def ready(self):
        from .models import UserModel,UserImageModel,ReviewModel,MapArea,Payment
        admin.site.register(UserModel)
        admin.site.register(UserImageModel)
        admin.site.register(ReviewModel)
        admin.site.register(MapArea)
        admin.site.register(Payment)
