from django.urls import path
from hello import views
from hello.models import LogChemical

home_list_view = views.HomeListView.as_view(
    queryset=LogChemical.objects.order_by("-log_date")[:5],
    context_object_name ="chemical_list",
    template_name = "hello/home.html",
)

urlpatterns = [
    path("", home_list_view, name="home"),
    path("about/", views.about, name="about"),
    path("contact/", views.contact, name="contact"),
    path("log/", views.log_message, name="log"),
    path("delete/<int:id>/", views.delete_message, name='delete_message'),
    path("login/", views.login, name="login"),
    path('scanner/', views.qr_code_scanner, name='scanner'),
]