from uuid import uuid4

from django.contrib.auth.models import User
from django.db import models
from django.template.defaultfilters import slugify
from django.urls import reverse
from easy_thumbnails.fields import ThumbnailerImageField

SECTION_CHOICE = (("non-ac", "non-ac"), ("ac", "ac"))


class BaseModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False, blank=True)
    created_at = models.DateTimeField(db_index=True, auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User, blank=True, null=True, related_name="creator_%(class)s_objects", on_delete=models.CASCADE
    )

    class Meta:
        abstract = True


class State(BaseModel):
    name = models.CharField("State Name", max_length=50)

    def __str__(self):
        return self.name


class District(BaseModel):
    state = models.ForeignKey(State, on_delete=models.CASCADE)
    name = models.CharField("State Name", max_length=50)

    def __str__(self):
        return f"{self.state} - {self.name}"


class Restaurant(BaseModel):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, limit_choices_to={"is_staff": True}, blank=True, null=True
    )
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    logo = models.ImageField(upload_to="restaurant_logos", blank=True, null=True)
    district = models.ForeignKey(District, on_delete=models.CASCADE, blank=True, null=True)
    address = models.TextField()
    is_blocked = models.BooleanField(default=False)

    phone = models.CharField(max_length=200, help_text="Phone number with country code")
    whatsapp = models.CharField(max_length=200, help_text="Whatsapp number with country code")
    whatsapp_message = models.CharField(max_length=200, blank=True, null=True)
    facebook_url = models.URLField(max_length=200, blank=True, null=True)
    instagram_url = models.URLField(max_length=200, blank=True, null=True)
    youtube_url = models.URLField(max_length=200, blank=True, null=True)
    twitter_url = models.URLField(max_length=200, blank=True, null=True)
    location_url = models.URLField(max_length=200, blank=True, null=True)

    feature_title = models.CharField(max_length=200, blank=True, null=True)
    feature_image = models.ImageField(upload_to="restaurant/feature_images/")
    feature_description = models.TextField(blank=True, null=True)
    visitor_count = models.PositiveIntegerField(default=1)

    enable_sending = models.BooleanField(default=False)
    is_Booknow = models.BooleanField(default=False)
    is_socialmedia = models.BooleanField(default=False)

    class Meta:
        ordering = ("name",)
        verbose_name_plural = "Restaurants"

    def get_absolute_url(self):
        return reverse("web:restaurant_slug_catalogue", kwargs={"slug": self.slug})

    def get_web_url(self):
        return reverse("web:restaurant_slug_catalogue", kwargs={"slug": self.slug})

    def get_categories(self):
        return Category.objects.filter(restaurant=self)

    def get_populars(self):
        return Product.objects.filter(subcategory__category__restaurant=self, is_popular=True)

    def save(self, *args, **kwargs):  # new
        if not self.slug:
            self.slug = slugify(self.name)
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class DefaultCategory(BaseModel):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to="category_images/")
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ("name",)
        verbose_name_plural = "Default Categories"


