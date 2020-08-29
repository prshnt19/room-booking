from django.contrib import admin
# from .models import FormSubmit, Booking
from .models import Room, UserProfile, FeedbackSubmit
from members.models import FormSubmit as FormSubmitmembers
from django.contrib.auth.models import User, Group
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from django.urls import reverse
from django.conf.urls import url, include
# from easy_pdf.views import PDFTemplateView
from django.conf import settings
from weasyprint import HTML, CSS
from django.template.loader import get_template
from django.template import RequestContext
from django.shortcuts import render
from django.http import HttpResponse
from django.core.mail import EmailMessage

admin.site.site_header = "MDP ADMIN PAGE";
admin.site.site_title = "ADMISTRATOR";


# class AllEntryAdmin(admin.ModelAdmin):
# 	list_display = ("id", "name", "email","arrive","depart","reference_name","reference_email")
# class AllEntryAdmin1(admin.ModelAdmin):
# 	list_display = ( "reference_name","reference_email")
class RoomEntry(admin.ModelAdmin):
    list_display = ("roomID", "room_type", "status")


# class BookingEntry(admin.ModelAdmin):
# 	list_display = ( "bookingID", "user", "roomID", "name", "arrive", "depart")
class UserProfileEntry(admin.ModelAdmin):
    list_display = ("user", "verified", "booking_mail_sent", "street", "city", "reference_email")


class FeedBackEntry(admin.ModelAdmin):
    list_display = ("name", "subject", "message")


class FormSubmitmembersInLine(admin.StackedInline):
    model = FormSubmitmembers
    can_delete = False


class UserProfileAdmin(UserAdmin):
    # inlines = [ ProfileInline,FormSubmitmembersInLine]
    ordering = ('-id',)

    # fieldsets = (
    # 		(None, {'fields': ('first_name','email', 'password')}),
    # )

    def reference_verified(self, obj):
        try:
            return obj.userprofile.reference_verified
        except UserProfile.DoesNotExist:
            return ''

    def admin_verified(self, obj):
        try:
            return obj.userprofile.director_verified
        except UserProfile.DoesNotExist:
            return ''

    def verified(self, obj):
        try:
            return obj.userprofile.verified
        except UserProfile.DoesNotExist:
            return ''

    def applied_for_member(self, obj):
        try:
            return obj.userprofile.applied_for_member
        except UserProfile.DoesNotExist:
            return ''

    def is_member(self, obj):
        try:
            return obj.userprofile.is_member
        except UserProfile.DoesNotExist:
            return ''

    # def room(self, obj):
    # 	try:
    # 		return obj.booking_set.get().roomID
    # 	except Booking.DoesNotExist:
    # 		return ''
    list_display = ('first_name', 'id', 'email', 'reference_verified', 'admin_verified', 'verified', 'account_actions',)
    list_filter = ('userprofile__is_member',)

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            url(
                r'^(?P<account_id>.+)/deposit/$',
                self.admin_site.admin_view(self.process_genrate),
                name='account-deposit',
            ),
            url(
                r'^(?P<account_id>.+)/withdraw/$',
                self.admin_site.admin_view(self.process_send),
                name='account-withdraw',
            ),
        ]
        return custom_urls + urls

    def account_actions(self, obj):
        return format_html(
            '<a class="button" href="{}">Generate Bill</a>&nbsp;'
            '<a class="button" href="{}">Send Bill</a>&nbsp;',

            reverse('admin:account-deposit', args=[obj.pk]),
            reverse('admin:account-withdraw', args=[obj.pk]),

        )

    account_actions.short_description = 'Bill'

    def process_genrate(self, request, account_id, *args, **kwargs):
        html_template = get_template('bill.html')
        a = settings.STATICFILES_DIRS
        b = ''.join(a)
        user = User.objects.get(pk=account_id)
        profile = user.userprofile
        booking = Booking.objects.get(user=user)
        rendered_html = html_template.render(({'user': user, 'profile': profile, 'booking': booking, })).encode(
            encoding="UTF-8")
        pdf_file = HTML(string=rendered_html, base_url=request.build_absolute_uri()).write_pdf(
            stylesheets=[CSS(b + '/css/bill.css')])
        response = HttpResponse(pdf_file, content_type='application/pdf')
        response['Content-Disposition'] = 'filename="home_page.pdf"'
        return response

    def process_send(self, request, account_id, *args, **kwargs):
        html_template = get_template('bill.html')
        a = settings.STATICFILES_DIRS
        b = ''.join(a)
        user = User.objects.get(pk=account_id)
        profile = user.userprofile
        booking = Booking.objects.get(user=user)
        rendered_html = html_template.render(({'user': user, 'profile': profile, 'booking': booking, })).encode(
            encoding="UTF-8")
        pdf_file = HTML(string=rendered_html, base_url=request.build_absolute_uri()).write_pdf(
            stylesheets=[CSS(b + '/css/bill.css')])
        response = HttpResponse(pdf_file, content_type='application/pdf')
        response['Content-Disposition'] = 'filename="home_page.pdf"'
        msg = EmailMessage("title", "content", to=[user.email])
        msg.attach("pdf_file.pdf", pdf_file, 'application/pdf')
        msg.content_subtype = "html"
        msg.send()

        return response


admin.site.unregister(User)
admin.site.unregister(Group)
admin.site.register(User, UserProfileAdmin)
# admin.site.register(FormSubmit,AllEntryAdmin)
admin.site.register(Room, RoomEntry)
# admin.site.register(Booking,BookingEntry)
admin.site.register(FeedbackSubmit, FeedBackEntry)
admin.site.register(UserProfile, UserProfileEntry)
