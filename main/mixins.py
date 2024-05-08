from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import redirect

from .models import Restaurant


class SuperuserRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_superuser


class RestaurantRequiredMixin(LoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        # Check if the user is authenticated
        if not request.user.is_authenticated:
            return redirect("auth_login")
        # Get the restaurant associated with the user
        if not request.user.is_superuser:
            try:
                restaurant = Restaurant.objects.get(user=request.user)
                return super().dispatch(request, *args, **kwargs)
            except Restaurant.DoesNotExist:
                print("restaurant not found")
                return redirect("main:auto_restaurant")

            # Check if the restaurant is blocked
            if restaurant.is_blocked:
                print("restaurant blocked")
                return redirect("main:restaurant_blocked")
        else:
            return super().dispatch(request, *args, **kwargs)
