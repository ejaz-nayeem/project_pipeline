
from django.contrib import admin

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/ip-solution/', include('ip_solution.urls')),
    path('api/phone-solution/', include('phone_solution.urls')),
    path('api/email-solution/', include('email_solution.urls')),
    path('api/ip_generate_with_one_click/', include('ip_generate_with_one_click.urls')),
    path('api/mail_generate_with_one_click/', include('mail_generate_with_one_click.urls')),
    path('api/phone_generate_with_one_click/', include('phone_generate_with_one_click.urls')),
]


