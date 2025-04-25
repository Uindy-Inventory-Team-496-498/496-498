from chemistry_system import views
from django.conf import settings
from .views import ChemicalAutocomplete, admin_dashboard
from chemistry_system.models import individualChemicals, allChemicals
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from chemistry_system.utils import export_chemicals_csv, import_chemicals_csv, update_checkout_status  # Import the new views

curr_list_view = views.ChemListView.as_view(
    queryset=individualChemicals.objects.order_by("-chemBottleIDNUM"),
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
    path("<str:value>", views.home, name="home"),

    path('scan/', views.qr_code_scan, name='scan'),
    path("search/", views.search_page, name="search"),
    path('live-search-api/', views.live_search_api, name='live_search_api'),
    path('checkinandout/', views.checkinandout, name='checkinandout'),
    
    path('current_chemicals/', views.list_chemicals, {'model_name': 'individualChemicals'}, name='current_chemicals'),
    path('add_chemical/<str:model_name>/', views.add_chemical, name='add_chemical'),
    path('edit_chemical/<str:model_name>/<int:pk>/', views.edit_chemical, name='edit_chemical'),
    path('delete_chemical/<str:model_name>/<int:pk>/', views.delete_chemical, name='delete_chemical'),
    path('scanner_add/<str:model_name>/', views.scanner_add, name='scanner_add'),
    path('add/<str:model_name>/', views.add_chemical, name='add_chemical'),
    path('export_chemicals_csv/', export_chemicals_csv, name='export_chemicals_csv'),  
    path('import_chemicals_csv/', import_chemicals_csv, name='import_chemicals_csv'),  
    path('update-checkout-status/<str:model_name>/<str:qrcode_value>/', update_checkout_status, name='update_checkout_status'),  
    path('delete_all_chemicals/', views.delete_all_chemicals, name='delete_all_chemicals'),
    path('print/', views.print_page, name='print_page'),
    path('download-qr-pdf/', views.generate_qr_pdf_view, name='download_qr_pdf'), 
    path('log/', views.log, name='log'),
    path('run-populate-storage/', views.run_populate_storage, name='run_populate_storage'),  
    path('chemical-autocomplete/', ChemicalAutocomplete.as_view(), name='chemical-autocomplete'),
    path('update-chemical-amount/', views.update_chemical_amount, name='update_chemical_amount'),
    path('get-chemical-details/<str:qrcode_value>/', views.get_chemical_details, name='get_chemical_details'),

    path("chem_display/<str:table_name>/", views.chem_display, name="chem_display"),
    path('force-update-total-amount/', views.force_update_total_amount, name='force_update_total_amount'),
    
    path("admin_dashboard/", admin_dashboard, name='admin_dashboard'),

]

if settings.DJANGO_ENV == 'development':
    urlpatterns += [path("__reload__/", include("django_browser_reload.urls"))]