class DefaultSubcategory(BaseModel):
    category = models.ForeignKey(DefaultCategory, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to="subcategory_images/", blank=True, null=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ("name",)
        verbose_name_plural = "Default Subcategories"


class DefaultProduct(BaseModel):
    subcategory = models.ForeignKey(DefaultSubcategory, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    ingredients = models.TextField(blank=True)
    image = models.ImageField(upload_to="product_images/")
    is_popular = models.BooleanField(default=True)
    is_vegetarian = models.BooleanField(default=True)
    display_foodtype = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ("name",)
        verbose_name_plural = "Default Products"


class DefualtproductOption(BaseModel):
    product = models.ForeignKey(DefaultProduct, on_delete=models.CASCADE)
    section = models.CharField(max_length=100, choices=SECTION_CHOICE, default="non-ac", null=True, blank=True)
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def str(self):
        return self.name


class Category(BaseModel):
    reference = models.ForeignKey(DefaultCategory, on_delete=models.CASCADE, blank=True, null=True)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to="category_images/")
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

    def get_web_url(self):
        return reverse("web:category_catalogue", kwargs={"pk": self.pk})

    def get_absolute_url(self):
        return reverse("main:category_detail", kwargs={"pk": self.pk})

    def get_edit_url(self):
        return reverse("main:category_edit", kwargs={"pk": self.pk})

    def get_delete_url(self):
        return reverse("main:category_delete", kwargs={"pk": self.pk})

    def get_subcategories(self):
        return Subcategory.objects.filter(category=self)

    def get_products(self):
        return Product.objects.filter(subcategory__category=self, is_active=True)

    class Meta:
        ordering = ("name",)
        verbose_name_plural = "Categories"


class Subcategory(BaseModel):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to="subcategory_images/", blank=True, null=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

    def get_edit_url(self):
        return reverse("main:subcategory_edit", kwargs={"pk": self.pk})

    def get_delete_url(self):
        return reverse("main:subcategory_delete", kwargs={"pk": self.pk})

    def get_products(self):
        return Product.objects.filter(subcategory=self)
    
    def has_products(self):
        return Product.objects.filter(subcategory=self).exists()

    class Meta:
        ordering = ("name",)
        verbose_name_plural = "Subcategories"


class Product(BaseModel):
    subcategory = models.ForeignKey(Subcategory, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    ingredients = models.TextField(blank=True)
    image = ThumbnailerImageField(upload_to="product_images/")
    is_popular = models.BooleanField(default=True)
    is_vegetarian = models.BooleanField(default=True)
    display_foodtype = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ("name",)
        verbose_name_plural = "Products"

    def get_absolute_url(self):
        return reverse("main:product_detail", kwargs={"pk": self.pk})

    def get_edit_url(self):
        return reverse("main:product_edit", kwargs={"pk": self.pk})

    def get_delete_url(self):
        return reverse("main:product_delete", kwargs={"pk": self.pk})

    def get_options(self):
        return Option.objects.filter(product=self)

    def get_price(self):
        return min([option.price for option in self.get_options()])

    def get_ac_price(self):
        prices = [option.price for option in self.get_options() if option.section == "ac"]
        if prices:
            return min(prices)
        else:
            return None
        # return min(prices) if prices else None

    def get_non_ac_price(self):
        prices = [option.price for option in self.get_options() if option.section == "non-ac"]
        if prices:
            return min(prices)
        else:
            return None
        # return min(prices) if prices else None


class Option(BaseModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    section = models.CharField(max_length=100, choices=SECTION_CHOICE, default="non-ac", null=True, blank=True)
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.product.name} - {self.name}"

    def get_delete_url(self):
        return reverse("main:option_delete", kwargs={"pk": self.pk})

    def get_edit_url(self):
        return reverse("main:option_edit", kwargs={"pk": self.pk})

    class Meta:
        ordering = ("product", "price")
        verbose_name_plural = "Options"


class Banner(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    image = models.ImageField(upload_to="banners/")

    def __str__(self):
        return str(self.restaurant.name)


class CatalogueAd(models.Model):
    image = models.ImageField(upload_to="catalogue/ads/")
    display_upto = models.DateField()
    display_in = models.ManyToManyField(Restaurant, blank=True)

    def __str__(self):
        return f"Advertisement: {self.image.url}"


class CheckoutAd(models.Model):
    image = models.ImageField(upload_to="checkout/ads/")
    display_upto = models.DateField()
    display_in = models.ManyToManyField(Restaurant, blank=True)

    def __str__(self):
        return f"Advertisement: {self.image.url}"


class ProductAd(models.Model):
    image = models.ImageField(upload_to="product/ads/")
    display_upto = models.DateField()
    display_in = models.ManyToManyField(Restaurant, blank=True)

    def __str__(self):
        return f"Advertisement: {self.image.url}"


class CartItem(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    session_key = models.CharField(max_length=200)
    product = models.ForeignKey(Option, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=0)

    def total_price(self):
        return self.product.price * self.quantity

    def __str__(self):
        return f"{self.product.name} - {self.quantity}"


class Notification(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    notification = models.TextField()

    def get_absolute_url(self):
        return reverse("main:notification_detail", kwargs={"pk": self.pk})

    def get_edit_url(self):
        return reverse("main:notification_edit", kwargs={"pk": self.pk})

    def get_delete_url(self):
        return reverse("main:notification_delete", kwargs={"pk": self.pk})

    def __str__(self):
        return str(self.notification)


class VideoPageAd(models.Model):
    image = models.ImageField(upload_to="catalogue/ads/")
    display_upto = models.DateField()
    display_in = models.ManyToManyField(Restaurant, blank=True)

    def __str__(self):
        return f"VideoPageAd: {self.image.url}"


class Badge(models.Model):
    title = models.CharField(max_length=100)
    value = models.CharField(max_length=100)

    def __str__(self):
        return self.title


class Feedback(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    message = models.TextField()
    reaction = models.CharField(max_length=255)  # Assuming reaction is a string

    def __str__(self):
        return self.name
