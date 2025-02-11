from django.urls import path
from hello import views
from .views import login_view
from hello.models import currentlyInStorageTable
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views

curr_list_view = views.ChemListView.as_view(
	#removed the [:5] at the end of the following line to display entire database
    queryset=currentlyInStorageTable.objects.order_by("-chemBottleIDNUM"),
    context_object_name ="chemical_list_db",
    template_name = "currchemicals.html",
)

urlpatterns = [
    path("home/", views.home, name="home"),
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
    path("", views.home, name="home"),
    path('scan/', views.qr_code_scan, name='scan'),
    path("search/", views.search_page, name="search"),


    path("search_by_qr/", views.search_by_qr, name="search_by_qr"),
    
    path("admin/", admin.site.urls),
    path('scanner_delete/', views.scanner_delete, name='scanner_delete'),
    
    #Main's Version of search by qr, update mine to use this one
    #path('search_by_qr/', views.search_by_qr, name='search_by_qr'),
    
    path('checkinandout/', views.checkinandout, name='checkinandout'),
    path('currchemicals/', curr_list_view, name='currchemicals'),
    path('current_chemicals/', views.list_chemicals, {'model_name': 'currentlyinstoragetable'}, name='current_chemicals'),
    #path('all_chemicals/', views.list_chemicals, {'model_name': 'allchemicalstable'}, name='all_chemicals'),
    path('add_chemical/<str:model_name>/', views.add_chemical, name='add_chemical'),
    path('edit_chemical/<str:model_name>/<int:pk>/', views.edit_chemical, name='edit_chemical'),
    #main's version of delete_chemical, change to use mine?
    path('delete_chemical/<str:model_name>/<int:pk>/', views.delete_chemical, name='delete_chemical'),
    path('scanner_add/', views.scanner_add, name='scanner_add'),
    path('add/<str:model_name>/', views.add_chemical, name='add_chemical'),
    path('update-checkout-status/<str:model_name>/<str:qrcode_value>/', views.update_checkout_status, name='update_checkout_status'),

]
