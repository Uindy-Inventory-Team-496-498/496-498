from django.urls import path
from hello import views
from .views import login_view
from hello.models import currentlyInStorageTable
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views

curr_list_view = views.ChemListView.as_view(
    queryset=currentlyInStorageTable.objects.order_by("-chemBottleIDNUM")[:5],
    context_object_name ="chemical_list_db",
    template_name = "currchemicals.html",
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("accounts.urls")),  
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/login/', auth_views.LoginView.as_view(), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),

    path("", views.home, name="home"),
    path('scan/', views.qr_code_scan, name='scan'),
    path("search/", views.search_page, name="search"),
    path('currchemicals/', curr_list_view, name='current_chemicals'),
	path('edit/<int:id>/', views.edit_chemical, name='edit_chemical'), 
]
