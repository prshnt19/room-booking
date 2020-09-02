from django.shortcuts import render
from .models import Room, UserProfile, FeedbackSubmit
from members.models import BookingTable
from django.contrib.auth.models import User
from django.core.mail import EmailMessage
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from .tokens import account_activation_token
from django.http import HttpResponse
from dateutil import parser
from random import randint
from forms.task import send_verification_email
from easy_pdf.views import PDFTemplateView
from django.conf import settings
from weasyprint import HTML, CSS
from django.template.loader import get_template
from django.template import RequestContext
import json
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required


def form_view(request):
    return render(request, 'room/book_a_room.html')


def vipform(request):
    return render(request, 'room/vip_form.html')


def lat_ajax(request):
    if request.method == 'POST' and request.is_ajax():
        name = request.POST.get('name')
        arrive = parser.parse(request.POST["arrive"]).date()
        depart = parser.parse(request.POST["depart"]).date()
        room_type = request.POST.get('room_type')
        no_of_rooms = request.POST.get("no_of_rooms")
        norooms = int(no_of_rooms)

        found = 0
        ru = []
        for i in range(norooms):
            for r in Room.objects.raw('SELECT * FROM forms_room WHERE status = "a" and room_type = %s', [room_type]):
                f = 1
                rID = r.roomID
                for b in BookingTable.objects.raw('SELECT * FROM members_bookingtable WHERE roomID_id = %s', [rID]):

                    if (b.arrive > depart or b.depart < arrive):
                        pass
                    else:

                        f = 0
                if f == 1:
                    r.status = 'u'
                    r.save()
                    ru.append(r)
                    # User.objects.get(id = user.id).booking_set.add(booking)
                    found += 1
                    break
                if found == norooms:
                    break

        for r in ru:
            r.status = 'a'
            r.save()
        data = {'found': found, 'norooms': norooms, 'arrive': arrive}
        return JsonResponse(data)


@login_required
def feedback_submit(request):
    user = request.user
    subject = request.POST["subject"]
    message = request.POST["message"]
    feedbacksubmit = FeedbackSubmit(name=user, subject=subject, message=message)
    feedbacksubmit.save()
    return render(request, "room/feedbacksubmitted.html")


def feedback_form(request):
    return render(request, "room/feedbackform.html")


def form_submit(request):
    name = request.POST["name"]
    email = request.POST["email"]
    number = request.POST["phone"]
    street = request.POST["street"]
    city = request.POST["city"]
    pincode = request.POST["post-code"]
    arrive = parser.parse(request.POST["arrive"]).date()
    depart = parser.parse(request.POST["depart"]).date()
    room_type = request.POST["room_type"]
    reference_name = request.POST["reference_name"]
    reference_email = request.POST["reference_email"]
    formsubmit = FormSubmit(name=name, email=email, number=number, street=street, city=city, pincode=pincode,
            arrive=arrive, depart=depart, reference_email=reference_email,
            reference_name=reference_name)
    formsubmit.save()

    user = User.objects.create_user(username=name + str(randint(0, 999)), email=email, password='arpitarpit',
            first_name=name)
    # user = User.objects.create_user(username=name,email=email,password='arpitarpit',first_name=name)
    found = 0
    for r in Room.objects.raw('SELECT * FROM forms_room WHERE status = "a" and room_type = %s', [room_type]):
        f = 1
        rID = r.roomID
        for b in Booking.objects.raw('SELECT * FROM members_bookingtable WHERE roomID_id = %s', [rID]):
            if (b.arrive > depart or b.depart < arrive):
                pass
            else:
                f = 0
        if f == 1:
            booking = Booking.objects.get(user=user)
            booking.bookingID = formsubmit.id
            booking.roomID_id = rID
            booking.name = name
            booking.arrive = arrive
            booking.depart = depart
            booking.save()
            # User.objects.get(id = user.id).booking_set.add(booking)
            found = 1
            break
        if found == 1:
            break
    if found == 0:
        return HttpResponse('Sorry no rooms available for requested dates')
    # room not available

    profile = user.userprofile
    profile.street = street
    profile.city = city
    profile.pincode = pincode
    profile.number = number
    profile.reference_name = reference_name
    profile.reference_email = reference_email
    profile.save()
    user.save()
    send_verification_email.delay(user.username)
    return render(request, "room/formsubmitted.html")


def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        profile = user.userprofile
        profile.reference_verified = True
        if profile.director_verified:
            profile.verified = True
            if not profile.booking_mail_sent:
                mail_subject = 'IIITM guest house'
                message = render_to_string('booking_mail.html', {'user': user,
                    'domain': '127.0.0.1:8000/director/cancel',
                    'uid': urlsafe_base64_encode(
                        force_bytes(user.pk)).decode(),
                    'token': account_activation_token.make_token(user),
                    'arrive': profile.arrive,
                    'depart': profile.depart
                    , })
                to_email = user.email
                profile.booking_mail_sent = True
                email = EmailMessage(mail_subject, message, to=[to_email])
                email.send()

        profile.save()
        return HttpResponse('Thank you for your confirmation')
    else:
        return HttpResponse('link is invalid! or You have already confirmed!!')


def director_activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        profile = user.userprofile
        booking = Booking.objects.get(user=user)
        profile.director_verified = True
        if profile.reference_verified:
            profile.verified = True
            if not profile.booking_mail_sent:
                mail_subject = 'IIITM guest house'
                message = render_to_string('booking_mail.html', {'user': user,
                    'arrive': profile.arrive,
                    'uid': urlsafe_base64_encode(
                        force_bytes(user.pk)).decode(),
                    'token': account_activation_token.make_token(user),
                    'depart': profile.depart,
                    'roomID': booking.roomID_id,
                    'domain': '127.0.0.1:8000/director/cancel'
                    , })
                to_email = user.email
                profile.booking_mail_sent = True
                email = EmailMessage(mail_subject, message, to=[to_email])
                email.send()

        profile.save()
        return HttpResponse('Thank you for your confirmation')
    else:
        return HttpResponse('link is invalid! or You have already confirmed!!')


def cancel_booking(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        try:
            booking = Booking.objects.get(user=user)

        except Booking.DoesNotExist:
            booking = None
        if booking is not None:
            booking.delete()
            return HttpResponse('cancelled')
        if booking is None:
            return HttpResponse('already cancelled')
