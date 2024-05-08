from django import forms
from django.contrib.auth.models import User

from .models import Product, Restaurant


class RestaurantCreateForm(forms.ModelForm):
    username = forms.CharField(max_length=200, label="Username")
    password = forms.CharField(widget=forms.PasswordInput(), max_length=200, label="Password")

    class Meta:
        model = Restaurant
        fields = (
            "name",
            "logo",
            "address",
            "phone",
            "district",
            "facebook_url",
            "instagram_url",
            "youtube_url",
            "twitter_url",
            "enable_sending",
        )

    def clean_username(self):
        username = self.cleaned_data.get("username")
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Username is already taken.")
        return username

    def save(self, commit=True):
        restaurant = super().save(commit=False)
        username = self.cleaned_data.get("username")
        password = self.cleaned_data.get("password")
        if not restaurant.user:
            restaurant.user = User.objects.create_user(username=username, password=password, is_staff=True)
        if commit:
            restaurant.save()
        return restaurant


class RestaurantEditForm(forms.ModelForm):
    class Meta:
        model = Restaurant
        fields = (
            "name",
            "logo",
            "address",
            "phone",
            "district",
            "facebook_url",
            "instagram_url",
            "youtube_url",
            "twitter_url",
            "enable_sending",
        )


class ProductForm(forms.ModelForm):
    price = forms.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        model = Product
        fields = [
            "subcategory",
            "name",
            "description",
            "ingredients",
            "image",
            "is_popular",
            "is_vegetarian",
            "display_foodtype",
            "is_active",
        ]
