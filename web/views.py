from django.http import JsonResponse
from django.shortcuts import render
from django.utils import timezone
from django.views import View
from django.views.generic import DetailView, ListView
from main.models import (
    Badge,
    Banner,
    CartItem,
    CatalogueAd,
    Category,
    CheckoutAd,
    Notification,
    Product,
    ProductAd,
    Restaurant,
)


class IndexView(ListView):
    model = Badge
    template_name = "web/index.html"
    context_object_name = "badges"
    paginate_by = 50


class RestaurantCatalogueView(DetailView):
    model = Restaurant
    template_name = "web/catalogue.html"
    context_object_name = "restaurant"

    def get_context_data(self, **kwargs):
        restaurant = self.get_object()
        if restaurant.visitor_count is None:
            restaurant.visitor_count = 0

        # Increment visitor count
        restaurant.visitor_count += 1
        restaurant.save()

        context = super().get_context_data(**kwargs)
        context["banners"] = Banner.objects.filter(restaurant=self.get_object())
        context["notifications"] = Notification.objects.filter(restaurant=self.get_object())
        context["product_ads"] = ProductAd.objects.filter(display_upto__gte=timezone.now(), display_in__in=[restaurant])
        return context


class RestaurantCatalogueSlugView(DetailView):
    model = Restaurant
    template_name = "web/catalogue.html"
    context_object_name = "restaurant"

    def get_context_data(self, **kwargs):
        restaurant = self.get_object()
        if restaurant.visitor_count is None:
            restaurant.visitor_count = 0

        # Increment visitor count
        restaurant.visitor_count += 1
        restaurant.save()

        context = super().get_context_data(**kwargs)
        context["banners"] = Banner.objects.filter(restaurant=self.get_object())
        context["notifications"] = Notification.objects.filter(restaurant=self.get_object())
        context["product_ads"] = ProductAd.objects.filter(display_upto__gte=timezone.now(), display_in__in=[restaurant])
        return context


class RestaurantProductsView(ListView):
    model = Product
    template_name = "web/products.html"

    def get_context_data(self, **kwargs):
        restaurant = self.get_object()
        context = super().get_context_data(**kwargs)
        context["restaurant"] = restaurant
        context["banners"] = Banner.objects.filter(restaurant=self.get_object())
        context["notifications"] = Notification.objects.filter(restaurant=self.get_object())
        context["product_ads"] = ProductAd.objects.filter(display_upto__gte=timezone.now(), display_in__in=[restaurant])
        return context

    def get_object(self):
        return Restaurant.objects.get(pk=self.kwargs["pk"])

    def get_queryset(self):
        request = self.request
        products = Product.objects.filter(subcategory__category__restaurant=self.get_object())
        if request.GET.get("q"):
            query = request.GET.get("q")
            print(query)
            products = products.filter(name__icontains=query) | products.filter(description__icontains=query)
        return products


class CategoryView(DetailView):
    model = Category
    template_name = "web/category.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        restaurant = self.get_object().restaurant
        session_key = self.request.session.session_key
        cart_items = CartItem.objects.filter(restaurant=restaurant, session_key=session_key)
        context["cart_items"] = cart_items
        context["total_price"] = sum([cart_item.total_price() for cart_item in cart_items])
        context["restaurant"] = restaurant
        context["banners"] = Banner.objects.filter(restaurant=restaurant)
        context["catalogue_ads"] = CatalogueAd.objects.filter(
            display_upto__gte=timezone.now(), display_in__in=[restaurant]
        )
        context["product_ads"] = ProductAd.objects.filter(display_upto__gte=timezone.now(), display_in__in=[restaurant])
        return context


class CheckoutView(DetailView):
    model = Restaurant
    template_name = "web/checkout.html"
    context_object_name = "restaurant"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        restaurant = self.get_object()
        if restaurant.visitor_count is None:
            restaurant.visitor_count = 0

        # Increment visitor count
        restaurant.visitor_count += 1
        restaurant.save()

        session_key = self.request.session.session_key
        cart_items = CartItem.objects.filter(restaurant=restaurant, session_key=session_key)
        context["banners"] = Banner.objects.filter(restaurant=restaurant)
        context["restaurant"] = restaurant
        context["cart_items"] = cart_items
        context["total_price"] = sum([cart_item.total_price() for cart_item in cart_items])
        context["checkout_ads"] = CheckoutAd.objects.filter(
            display_upto__gte=timezone.now(), display_in__in=[restaurant]
        )
        context["product_ads"] = ProductAd.objects.filter(display_upto__gte=timezone.now(), display_in__in=[restaurant])
        return context


class CartItemPlusView(View):
    def get(self, request):
        option_pk = request.GET.get("option")
        restaurant_pk = request.GET.get("restaurant_pk")
        session_key = request.GET.get("session_key")
        cart_item = CartItem.objects.get_or_create(
            product_id=option_pk, restaurant_id=restaurant_pk, session_key=session_key
        )[0]
        cart_item.quantity += 1
        cart_item.save()
        response = {"success": True, "quantity": cart_item.quantity, "subtotal": cart_item.total_price()}
        return JsonResponse(response)


class CartItemMinusView(View):
    def get(self, request):
        option_pk = request.GET.get("option")
        restaurant_pk = request.GET.get("restaurant_pk")
        session_key = request.GET.get("session_key")
        cart_item = CartItem.objects.get_or_create(
            product_id=option_pk, restaurant_id=restaurant_pk, session_key=session_key
        )[0]
        print(cart_item.quantity, "*" * 20)
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
            response = {"success": True, "quantity": cart_item.quantity, "subtotal": cart_item.total_price()}
        else:
            cart_item.delete()
            response = {"success": True, "quantity": 0, "subtotal": 0}
        return JsonResponse(response)


def handler404(request, exception):
    return render(request, "404.html", status=404)
