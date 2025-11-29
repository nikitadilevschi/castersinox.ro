from django.urls import path

from . import views
from .views import *

app_name = "core"

urlpatterns = [
    path("", views.MainView.as_view(), name="index"),
    path("catalog/<slug:category_slug>/<slug:subcategory_slug>/", views.ProductPageView.as_view(), name="catalog"),
    path("catalog/", views.ProductPageView.as_view(), name="catalog_all"),
    path('catalog/<slug:category_slug>/', views.ProductPageView.as_view(), name='catalog'),
    path('product/<slug:slug>', views.ProductDetailView.as_view(), name='product_detail'),
    path('contact/', contact_view, name='contact'),
    path('success/', SuccessView.as_view(), name='success'),
    path('policy/', PolicyView, name='policy'),

]
