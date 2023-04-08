from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django_ledger import views

urlpatterns = [
    path('<slug:entity_slug>/list/', views.VendorModelListView.as_view(), name='vendor-list'),
    path('ImportCSV/', views.ImportCSV.as_view(), name='ImportCSV'),
    path('<slug:entity_slug>/create/', views.VendorModelCreateView.as_view(), name='vendor-create'),
    path('<slug:entity_slug>/update/<uuid:vendor_pk>/', views.VendorModelUpdateView.as_view(), name='vendor-update'),
    path('<slug:entity_slug>/delete/<uuid:vendor_pk>/', views.VendorModelDeleteView.as_view(), name='vendor-delete'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)