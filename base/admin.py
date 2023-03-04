from django.contrib import admin

from .models import *

# Register your models here.
admin.site.register(Live_Counts)
admin.site.register(IP)
admin.site.register(Locations)
admin.site.register(Counts)
admin.site.register(DailyLocations)
admin.site.register(user)
admin.site.register(App)
admin.site.register(Package)
admin.site.register(StripeCustomer)
admin.site.register(Subscription)
admin.site.register(Card)
admin.site.register(PaymentHistory)



