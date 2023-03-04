from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Package(models.Model):
    name = models.CharField(max_length=64)
    price = models.FloatField(default=0.0)
    max_requests = models.IntegerField(default=0)
    max_apps = models.IntegerField(default=0,null=True)

    def __str__(self):
        return self.name

class user(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE,null=True)
    api_key = models.CharField(max_length=100,null=False,blank=False)
    package = models.ForeignKey(Package,on_delete=models.SET_NULL,null=True)
    request_made = models.IntegerField(default=0,null=True,blank=True)

    def __str__(self):
        return self.user.username

class App(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE,null=True)
    name = models.CharField(max_length=64,null=False,blank=False)

    def __str__(self):
        return self.name

class StripeCustomer(models.Model):
    user = models.OneToOneField(to=User, on_delete=models.CASCADE)
    stripeCustomerId = models.CharField(max_length=255)

    def __str__(self):
        return self.user.username

class Subscription(models.Model):
    user = models.OneToOneField(to=User, on_delete=models.CASCADE)
    stripeSubscriptionId = models.CharField(max_length=255)
    plan = models.ForeignKey(Package,on_delete=models.SET_NULL,null=True)
    current_period_start = models.CharField(max_length=64)
    current_period_end = models.CharField(max_length=64)

    def __str__(self):
        return self.user.username

class Card(models.Model):
    user = models.OneToOneField(to=User, on_delete=models.CASCADE)
    brand = models.CharField(max_length=64)
    exp_month = models.IntegerField()
    exp_year = models.IntegerField()
    last4 = models.BigIntegerField()

    def __str__(self):
        return self.user.username

class PaymentHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.FloatField(default=0.0)
    status = models.CharField(max_length=64)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username









#live tracking models
class Locations(models.Model):
    city = models.CharField(max_length=120)
    country = models.CharField(max_length=120)
    longtitute = models.CharField(max_length=120)
    lattitute = models.CharField(max_length=120)

    def __str__(self):
        return self.country

class IP(models.Model):
    address = models.CharField(max_length=64)

    def __str__(self):
        return self.address

class Live_Counts(models.Model):
    app = models.ForeignKey(App,null=True,on_delete=models.CASCADE)
    user = models.IntegerField(default=0)
    desktop = models.IntegerField(default=0)
    mobile = models.IntegerField(default=0)
    locations = models.ManyToManyField(Locations,null=True,blank=True)
    ip_addresses = models.ManyToManyField(IP,null=True,blank=True)

    def __str__(self):
        return str(self.user)

#data for day by day
class DailyLocations(models.Model):
    city = models.CharField(max_length=120)
    country = models.CharField(max_length=120)
    longtitute = models.CharField(max_length=120)
    lattitute = models.CharField(max_length=120)

    def __str__(self):
        return self.country

class Counts(models.Model):
    app = models.ForeignKey(App,null=True,on_delete=models.CASCADE)
    date = models.DateField()
    user = models.IntegerField(default=0)
    desktop = models.IntegerField(default=0)
    mobile = models.IntegerField(default=0)
    locations = models.ManyToManyField(DailyLocations,null=True,blank=True)

    def __str__(self):
        return str(self.app.name)