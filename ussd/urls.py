from django.urls import path
from .views import ussd_callback, sms_reply_handler

urlpatterns = [
    path('ussd/', ussd_callback, name='ussd_callback'),
    path('sms/', sms_reply_handler, name='sms_reply_handler'),
]
