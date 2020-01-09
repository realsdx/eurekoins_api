from django.db import models
from datetime import datetime


class ApiUser(models.Model):
    name = models.CharField(max_length=512)
    email = models.EmailField(unique=True)
    coins = models.PositiveIntegerField(default=0)
    invite_code = models.CharField(max_length=16, unique=True)
    refered_invite_code = models.CharField(max_length=16, blank=True, null=True)
    image = models.ImageField(blank=True, null=True) 
    cupons_used = models.CharField(max_length=1024, blank=True, null=True) # store as list of strings
    token = models.CharField(max_length=1024, unique=True)

    def __str__(self):
        return self.email

class Coupon(models.Model):
    code = models.CharField(max_length=32)
    amount = models.IntegerField()
    one_time = models.BooleanField(default=True)
    start_time = models.DateTimeField(default=datetime.now)
    end_time = models.DateTimeField(default=datetime.now)

    def __str__(self):
        return self.code


class Transaction(models.Model):
    amount = models.IntegerField()
    sender = models.ForeignKey(ApiUser, on_delete=models.CASCADE)
    recevier = models.ForeignKey(ApiUser, on_delete=models.CASCADE)
    created_at = models.DateTimeField()
    msg = models.CharField(max_length=512, blank=True, null=True) # for what
    is_in_game = models.BooleanField(default=False)

    def __str__(self):
        return self.amount
