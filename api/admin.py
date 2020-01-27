from django.contrib import admin
from api.models import ApiUser, Transaction, Coupon

class TransactionAdmin(admin.ModelAdmin):
    list_display = ['amount','sender','receiver','created_at','msg']

admin.site.register(ApiUser)
admin.site.register(Transaction, TransactionAdmin)
admin.site.register(Coupon)
