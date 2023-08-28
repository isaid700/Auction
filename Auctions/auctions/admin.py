from django.contrib import admin
from .models import User, listings, Bid, comment

# Register your models here.
admin.site.register(User)
admin.site.register(listings)
admin.site.register(Bid)
admin.site.register(comment)