from django.contrib import admin
from forms.models import   Room
from members.models import FormSubmit,BookingTable
from django.contrib.auth.models import User, Group
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from django.urls import reverse
from django.conf.urls import url ,include
from easy_pdf.views import PDFTemplateView
from django.conf import settings
from weasyprint import HTML, CSS
from django.template.loader import get_template
from django.template import RequestContext
from django.shortcuts import render
from django.http import HttpResponse
from django.core.mail import EmailMessage
class FormSubmitAdmin(admin.ModelAdmin):
	ordering = ('-id', )
	# fieldsets = (
	# 		(None, {'fields': ('name','email','no_of_rooms','adults','childs','userbookings','reference_verified','director_verified','verified')}),
	# )
	# def reference_verified(self, obj):
	# 	try:
	# 		return obj.formsubmit.reference_verified
	# 	except FormSubmit.DoesNotExist:
	# 		return ''
	# def admin_verified(self, obj):
	# 	try:
	# 		return obj.formsubmit.director_verified
	# 	except FormSubmit.DoesNotExist:
	# 		return ''
	# def verified(self, obj):
	# 	try:
	# 		return obj.formsubmit.verified
	# 	except FormSubmit.DoesNotExist:
	# 		return ''
	# def applied_for_member(self, obj):
	# 	try:
	# 		return obj.formsubmit.applied_for_member
	# 	except FormSubmit.DoesNotExist:
	# 		return ''
	# def is_member(self, obj):
	# 	try:
	# 		return obj.formsubmit.is_member
	# 	except FormSubmit.DoesNotExist:
	# 		return ''

	# def room(self, obj):
	# 	try:
	# 		return BookingTable.objects.get(bookingID=obj).roomID
	# 	except BookingTable.DoesNotExist:
	# 		return ''

	list_display =  ('id','name','user','email','no_of_rooms','adults','childs','arrive','depart','reference_verified','director_verified','verified','account_actions',)



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
		a=settings.STATICFILES_DIRS
		b=''.join(a)
		formsubmit=FormSubmit.objects.get(pk=account_id)
		booking = BookingTable.objects.get(bookingID=formsubmit)
		room = Room.objects.get(roomID=booking.roomID)
		rendered_html = html_template.render(({'formsubmit':formsubmit,'booking':booking,'room':room,})).encode(encoding="UTF-8")
		pdf_file = HTML(string=rendered_html,base_url=request.build_absolute_uri()).write_pdf(stylesheets=[CSS(b +'/css/bill.css')])
		response = HttpResponse(pdf_file, content_type='application/pdf')
		response['Content-Disposition'] = 'filename="home_page.pdf"'
		return response

	def process_send(self, request, account_id, *args, **kwargs):
		html_template = get_template('bill.html')
		a=settings.STATICFILES_DIRS
		b=''.join(a)
		user=User.objects.get(pk=account_id)
		profile = user.formsubmit
		booking = BookingTable.objects.get(user=user)
		rendered_html = html_template.render(({'user': user,'profile':profile,'booking':booking,})).encode(encoding="UTF-8")
		pdf_file = HTML(string=rendered_html,base_url=request.build_absolute_uri()).write_pdf(stylesheets=[CSS(b +'/css/bill.css')])
		response = HttpResponse(pdf_file, content_type='application/pdf')
		response['Content-Disposition'] = 'filename="home_page.pdf"'
		msg = EmailMessage("title", "content", to=[user.email])
		msg.attach("pdf_file.pdf", pdf_file, 'application/pdf')
		msg.content_subtype = "html"
		msg.send()
		return response
#
# class FormSubmitInline(admin.StackedInline):
# 	model = FormSubmit
# 	can_delete = False
# 	fk_name = 'bookingtable'
# 	ordering = ('-id',)

class BookingTableAdmin(admin.ModelAdmin):
	# inlines=[FormSubmitInline]
	# fieldsets = (
	# 		(None, {'fields': ('roomID','name')}),
	# )
	list_display =  ('id','bookingID','name','roomID','arrive','depart')
	def name(self, obj):
		try:
			return obj.formsubmit.name
		except FormSubmit.DoesNotExist:
			return ''


admin.site.register(FormSubmit,FormSubmitAdmin)
admin.site.register(BookingTable,BookingTableAdmin)
