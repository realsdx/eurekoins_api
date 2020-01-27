from django.contrib import admin
from api.models import ApiUser, Transaction, Coupon

class TransactionAdmin(admin.ModelAdmin):
    list_display = ['amount','sender','receiver','created_at','msg']

class CouponAdmin(admin.ModelAdmin):
    list_display = ['code','amount']

class ApiUserAdmin(admin.ModelAdmin):
    list_display = ['email','name','coins']

admin.site.register(ApiUser, ApiUserAdmin)
admin.site.register(Transaction, TransactionAdmin)
admin.site.register(Coupon, CouponAdmin)
