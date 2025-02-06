from django.urls import path
from hello import views
from .views import login_view
from hello.models import LogChemical, currentlyInStorageTable
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views


home_list_view = views.HomeListView.as_view(
    queryset=LogChemical.objects.order_by("-log_date")[:5],
    context_object_name="chemical_list",
    template_name="home.html",
)

curr_list_view = views.ChemListView.as_view(
	#removed the [:5] at the end of the following line to display entire database
    queryset=currentlyInStorageTable.objects.order_by("-chemBottleIDNUM"),
    context_object_name ="chemical_list_db",
    template_name = "currchemicals.html",
)


urlpatterns = [
    path("", home_list_view, name="home"),
    path("about/", views.about, name="about"),
    path("contact/", views.contact, name="contact"),
    path("log/", views.log_chemical, name="log"),
    path("delete/<int:chemBottleIDNUM>/", views.delete_chemical, name='delete_chemical'),
    path('scan/', views.qr_code_scan, name='scan'),
    path("admin/", admin.site.urls),
    path("accounts/", include("accounts.urls")),  
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/login/', auth_views.LoginView.as_view(), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('scan/', views.qr_code_scan, name='scan'),
    path("search/", views.search_page, name="search"),
    path("search_by_qr_code/", views.search_by_qr_code, name="search_by_qr_code"),
    path('currchemicals/', curr_list_view, name='current_chemicals'),
    path("admin/", admin.site.urls),
    path('accounts/login/', auth_views.LoginView.as_view(), name='login'),
	path('edit/<int:id>/', views.edit_chemical, name='edit_chemical'), 
    path('scanner_delete/', views.scanner_delete, name='scanner_delete'),
    
]
