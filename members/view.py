from django.shortcuts import render,redirect
from django.http import HttpResponse,HttpResponseRedirect
from django.contrib.auth.models import User
from .models import FormSubmit, BookingTable
from django.core.mail import EmailMessage
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from forms.tokens import account_activation_token
from members.token import forgot_password_token
from django.template.loader import render_to_string
from django.contrib.auth import authenticate, login ,logout
from forms.models import  Room, UserProfile
from django.contrib.auth.decorators import login_required
from dateutil import parser
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from forms.task import send_verification_email
from django import template
register = template.Library()
@register.filter
def add(value_1, value_2):
    return str(value_1) + str(value_2)

@login_required
def profile(request):
	user=request.user
	formsubmits=(FormSubmit.objects.filter(userbookings=user))
	return render(request, 'room/index.html',{'user':user,'formsubmits':formsubmits})

@login_required
def bookings(request):
	user=request.user
	bookings=(BookingTable.objects.filter(user=user))
	return render(request, 'bookings.html',{'user':user,'bookings':bookings})

@login_required
def roombook(request):
	return render(request,'room/book_a_room.html')
@login_required
def changepassword(request):
	return render(request,'room/changepassword.html')
@login_required
def changepasswordsubmit(request):
	user=request.user
	newpassword=request.POST["newpassword"]
	renewpassword=request.POST["renewpassword"]
	user.set_password(newpassword)
	user.save()
	return render(request,'room/index.html')
def forgotpassworduser(request):
	return render(request,'forgotpassword.html')
def forgotpassword(request):

	username = request.POST.get('username')
	user = User.objects.get(username=username)

	
		
	# if user is not  None and profile.is_member is True :
	if user is not None:
			mail_subject = 'IIITM guest house'
			message=render_to_string('forgotpassword_mail.html',{'user': user,
					'domain': '127.0.0.1:8000',
					'uid': urlsafe_base64_encode(force_bytes(user.pk)).decode(),
					'token': forgot_password_token.make_token(user),})
			email=EmailMessage(mail_subject,message,to=[user.email])
			email.send()
			return HttpResponse('Check Your Email')
		
	else:
		return HttpResponse('Sorry you are not a member')
def forgotpasswordsubmit(request, uidb64, token):
	try:
		uid = force_text(urlsafe_base64_decode(uidb64))
		user = User.objects.get(pk=uid)
	except(TypeError, ValueError, OverflowError, User.DoesNotExist):
		user = None
	if user is not None and forgot_password_token.check_token(user, token):
		login(request,user)

		return redirect('/membership/changepassword/')
	else:
		return HttpResponse('link is invalid! or You have already confirmed!!')

@login_required
def submit(request):
	user=request.user
	name = request.POST["name"]
	email = request.POST["email"]
	age = request.POST["age"]
	street = request.POST["street"]
	city = request.POST["city"]
	number = request.POST["phone"]
	pincode = request.POST["post-code"]
	arrive = parser.parse(request.POST["arrive"]).date()
	depart = parser.parse(request.POST["depart"]).date()
	reference_name = request.POST["reference_name"]
	reference_email = request.POST["reference_email"]
	reference_designation = request.POST["reference_designation"]
	room_type = request.POST["room_type"]
	no_of_rooms = request.POST["no_of_rooms"]
	adults = request.POST["adults"]
	childs = request.POST["childs"]
	formsubmit = FormSubmit(user=user,name=name, email=email, age=age, number=number, street=street, city=city,
							pincode=pincode, arrive=arrive, depart=depart, reference_email=reference_email,
							reference_name=reference_name, reference_designation=reference_designation,
							room_type=room_type, no_of_rooms=no_of_rooms, adults=adults, childs=childs)
	formsubmit.save()

	found = 0
	norooms = int(no_of_rooms)
	for i in range(norooms):

		for r in Room.objects.raw('SELECT * FROM forms_room WHERE status = "a" and room_type = %s', [room_type]):
			f = 1
			rID = r.roomID
			for b in BookingTable.objects.raw('SELECT * FROM members_bookingtable WHERE roomID_id = %s', [rID]):

				if(b.arrive > depart or b.depart < arrive):
					pass
				else:

					f=0
			if f == 1:
				booking = BookingTable.objects.create(user=user, roomID_id=r, bookingID=formsubmit, arrive=arrive, name=name, depart=depart)
				booking.save()
				#User.objects.get(id = user.id).booking_set.add(booking)
				found += 1
				break
			if found == norooms:
					break
	if found == 0:
		return HttpResponse('Sorry! no rooms available for requested dates')
	elif found < norooms:
		return HttpResponse('Only ' + str(found) + ' rooms available for requested dates!')
	send_verification_email.delay(formsubmit.id)
		#room not available

	return HttpResponseRedirect('/')

