from django.contrib import admin

from .models import User, Category, Listing, Bid, BidItem, Comment, Watcher

# Register your models here.

class WatcherAdmin(admin.ModelAdmin):
    filter_horizontal = ("listings",)

admin.site.register(User)
admin.site.register(Category)
admin.site.register(Listing)
admin.site.register(Bid)
admin.site.register(BidItem)
admin.site.register(Comment)
admin.site.register(Watcher, WatcherAdmin)