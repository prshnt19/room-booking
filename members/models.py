from django.db import models
from forms.models import Room
# Create your models here.
from django.contrib.auth.models import User


class FormSubmit(models.Model):
	user=models.ForeignKey(User, on_delete=models.CASCADE)
	name = models.CharField(max_length=30)
	email = models.CharField(max_length=30)
	age = models.IntegerField()
	street = models.TextField(max_length=300)
	city = models.CharField(max_length=30)
	number = models.CharField(max_length=30)
	pincode = models.CharField(max_length=30)
	arrive = models.DateField()
	depart = models.DateField()
	reference_name = models.CharField(max_length=30)
	reference_email = models.CharField(max_length=30)
	reference_designation = models.CharField(max_length=30)
	room_type = models.CharField(max_length=5)
	no_of_rooms = models.IntegerField()
	adults = models.IntegerField()
	childs = models.IntegerField()
	reference_verified=models.BooleanField(default=False)
	director_verified=models.BooleanField(default=False)
	verified=models.BooleanField(default=False)
	booking_mail_sent=models.BooleanField(default=False)
	admin_verified=models.BooleanField(default=False)

	def room(self):
		return self.bookingtable.roomID

	def __str__(self):
		return str(self.id)


class BookingTable(models.Model):
	user=models.ForeignKey(User, on_delete=models.CASCADE)
	bookingID = models.ForeignKey(FormSubmit, on_delete=models.CASCADE)
	roomID = models.ForeignKey(Room,on_delete=models.CASCADE)
	name = models.CharField(max_length=30)
	arrive = models.DateField()
	depart = models.DateField()

	def __str__(self):
		return str(self.bookingID.id)