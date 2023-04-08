from django.urls import path
from django_ledger import views

urlpatterns = [
    path('<slug:entity_slug>/list/', views.CustomerModelListView.as_view(), name='customer-list'),
    path('ImportCSV_Customer/', views.ImportCSV_Customer.as_view(), name='ImportCSV_Customer'),
    path('<slug:entity_slug>/create/', views.CustomerModelCreateView.as_view(), name='customer-create'),
    path('<slug:entity_slug>/update/<uuid:customer_pk>/',
         views.CustomerModelUpdateView.as_view(),
         name='customer-update'),
    path('<slug:entity_slug>/delete/<uuid:customer_pk>/',
            views.CustomerModelDeleteView.as_view(),
            name='customer-delete'),
]
