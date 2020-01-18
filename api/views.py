from django.shortcuts import render
from django.http import JsonResponse, HttpResponseRedirect, HttpResponse
from django.utils import timezone
from django.contrib.admin.views.decorators import staff_member_required
from api.models import ApiUser, Transaction, Coupon

from random import randint, choices
from decouple import config
from hashlib import sha1
import string, datetime


SECRET_AUTH_TOKEN = config('TOKEN')

def index(request):
    return render(request, 'api/index.html',{})

def gen_invite_code(name, email):
    code = ""
    for x in name.split(" "):
        code += x[0]
    code += str(randint(100,999))
    x = ''.join(choices(string.ascii_letters + string.digits, k=5))
    code = "ARHN"+code+x
    return code

def gen_token(email):
    token = sha1((str(email)+SECRET_AUTH_TOKEN).encode())
    return token.hexdigest()

def redeem_coupon(request):
    token = request.GET.get('token')
    code = request.GET.get('code')
    if token and code:
        user = ApiUser.objects.filter(token=token).first()
        if user:
            coupon = Coupon.objects.filter(code=code).first()
            if coupon:
                if not coupon.is_active:
                    return JsonResponse({'status': '4'}) # Coupon expired
                
                # TODO: Check it
                if user in coupon.users.all():
                    return JsonResponse({'status': '3'}) # Coupon already used by user

                # Valid redeem
                user.coins += coupon.amount
                user.coupons_used.add(coupon)
                coupon.use_count += 1
                coupon.save()
                user.save()

                # log transaction
                admin_user = ApiUser.objects.filter(email="avskr@admin.com").first()
                t = Transaction(amount=coupon.amount, sender=admin_user, receiver=user, created_at=timezone.now(), msg="COUPON_REDEEM")
                t.save()
                return JsonResponse({'status': '0'}) # successfull
            else:
                return JsonResponse({'status': '2'}) # No such coupon
        else:
            return JsonResponse({'status': '1'}) # No such user

def transfer_coin(request):
    if request.method == "GET":
        token = request.GET.get('token')
        rcv_email = request.GET.get('email')
        amount = int(request.GET.get('amount', 0))
    
        if token and (rcv_email and amount):
            sender = ApiUser.objects.filter(token=token).first()
            receiver = ApiUser.objects.filter(email=rcv_email).first()

            if not sender:
                return JsonResponse({'status': '1'}) # No sender
            if not receiver:
                return JsonResponse({'status': '2'}) # No receiver
            
            if sender.coins < amount:
                return JsonResponse({'status': '3'}) # Insufficient balance

            if amount <=0 :
                return JsonResponse({'status': '4'}) # Not valid amount
            if sender == receiver:
                return JsonResponse({'status': '5'}) # Not valid

            # Valid data
            sender.coins -= amount
            receiver.coins += amount
            sender.save()
            receiver.save()
            # log transaction
            t = Transaction(amount=amount, sender=sender, receiver=receiver, created_at=timezone.now(), msg="USER_TRANSFER")
            t.save()
            
            return JsonResponse({'status': '0'}) # valid
    
    return JsonResponse({'status':'-1'}) # Error


def register_user(request):
    if request.method == "GET":
        email = request.GET.get('email')
        name = request.GET.get('name')
        image = request.GET.get('image')
        refered_invite_code = request.GET.get('refered_invite_code')
        
        if not (email and name):
            return JsonResponse({'status': '-1' }) # invalid parameters
        
        if ApiUser.objects.filter(email=email).exists():
            return JsonResponse({'status': '1' }) # Email already exists

        # create a new user
        new_user = ApiUser(name=name, email=email, image=image, invite_code=gen_invite_code(name, email))
        new_user.token = gen_token(email)

        refered_by = ApiUser.objects.filter(invite_code=refered_invite_code).first()
        if refered_by:
            # if refered then referer gets +50
            refered_by.coins += 50
            refered_by.save()

            new_user.refered_invite_code = refered_invite_code

            # log transaction
            admin_user = ApiUser.objects.filter(email="avskr@admin.com").first()
            t = Transaction(amount=50, sender=admin_user, receiver=refered_by, created_at=timezone.now(), msg="REFERAL")
            t.save()

        new_user.coins = 50
        new_user.save()

        return JsonResponse({'status': '0'}) # Succesfully registered
    
    return JsonResponse({'status': '3'}) # error


def check_user_exists(request):
    token = request.GET.get('token')
    if token:
        if ApiUser.objects.filter(token=token).exists():
            return JsonResponse({'status': '1'})

    return JsonResponse({'status': '0'})

def get_coins(request):
    token = request.GET.get('token')
    if token:
        user = ApiUser.objects.filter(token=token).first()
        if user:
            return JsonResponse({'status': '0', 'coins': user.coins})
    return JsonResponse({'status': '1'})

def get_invite_code(request):
    token = request.GET.get('token')
    if token:
        user = ApiUser.objects.filter(token=token).first()
        if user:
            return JsonResponse({'status': '0', 'invite_code': user.invite_code})
    return JsonResponse({'status': '1'})

def get_user_list(request):
    pattern = request.GET.get('pattern')
    if pattern:
        users = ApiUser.objects.filter(name__icontains=pattern)
        res_users = []
        for user in users:
            res_users.append([user.name, user.email, user.image])
        
        return JsonResponse({'status':'0', 'users': res_users})
    return JsonResponse({'status': '1'})

def get_transaction_history(request):
    token = request.GET.get('token')
    if token:
        user = ApiUser.objects.filter(token=token).first()
        if user:
            incoming = Transaction.objects.filter(receiver=user)
            outgoing = Transaction.objects.filter(sender=user)
            trns = []
            for i in incoming:
                amount = i.amount
                time = i.created_at
                trns.append([amount, i.sender.email, time])

            for o in outgoing:
                amount = -o.amount
                time = o.created_at
                trns.append([amount, i.receiver.email, time])

            trns = sorted(trns, key=lambda x: x[2])

            return JsonResponse({'status': '0', 'history': trns})
    return JsonResponse({'status': '1'})    


# Admin views
@staff_member_required
def coupon_manager(request):
    coupons = Coupon.objects.all()
    total_count = len(coupons)
    active_count = 0
    total_value = 0
    for c in coupons:
        total_value += c.amount
        if c.is_active:
            active_count += 1
    
    ctx = {'total':total_count, 'active':active_count, 'value':total_value}

    return render(request, 'api/coupon_manager.html', ctx)

@staff_member_required
def add_coupon(request):
    n = int(request.GET.get('number', 5))
    mins = int(request.GET.get('mins', 360))
    amount = int(request.GET.get('amount', 25))
    for c in range(n):
        x = ''.join(choices(string.ascii_letters + string.digits, k=8))
        code = x.upper()
        end = timezone.now()+datetime.timedelta(minutes=mins)
        c = Coupon(code=code, amount=amount, start_time=timezone.now(), end_time=end)
        c.save()

    return HttpResponseRedirect('/api/coupon_manager/', {})

@staff_member_required
def export_coupons(request):
    coupons = Coupon.objects.all()
    content = ""
    for c in coupons:
        content += (c.code+"\n")
    
    response = HttpResponse(content, content_type='text/plain')
    response['Content-Disposition'] = 'attachment; filename="coupons.txt"'
    return response
