from django.urls import path
from chemistry_system import views
from .views import login_view
from chemistry_system.models import currentlyInStorageTable
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views

curr_list_view = views.ChemListView.as_view(
    queryset=currentlyInStorageTable.objects.order_by("-chemBottleIDNUM"),
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
    path('search_by_qr/', views.search_by_qr, name='search_by_qr'),
    path('checkinandout/', views.checkinandout, name='checkinandout'),
    path('currchemicals/', views.currchemicals, name='currchemicals'),
    path('live-search-api/', views.live_search_api, name='live_search_api'),

    path('current_chemicals/', views.list_chemicals, {'model_name': 'currentlyinstoragetable'}, name='current_chemicals'),
    path('add_chemical/<str:model_name>/', views.add_chemical, name='add_chemical'),
    path('edit_chemical/<str:model_name>/<int:pk>/', views.edit_chemical, name='edit_chemical'),
    path('delete_chemical/<str:model_name>/<int:pk>/', views.delete_chemical, name='delete_chemical'),
    path('scanner_add/', views.scanner_add, name='scanner_add'),
    path('add/<str:model_name>/', views.add_chemical, name='add_chemical'),
    path('export_chemicals_csv/', views.export_chemicals_csv, name='export_chemicals_csv'),
    path('import_chemicals_csv/', views.import_chemicals_csv, name='import_chemicals_csv'),
    path('update-checkout-status/<str:model_name>/<str:qrcode_value>/', views.update_checkout_status, name='update_checkout_status'),
    path('delete_all_chemicals/', views.delete_all_chemicals, name='delete_all_chemicals'),
]
