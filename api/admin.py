from django.contrib import admin
from api.models import ApiUser, Transaction, Coupon

admin.site.register(ApiUser)
admin.site.register(Transaction)
admin.site.register(Coupon)
