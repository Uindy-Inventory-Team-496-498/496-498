from django.urls import path
from hello import views
from hello.models import LogMessage

home_list_view = views.HomeListView.as_view(
    queryset=LogMessage.objects.order_by("-log_date")[:5],
    context_object_name ="message_list",
    template_name = "hello/home.html",
)

urlpatterns = [
    path("", home_list_view, name="home"),
    path("about/", views.about, name="about"),
    path("contact/", views.contact, name="contact"),
    path("log/", views.log_message, name="log"),
    path("movies/", views.movie_list, name="movies"),
    path("hello/<name>", views.hello_there, name="hello_there"),
    path("delete/<int:message_id>/", views.delete_message, name="delete_message"),
]