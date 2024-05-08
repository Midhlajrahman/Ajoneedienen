import admin_thumbnails
from django.contrib import admin
from django.db import models
from django.forms import CheckboxSelectMultiple
from import_export.admin import ImportExportActionModelAdmin
from registration.models import RegistrationProfile

from .models import (
    Badge,
    Banner,
    CartItem,
    CatalogueAd,
    Category,
    CheckoutAd,
    DefaultCategory,
    DefaultProduct,
    DefaultSubcategory,
    DefualtproductOption,
    District,
    Feedback,
    Notification,
    Option,
    Product,
    ProductAd,
    Restaurant,
    State,
    Subcategory,
    VideoPageAd,
)

admin.site.unregister(RegistrationProfile)


@admin.register(State)
class StateAdmin(ImportExportActionModelAdmin):
    pass


@admin.register(District)
class DistrictAdmin(ImportExportActionModelAdmin):
    pass


@admin.register(Restaurant)
@admin_thumbnails.thumbnail("logo")
class RestaurantAdmin(ImportExportActionModelAdmin):
    list_display = ("name", "user", "phone")
    list_filter = ("name", "user")
    autocomplete_fields = ("user",)
    search_fields = ("name", "user__username")
    readonly_fields = ("created_by",)
    prepopulated_fields = {"slug": ("name",)}


@admin.register(DefaultCategory)
@admin_thumbnails.thumbnail("image")
class DefaultCategoryAdmin(ImportExportActionModelAdmin):
    list_display = ("name", "image")
    search_fields = ("name", "description")
    readonly_fields = ("created_by",)


@admin.register(Category)
@admin_thumbnails.thumbnail("image")
class CategoryAdmin(ImportExportActionModelAdmin):
    list_display = ("name", "restaurant", "image")
    list_filter = ("restaurant",)
    autocomplete_fields = ("restaurant",)
    search_fields = ("name", "description")
    readonly_fields = ("created_by",)


@admin.register(Subcategory)
@admin_thumbnails.thumbnail("image")
class SubcategoryAdmin(ImportExportActionModelAdmin):
    list_display = ("name", "category", "image")
    list_filter = ("category","category__restaurant")
    autocomplete_fields = ("category",)
    search_fields = ("name", "description")
    readonly_fields = ("created_by",)


@admin.register(Option)
class OptionAdmin(ImportExportActionModelAdmin):
    list_display = ("name", "product")
    list_filter = ("product",)
    autocomplete_fields = ("product",)
    search_fields = ("name",)
    readonly_fields = ("created_by",)


class OptionInline(admin.TabularInline):
    model = Option
    extra = 1
    fields = ("name", "price")


@admin.register(Product)
@admin_thumbnails.thumbnail("image")
class ProductAdmin(ImportExportActionModelAdmin):
    list_display = ("name", "subcategory", "description", "image")
    list_filter = ("name", "subcategory", "subcategory__category", "subcategory__category__restaurant")
    autocomplete_fields = ("subcategory",)
    readonly_fields = ("created_by",)
    search_fields = ("name", "description")
    inlines = (OptionInline,)


@admin.register(Banner)
@admin_thumbnails.thumbnail("image")
class BannerAdmin(ImportExportActionModelAdmin):
    pass


@admin.register(CartItem)
class CartItemAdmin(ImportExportActionModelAdmin):
    list_display = ("__str__", "restaurant", "quantity", "total_price")
    list_filter = ("restaurant",)


@admin.register(CatalogueAd)
@admin_thumbnails.thumbnail("image")
class CatalogueAdAdmin(ImportExportActionModelAdmin):
    list_display = ("__str__", "display_upto")
    formfield_overrides = {models.ManyToManyField: {"widget": CheckboxSelectMultiple}}

    class Media:
        js = ("custom_admin/script.js",)
        css = {"all": ("custom_admin/style.css",)}


@admin.register(CheckoutAd)
@admin_thumbnails.thumbnail("image")
class CheckoutAdAdmin(ImportExportActionModelAdmin):
    list_display = ("__str__", "display_upto")
    formfield_overrides = {models.ManyToManyField: {"widget": CheckboxSelectMultiple}}

    class Media:
        js = ("custom_admin/script.js",)
        css = {"all": ("custom_admin/style.css",)}


@admin.register(ProductAd)
@admin_thumbnails.thumbnail("image")
class ProductAdAdmin(ImportExportActionModelAdmin):
    list_display = ("__str__", "display_upto")
    formfield_overrides = {models.ManyToManyField: {"widget": CheckboxSelectMultiple}}

    class Media:
        js = ("custom_admin/script.js",)
        css = {"all": ("custom_admin/style.css",)}


@admin.register(Notification)
class NotificationAdmin(ImportExportActionModelAdmin):
    list_display = ("restaurant", "notification")
    list_filter = ("restaurant",)


@admin.register(VideoPageAd)
@admin_thumbnails.thumbnail("image")
class VideoPageAdAdmin(ImportExportActionModelAdmin):
    list_display = ("__str__", "display_upto")
    formfield_overrides = {models.ManyToManyField: {"widget": CheckboxSelectMultiple}}

    class Media:
        js = ("custom_admin/script.js",)
        css = {"all": ("custom_admin/style.css",)}


@admin.register(Badge)
class BadgeAdmin(ImportExportActionModelAdmin):
    list_display = ("title", "value")
    search_fields = ("title",)


@admin.register(Feedback)
class FeedbackAdmin(ImportExportActionModelAdmin):
    list_display = ("name", "restaurant", "reaction")
    list_filter = ("restaurant", "reaction")


class DefualtproductOptionInline(admin.TabularInline):
    model = DefualtproductOption
    extra = 1
    fields = ("name", "price", "section")


@admin.register(DefaultProduct)
class DefaultProductAdmin(ImportExportActionModelAdmin):
    list_display = ("name", "subcategory", "image")
    list_filter = ("subcategory",)
    inlines = (DefualtproductOptionInline,)


@admin.register(DefaultSubcategory)
@admin_thumbnails.thumbnail("image")
class DefaultSubcategoryAdmin(ImportExportActionModelAdmin):
    list_display = ("name", "category", "image")
    list_filter = ("category",)
