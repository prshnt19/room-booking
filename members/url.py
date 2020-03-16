from django.conf.urls import url ,include
from django.urls import path
from members import view


urlpatterns = [
     url(r'^$', view.loginregisterpage, name='login_member'),
     path('register/',view.register,name='register'),
     path('login/',view.loginuser,name='login'),
     path('profile/',view.profile,name='profile'),
     path('bookings/',view.bookings,name='bookings'),
     path('bookings/details/',view.bookingdetails,name='bookingdetails'),
     path('logout/',view.logoutuser,name="logout"),
     path('roombooking/', view.roombook, name='roombook'),
     path('roombooking/formsubmit/', view.submit, name='submit'),
     url(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/$',
        view.activate, name='activate'),
     url(r'^activatedirector/(?P<uidb64>[0-9A-Za-z_\-]+)/$',
           view.director_activate, name='activatedirector'),

     url(r'^activatemembers/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
           view.member_activate, name='activatemembers'), 
     path('changepassword/', view.changepassword, name='changepassword'),      
     path('changepassword/changepasswordsubmit/', view.changepasswordsubmit, name='changepasswordsubmit'),
     path('forgotpassworduser/forgotpassword/', view.forgotpassword, name='forgotpassword'),
     path('forgotpassworduser/', view.forgotpassworduser, name='forgotpassworduser'),
     url(r'^forgotpasswordsubmit/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
           view.forgotpasswordsubmit, name='forgotpasswordsubmit'), 

    # path('register/',views.register,name='register'),

]
