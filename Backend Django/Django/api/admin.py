from django.contrib import admin
from .models import User, Category, Services, Link, Request, Evaluation, Report, Provider, Notification, FavoriteServices
# Register your models here.
admin.site.register(User)
admin.site.register(Provider)
admin.site.register(Category)
admin.site.register(Services)
admin.site.register(Evaluation)
admin.site.register(Link)
admin.site.register(Request)
admin.site.register(Report)
admin.site.register(Notification)
admin.site.register(FavoriteServices)