def loginregisterpage(request):
	if request.user.is_authenticated :
		return HttpResponseRedirect('/')
	else:
		return render(request,'login_members.html')
def loginuser(request):

	username = request.POST.get('username')
	password = request.POST.get('password')
	user = authenticate(request, username=username, password=password)
	# if user is not  None and profile.is_member is True :
	if user is not None:
		login( request , user)
		return redirect('/')
	else:
		return HttpResponse('Sorry you are not a member')
		# Return an 'invalid login' error message.
@login_required
def logoutuser(request):
	logout(request)
	return redirect('/membership')

@login_required
def bookingdetails(request):
		return render(request, 'booking_details.html')

def register(request):
	name=request.POST["name"]
	email=request.POST["email"]
	number=request.POST["number"]
	street=request.POST["street"]
	city=request.POST["city"]
	pincode=request.POST["post-code"]
	reference_name=request.POST["reference_name"]
	reference_email=request.POST["reference_email"]
	username=request.POST["username"]
	password=request.POST["password"]
	repass=request.POST["repassword"]

	if User.objects.filter(username=username).exists():
		return HttpResponse('Username not available')

	user = User.objects.create_user(username=username,email=email,password=password,first_name=name)
	profile = user.userprofile
	profile.street=street
	profile.city=city
	profile.pincode=pincode
	profile.number=number
	profile.reference_name=reference_name
	profile.reference_email=reference_email
	profile.applied_for_member=True
	profile.save()
	user.save()
	mail_subject = 'IIITM guest house'
	message=render_to_string('membership_apply.html',{'user': user,
					'reference_name' : reference_name ,
					'domain': '127.0.0.1:8000',
					'uid': urlsafe_base64_encode(force_bytes(user.pk)).decode(),
					'token': account_activation_token.make_token(user),})
	email=EmailMessage(mail_subject,message,to=['imarpit02@gmail.com'])
	email.send()

	return  HttpResponse('Thank you for applying ')
def member_activate(request, uidb64, token):
	try:
		uid = force_text(urlsafe_base64_decode(uidb64))
		user = User.objects.get(pk=uid)
	except(TypeError, ValueError, OverflowError, User.DoesNotExist):
		user = None
	if user is not None and account_activation_token.check_token(user, token):
		profile = user.userprofile
		profile.is_member = True

		profile.save()
		return HttpResponse('Thank you for your confirmation')
	else:
		return HttpResponse('link is invalid! or You have already confirmed!!')
def activate(request, uidb64):
	try:
		uid = force_text(urlsafe_base64_decode(uidb64))
		formsubmit = FormSubmit.objects.get(pk=uid)
	except(TypeError, ValueError, OverflowError, FormSubmit.DoesNotExist):
		formsubmit = None
	if formsubmit is not None :
		formsubmit.reference_verified = True
		if formsubmit.director_verified:
			formsubmit.verified = True
			if not formsubmit.booking_mail_sent:
				mail_subject = 'IIITM guest house'
				message=render_to_string('booking_mail.html',{'user': formsubmit,
				'domain': '127.0.0.1:8000/membership/',
				'uid': urlsafe_base64_encode(force_bytes(formsubmit.pk)).decode(),
				# 'token': account_activation_token.make_token(user),
				'arrive': formsubmit.arrive,
				'depart' : formsubmit.depart
				,})
				to_email=formsubmit.email
				formsubmit.booking_mail_sent= True
				email=EmailMessage(mail_subject,message,to=[to_email])
				email.send()

		formsubmit.save()
		return HttpResponse('Thank you for your confirmation')
	else:
		return HttpResponse('link is invalid! or You have already confirmed!!')
def director_activate(request, uidb64):
	try:
		uid = force_text(urlsafe_base64_decode(uidb64))
		formsubmit = FormSubmit.objects.get(pk=uid)
	except(TypeError, ValueError, OverflowError, FormSubmit.DoesNotExist):
		formsubmit = None
	if formsubmit is not None :
		formsubmit.director_verified = True
		if formsubmit.reference_verified:
			formsubmit.verified = True
			if not formsubmit.booking_mail_sent:
				mail_subject = 'IIITM guest house'
				message=render_to_string('booking_mail.html',{'user': formsubmit,
				'arrive': formsubmit.arrive,
				'uid': urlsafe_base64_encode(force_bytes(formsubmit.pk)).decode(),
				# 'token': account_activation_token.make_token(user),
				'depart' : formsubmit.depart,
				# 'roomID' : booking.roomID_id,
				'domain': '127.0.0.1:8000/director/cancel'
				,})
				to_email=formsubmit.email
				formsubmit.booking_mail_sent= True
				email=EmailMessage(mail_subject,message,to=[to_email])
				email.send()

		formsubmit.save()
		return HttpResponse('Thank you for your confirmation')
	else:
		return HttpResponse('link is invalid! or You have already confirmed!!')
