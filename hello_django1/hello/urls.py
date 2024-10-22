from django.urls import path
from hello import views
from .views import login_view
from hello.models import LogMessage
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views

home_list_view = views.HomeListView.as_view(
    queryset=LogMessage.objects.order_by("-log_date")[:5],
    context_object_name ="message_list",
    template_name = "home.html",
)

urlpatterns = [
    path("", home_list_view, name="home"),
    path("about/", views.about, name="about"),
    path("contact/", views.contact, name="contact"),
    path("log/", views.log_message, name="log"),
    path("delete/<int:id>/", views.delete_message, name='delete_message'),
    path('scanner/', views.qr_code_scanner, name='scanner'),
    path("admin/", admin.site.urls),
    path('accounts/login/', auth_views.LoginView.as_view(), name='login'),
]