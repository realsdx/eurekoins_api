import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "eurekoins.settings")
django.setup()

from api.models import ApiUser, Transaction

def run():
    users = ApiUser.objects.all()
    for u in users:
        tcount =  Transaction.objects.filter(receiver=u, msg="REFERAL").count()
        print(f"{u.name} :: {tcount}")
        u.ref_count = tcount
        u.save()

    print("Done!")

if __name__ == "__main__":
    run()