from django.urls import path
from hello import views
from .views import login_view
from hello.models import LogChemical
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views

home_list_view = views.HomeListView.as_view(
    queryset=LogChemical.objects.order_by("-log_date")[:5],
    context_object_name ="chemical_list",
    template_name = "home.html",
)

urlpatterns = [
    path("", home_list_view, name="home"),
    path("about/", views.about, name="about"),
    path("contact/", views.contact, name="contact"),
    path("log/", views.log_chemical, name="log"),
    path("delete/<int:id>/", views.delete_chemical, name='delete_message'),
    path('scanner/', views.qr_code_scanner, name='scanner'),
    path('scan/', views.qr_code_scan, name='scan'),
    path('search/', views.search_by_qr_code, name='search_by_qr_code'),
    path("admin/", admin.site.urls),
    path('accounts/login/', auth_views.LoginView.as_view(), name='login'),
]
