from django.db import models
from django.utils.timezone import now
import datetime
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.conf import settings


# class FormSubmit(models.Model):
# 	name=models.CharField(max_length=30)
# 	email=models.CharField(max_length=30)
# 	street=models.TextField(max_length=300)
# 	city=models.CharField(max_length=30)
# 	number=models.CharField(max_length=30)
# 	pincode=models.CharField(max_length=30)
# 	arrive=models.DateField()
# 	depart=models.DateField()
# 	reference_name=models.CharField(max_length=30)
# 	reference_email=models.CharField(max_length=30)
# 	room_type = models.CharField(max_length = 5)

class FeedbackSubmit(models.Model):
    """docstring for FeedbackSubmit"""
    name = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    subject = models.CharField(max_length=30)
    message = models.TextField(max_length=1000)


# class Booking(models.Model):
# 	user = models.ForeignKey(User,on_delete=models.CASCADE)
# 	bookingID = models.CharField(max_length=15)
# 	roomID = models.CharField(max_length=15)
# 	name = models.CharField(max_length=30)
# 	arrive = models.DateField()
# 	depart = models.DateField()

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    reference_verified = models.BooleanField(default=False)
    director_verified = models.BooleanField(default=False)
    verified = models.BooleanField(default=False)
    booking_mail_sent = models.BooleanField(default=False)
    street = models.TextField(max_length=300)
    city = models.CharField(max_length=30)
    number = models.CharField(max_length=30)
    pincode = models.CharField(max_length=30)
    reference_name = models.CharField(max_length=30)
    reference_email = models.CharField(max_length=30)
    is_member = models.BooleanField(default=False)
    applied_for_member = models.BooleanField(default=False)

    # room_type = models.CharField(max_length = 5)

    # other fields here

    def __str__(self):
        return "%s's profile" % self.user


def create_user_profile(sender, instance, created, **kwargs):
    if created:
        profile, created = UserProfile.objects.get_or_create(user=instance)
        # profile, created = Booking.objects.get_or_create(user=instance)


post_save.connect(create_user_profile, sender=User)


class Room(models.Model):
    roomID = models.CharField(primary_key=True, max_length=15, )
    room_type = models.CharField(max_length=5)
    status = models.CharField(max_length=15)

    def __str__(self):
        return self.roomID
