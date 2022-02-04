from django.db import models
from django.utils import timezone
from datetime import datetime
import uuid

class FreezeTime(models.Model):
    freeze_time = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return "Freeze Time"

class Coupon(models.Model):
    code = models.CharField(max_length=128, unique=True)
    amount = models.IntegerField()
    one_time = models.BooleanField(default=True)
    start_time = models.DateTimeField(default=timezone.now)
    end_time = models.DateTimeField(default=timezone.now)
    use_count = models.PositiveIntegerField(default=0)
    max_usage = models.PositiveIntegerField(default=1)

    def __str__(self):
        return self.code

    @property
    def is_active(self):
        tnow = timezone.now()
        if self.use_count >= self.max_usage:
            return False
        if  self.start_time <= tnow <= self.end_time:
            return True
        return False

    @property
    def is_used(self):
        if self.use_count > 0:
            return True
        return False


class KoinPartner(models.Model):
    """Koin Partners are entities who are partners of the Eurokoin program.
    If an users registers for someting in partner app, they can be rewarded with eurokoins
    """
    partner_name = models.CharField(max_length=256)
    partner_email = models.EmailField(help_text="For transaction log only")
    partner_uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    koin_amount = models.IntegerField(default=0, help_text="Amount to be rewarded")

    def __str__(self):
        return self.partner_name


class ApiUser(models.Model):
    name = models.CharField(max_length=512)
    email = models.EmailField(unique=True)
    coins = models.PositiveIntegerField(default=0)
    coins_before_freeze = models.PositiveIntegerField(default=0)
    invite_code = models.CharField(max_length=16, unique=True)
    refered_invite_code = models.CharField(max_length=16, blank=True, null=True)
    image = models.URLField(blank=True, null=True) 
    token = models.CharField(max_length=1024, unique=True)

    coupons_used = models.ManyToManyField(Coupon, blank=True, related_name="users")
    partners_registerd = models.ManyToManyField(KoinPartner, blank=True, related_name="users_registered")
    ref_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.email
    
    def save(self, *args, **kwargs):
        if timezone.now() <= FreezeTime.objects.first().freeze_time:
            self.coins_before_freeze = self.coins
        super(ApiUser, self).save(*args, **kwargs)

class Transaction(models.Model):
    amount = models.IntegerField()
    sender = models.ForeignKey(ApiUser, on_delete=models.CASCADE)
    receiver = models.ForeignKey(ApiUser, on_delete=models.CASCADE, related_name="receiver_user")
    created_at = models.DateTimeField()
    msg = models.CharField(max_length=512, blank=True, null=True) # for what
    is_in_game = models.BooleanField(default=False)

    def __str__(self):
        return str(self.amount)

class Config(models.Model):
    promo_start_time = models.DateTimeField(default=timezone.now)
    promo_end_time = models.DateTimeField(default=timezone.now)
    promo_coin_value = models.IntegerField(default=50)

    def __str__(self):
        return "Project Settings"

