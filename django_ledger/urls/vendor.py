from django.http import HttpResponseRedirect
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django_ledger import views

def redirect_to_mapping(request):
    return HttpResponseRedirect('/vendor/mapping/')  # Updated URL

app_name = 'vendor'  # Specify the app namespace

urlpatterns = [
    path('<slug:entity_slug>/list/', views.VendorModelListView.as_view(), name='vendor-list'),
    path('ImportCSV/', views.ImportCSV.as_view(), name='ImportCSV'),
    path('<slug:entity_slug>/create/', views.VendorModelCreateView.as_view(), name='vendor-create'),
    path('<slug:entity_slug>/update/<uuid:vendor_pk>/', views.VendorModelUpdateView.as_view(), name='vendor-update'),
    path('<slug:entity_slug>/delete/<uuid:vendor_pk>/', views.VendorModelDeleteView.as_view(), name='vendor-delete'),
    path('upload/', views.upload, name='upload'),
    path('redirect-to-mapping/', redirect_to_mapping, name='redirect-to-mapping'),  # Update the name
    path('mapping/', views.mapping, name='mapping'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
