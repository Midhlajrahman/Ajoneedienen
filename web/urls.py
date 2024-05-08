from django.urls import path

from . import views

app_name = "web"

urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    path("catalogue/<str:pk>/", views.RestaurantCatalogueView.as_view(), name="restaurant_catalogue"),
    path("catalogue/<str:pk>/products/", views.RestaurantProductsView.as_view(), name="restaurant_products"),
    path("category/<str:pk>/", views.CategoryView.as_view(), name="category_catalogue"),
    path("checkout/<str:pk>/", views.CheckoutView.as_view(), name="checkout"),
    path("view/catalogue/<str:slug>/", views.RestaurantCatalogueSlugView.as_view(), name="restaurant_slug_catalogue"),
    path("cart_item/plus/", views.CartItemPlusView.as_view(), name="cart_item_plus"),
    path("cart_item/minus/", views.CartItemMinusView.as_view(), name="cart_item_minus"),
]
