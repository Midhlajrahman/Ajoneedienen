from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.views import View, generic
from django.views.decorators.http import require_POST
from django.views.generic.edit import DeleteView, UpdateView
from registration.views import RegistrationView
from django.http import HttpResponse
from .forms import ProductForm, RestaurantCreateForm, RestaurantEditForm
from .mixins import RestaurantRequiredMixin, SuperuserRequiredMixin
from .models import (
    CartItem,
    Category,
    DefaultCategory,
    DefaultProduct,
    DefaultSubcategory,
    DefualtproductOption,
    Feedback,
    Notification,
    Option,
    Product,
    Restaurant,
    Subcategory,
    VideoPageAd,
)


class UserRegisterView(RegistrationView):
    success_url = reverse_lazy("main:index")

    def register(self, form):
        new_user = User.objects.create_user(
            username=form.cleaned_data["username"],
            password=form.cleaned_data["password1"],
            email=form.cleaned_data["email"],
        )
        new_user.is_staff = True
        new_user.save()

        user = authenticate(
            self.request, username=form.cleaned_data["username"], password=form.cleaned_data["password1"]
        )
        if user is not None:
            login(self.request, user)

        return new_user


class IndexView(LoginRequiredMixin, generic.ListView):
    def get(self, request, *args, **kwargs):
        if request.user.is_superuser:
            return redirect("main:admin_index")
        elif request.user.is_staff:
            return redirect("main:restaurant_index")
        else:
            return redirect("main:shop_index")


class AdminIndexView(LoginRequiredMixin, SuperuserRequiredMixin, generic.ListView):
    context_object_name = "products"
    paginate_by = 50
    template_name = "main/admin_index.html"

    def get_queryset(self):
        return Product.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Home"
        context["restaurant_count"] = Restaurant.objects.all().count()
        context["product_count"] = Product.objects.all().count()
        context["category_count"] = Category.objects.all().count()
        context["subcategory_count"] = Subcategory.objects.all().count()
        return context


class RestaurantBlockedView(LoginRequiredMixin, generic.TemplateView):
    template_name = "main/restaurant_blocked.html"


class AutoRestaurantUpdateView(LoginRequiredMixin, generic.FormView):
    model = Restaurant
    template_name = "main/restaurant_update.html"
    success_url = reverse_lazy("main:index")

    def dispatch(self, request, *args, **kwargs):
        if not self.request.user.is_superuser and Restaurant.objects.filter(user=self.request.user).exists():
            return redirect("main:admin_index")
        return super().dispatch(request, *args, **kwargs)

    def get_form(self, form_class=None):
        if Restaurant.objects.filter(user=self.request.user).exists():
            return RestaurantEditForm(
                self.request.POST or None,
                self.request.FILES or None,
                instance=Restaurant.objects.get(user=self.request.user),
            )
        else:
            return RestaurantEditForm(self.request.POST or None, self.request.FILES or None)

    def form_valid(self, form):
        data = form.save()
        data.user = self.request.user
        data.save()
        # Create categories for the restaurant
        # Create categories for the restaurant
        for cat in DefaultCategory.objects.all():
            category_instance = Category.objects.create(
                restaurant=data, name=cat.name, image=cat.image, description=cat.description
            )

            # Create subcategories for each category
            for subcat in DefaultSubcategory.objects.filter(category=cat):
                subcategory_instance = Subcategory.objects.create(
                    category=category_instance, name=subcat.name, description=subcat.description
                )

                # Create products for each subcategory
                for product in DefaultProduct.objects.filter(subcategory=subcat):
                    product_instance = Product.objects.create(
                        subcategory=subcategory_instance,
                        name=product.name,
                        description=product.description,
                        ingredients=product.ingredients,
                        image=product.image,
                        is_popular=product.is_popular,
                        is_vegetarian=product.is_vegetarian,
                        display_foodtype=product.display_foodtype,
                        is_active=product.is_active,
                    )

                    # Create options for each product
                    for option in DefualtproductOption.objects.filter(product=product):
                        Option.objects.create(
                            product=product_instance, section=option.section, name=option.name, price=option.price
                        )

        return super().form_valid(form)

    def form_invalid(self, form):
        print("data is not saved", form.errors)
        return super().form_invalid(form)


class RestaurantProfileView(RestaurantRequiredMixin, generic.FormView):
    model = Restaurant
    template_name = "main/restaurant_profile.html"
    success_url = reverse_lazy("main:index")

    def get_form(self, form_class=None):
        if Restaurant.objects.filter(user=self.request.user).exists():
            return RestaurantEditForm(
                self.request.POST or None,
                self.request.FILES or None,
                instance=Restaurant.objects.get(user=self.request.user),
            )
        else:
            return RestaurantEditForm(self.request.POST or None, self.request.FILES or None)

    def form_valid(self, form):
        data = form.save()
        data.user = self.request.user
        data.save()
        return super().form_valid(form)

    def form_invalid(self, form):
        print("data is not saved", form.errors)
        return super().form_invalid(form)


class RestaurantIndexView(RestaurantRequiredMixin, generic.ListView):
    context_object_name = "products"
    paginate_by = 50
    template_name = "main/restaurant_index.html"

    def get_queryset(self):
        return Product.objects.filter(
            is_active=True, subcategory__category__restaurant=Restaurant.objects.get(user=self.request.user)
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Home"
        restaurant = Restaurant.objects.get(user=self.request.user)
        category_count = Category.objects.filter(restaurant=restaurant).count()
        subcategory_count = Subcategory.objects.filter(category__restaurant=restaurant).count()
        product_count = Product.objects.filter(is_active=True, subcategory__category__restaurant=restaurant).count()
        context["restaurant"] = restaurant
        context["category_count"] = category_count
        context["subcategory_count"] = subcategory_count
        context["product_count"] = product_count
        return context


class RestaurantListView(LoginRequiredMixin, SuperuserRequiredMixin, generic.ListView):
    template_name = "main/restaurant_list.html"
    context_object_name = "restaurants"
    paginate_by = 50

    def get_queryset(self):
        return Restaurant.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Restaurants"
        return context


class RestaurantDetailView(LoginRequiredMixin, SuperuserRequiredMixin, generic.DetailView):
    model = Restaurant
    template_name = "main/restaurant_detail.html"
    context_object_name = "restaurant"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Restaurant"
        return context


class RestaurantUpdateView(LoginRequiredMixin, SuperuserRequiredMixin, UpdateView):
    model = Restaurant
    template_name = "main/restaurant_update.html"
    form_class = RestaurantEditForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Restaurant"
        return context

    def get_success_url(self):
        return reverse_lazy("main:restaurant_list")


class RestaurantCreateView(LoginRequiredMixin, SuperuserRequiredMixin, generic.CreateView):
    model = Restaurant
    template_name = "main/restaurant_create.html"
    form_class = RestaurantCreateForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Restaurant"
        return context


class CategoryListView(RestaurantRequiredMixin, generic.ListView):
    template_name = "main/category_list.html"
    context_object_name = "categories"
    paginate_by = 100

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Category.objects.all()
        else:
            restaurant = Restaurant.objects.get(user=self.request.user)
            return Category.objects.filter(restaurant=restaurant)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Categories"
        return context


class CategoryDetailView(RestaurantRequiredMixin, generic.DetailView):
    template_name = "main/category_detail.html"
    paginate_by = 50

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Category.objects.all()
        else:
            restaurant = Restaurant.objects.get(user=self.request.user)
            return Category.objects.filter(restaurant=restaurant)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Categories"
        return context


class CategoryCreateView(RestaurantRequiredMixin, generic.CreateView):
    model = Category
    template_name = "main/category_create.html"
    fields = ("name", "image", "description")
    success_url = reverse_lazy("main:index")

    def form_valid(self, form):
        data = form.save(commit=False)
        data.restaurant = Restaurant.objects.get(user=self.request.user)
        data.save()
        return super().form_valid(form)


class CategoryUpdateView(RestaurantRequiredMixin, UpdateView):
    model = Category
    template_name = "main/category_update.html"
    fields = ("name", "image", "description")

    def dispatch(self, request, *args, **kwargs):
        if not self.request.user.is_superuser and not Category.objects.get(pk=kwargs["pk"]).restaurant.user == request.user:
            raise PermissionDenied()
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy("main:index")


class CategoryDeleteView(RestaurantRequiredMixin, DeleteView):
    model = Category
    template_name = "main/category_delete.html"

    def dispatch(self, request, *args, **kwargs):
        if not self.request.user.is_superuser and not Category.objects.get(pk=kwargs["pk"]).restaurant.user == request.user:
            raise PermissionDenied()
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy("main:index")


class SubcategoryListView(RestaurantRequiredMixin, generic.ListView):
    template_name = "main/subcategory_list.html"
    context_object_name = "subcategories"
    paginate_by = 100

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Subcategory.objects.all()
        else:
            restaurant = Restaurant.objects.get(user=self.request.user)
            return Subcategory.objects.filter(category__restaurant=restaurant)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Categories"
        return context


class SubcategoryCreateView(RestaurantRequiredMixin, generic.CreateView):
    model = Subcategory
    template_name = "main/subcategory_create.html"
    fields = ("name", "image", "description")

    def form_valid(self, form):
        category_pk = self.kwargs.get("category_pk")
        category = get_object_or_404(Category, pk=category_pk)
        data = form.save(commit=False)
        data.category = category
        data.save()
        return super().form_valid(form)

    def get_success_url(self):
        category_pk = self.kwargs.get("category_pk")
        category = get_object_or_404(Category, pk=category_pk)
        return category.get_absolute_url()


class SubcategoryUpdateView(RestaurantRequiredMixin, UpdateView):
    model = Subcategory
    template_name = "main/subcategory_update.html"
    fields = ("name", "image", "description")

    def dispatch(self, request, *args, **kwargs):
        if not self.request.user.is_superuser and not self.get_object().category.restaurant.user == request.user:
            raise PermissionDenied()
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy("main:index")


class SubcategoryDeleteView(RestaurantRequiredMixin, DeleteView):
    model = Subcategory
    template_name = "main/subcategory_delete.html"

    def dispatch(self, request, *args, **kwargs):
        if not self.request.user.is_superuser and not self.get_object().category.restaurant.user == request.user:
            raise PermissionDenied()
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy("main:index")


class ProductListView(RestaurantRequiredMixin, generic.ListView):
    template_name = "main/product_list.html"
    context_object_name = "products"
    paginate_by = 300

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Product.objects.all()
        else:
            restaurant = Restaurant.objects.get(user=self.request.user)
            return Product.objects.filter(is_active=True, subcategory__category__restaurant=restaurant)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Products"
        return context


class ProductDetailView(RestaurantRequiredMixin, generic.DetailView):
    template_name = "main/product_detail.html"
    paginate_by = 50

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Product.objects.all()
        else:
            restaurant = Restaurant.objects.get(user=self.request.user)
            return Product.objects.filter(is_active=True, subcategory__category__restaurant=restaurant)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Products"
        return context


class ProductCreateView(RestaurantRequiredMixin, generic.CreateView):
    model = Product
    template_name = "main/product_create.html"
    form_class = ProductForm
    success_url = reverse_lazy("main:index")

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields["subcategory"].queryset = Subcategory.objects.filter(category__restaurant__user=self.request.user)
        return form

    def form_valid(self, form):
        response = super().form_valid(form)
        price = self.request.POST.get("price")
        Option.objects.create(product=self.object, name="Full", price=price)
        return response


class ProductUpdateView(RestaurantRequiredMixin, UpdateView):
    model = Product
    template_name = "main/product_update.html"
    fields = (
        "subcategory",
        "name",
        "description",
        "ingredients",
        "image",
        "is_vegetarian",
        "display_foodtype",
        "is_popular",
        "is_active",
    )

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields["subcategory"].queryset = Subcategory.objects.filter(category__restaurant__user=self.request.user)
        return form

    def dispatch(self, request, *args, **kwargs):
        if not self.request.user.is_superuser and not self.get_object().subcategory.category.restaurant.user == request.user:
            raise PermissionDenied()
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy("main:index")


class ProductDeleteView(RestaurantRequiredMixin, DeleteView):
    model = Product
    template_name = "main/product_delete.html"

    def dispatch(self, request, *args, **kwargs):
        if not self.request.user.is_superuser and not self.get_object().subcategory.category.restaurant.user == request.user:
            raise PermissionDenied()
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy("main:index")


class AddCartView(View):
    def get(self, request, *args, **kwargs):
        session_key = request.session.session_key
        cart_items = CartItem.objects.filter(session_key=session_key)
        total_price = sum(item.product.price * item.quantity for item in cart_items)
        context = {"cart_items": cart_items, "total_price": total_price}
        return render(request, "web/includes/cart.html", context)

    def post(self, request, *args, **kwargs):
        option_pk = request.POST.get("option_pk")
        quantity = request.POST.get("quantity")
        session_key = request.session.session_key

        cart_item, created = CartItem.objects.get_or_create(
            session_key=session_key, product_id=option_pk, defaults={"quantity": quantity}
        )

        if not created:
            cart_item.quantity += int(quantity)
            cart_item.save()

        return JsonResponse({"message": "Item added to cart successfully"})


class MinusCartView(View):
    def get(self, request, pk, *args, **kwargs):
        try:
            option = Option.objects.get(pk=pk)
            session_key = request.session.session_key
            try:
                cart_item = CartItem.objects.get(session_key=session_key, option=option)
                if cart_item.quantity > 1:
                    cart_item.quantity -= 1
                    cart_item.save()
                else:
                    cart_item.delete()

                return JsonResponse({"message": "Product removed from cart successfully"})
            except CartItem.DoesNotExist:
                return JsonResponse({"message": "Product not found in cart"}, status=404)
        except Option.DoesNotExist:
            return JsonResponse({"message": "Product option does not exist"}, status=404)


class HowItWorksView(generic.DetailView):
    template_name = "web/howitworks.html"
    context_object_name = "restaurant"
    model = Restaurant

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        restaurant = self.get_object()
        context["banners"] = VideoPageAd.objects.filter(display_upto__gte=timezone.now(), display_in__in=[restaurant])
        return context


class NotificationListView(RestaurantRequiredMixin, generic.ListView):
    template_name = "main/notification_list.html"
    context_object_name = "notifications"
    paginate_by = 50

    def get_queryset(self):
        restaurant = Restaurant.objects.get(user=self.request.user)
        return Notification.objects.filter(restaurant=restaurant)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Notifications"
        return context


class NotificationDetailView(RestaurantRequiredMixin, generic.DetailView):
    template_name = "main/notification_detail.html"
    paginate_by = 50

    def get_queryset(self):
        restaurant = Restaurant.objects.get(user=self.request.user)
        return Notification.objects.filter(restaurant=restaurant)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Notifications"
        return context


class NotificationCreateView(RestaurantRequiredMixin, generic.CreateView):
    model = Notification
    template_name = "main/notification_create.html"
    fields = ("notification",)
    success_url = reverse_lazy("main:index")

    def form_valid(self, form):
        data = form.save(commit=False)
        data.restaurant = Restaurant.objects.get(user=self.request.user)
        data.save()
        return super().form_valid(form)


class NotificationUpdateView(RestaurantRequiredMixin, UpdateView):
    model = Notification
    template_name = "main/notification_update.html"
    fields = ("notification",)

    def dispatch(self, request, *args, **kwargs):
        if not self.request.user.is_superuser and not self.get_object().restaurant.user == request.user:
            raise PermissionDenied()
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        data = form.save(commit=False)
        data.restaurant = Restaurant.objects.get(user=self.request.user)
        data.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("main:index")


class NotificationDeleteView(RestaurantRequiredMixin, DeleteView):
    model = Notification
    template_name = "main/notification_delete.html"

    def dispatch(self, request, *args, **kwargs):
        if not self.request.user.is_superuser and not self.get_object().restaurant.user == request.user:
            raise PermissionDenied()
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy("main:index")


class OptionDeleteView(RestaurantRequiredMixin, DeleteView):
    model = Option
    template_name = "main/option_delete.html"

    def dispatch(self, request, *args, **kwargs):
        if not self.request.user.is_superuser and not self.get_object().product.subcategory.category.restaurant.user == request.user:
            raise PermissionDenied()
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy("main:product_detail", kwargs={"pk": self.get_object().product.pk})


class OptionCreateView(RestaurantRequiredMixin, generic.CreateView):
    model = Option
    template_name = "main/option_create.html"
    fields = ("name", "section", "price")

    def get_success_url(self):
        product_pk = self.kwargs.get("product_pk")
        return reverse_lazy("main:product_detail", kwargs={"pk": product_pk})

    def form_valid(self, form):
        data = form.save(commit=False)
        product_pk = self.kwargs.get("product_pk")
        product = get_object_or_404(Product, pk=product_pk)
        data.product = product
        data.save()
        return super().form_valid(form)


class OptionUpdateView(RestaurantRequiredMixin, UpdateView):
    model = Option
    template_name = "main/option_update.html"
    fields = ("name", "section", "price")

    def dispatch(self, request, *args, **kwargs):
        if not self.request.user.is_superuser and not self.get_object().product.subcategory.category.restaurant.user == request.user:
            raise PermissionDenied()
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy("main:product_detail", kwargs={"pk": self.get_object().product.pk})


class FeedbackView(RestaurantRequiredMixin, generic.ListView):
    template_name = "main/feedback_list.html"
    context_object_name = "feedbacks"

    def get_queryset(self):
        restaurant = Restaurant.objects.get(user=self.request.user)
        return Feedback.objects.filter(restaurant=restaurant)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Feedback"
        return context


@require_POST
def submit_feedback(request):
    restaurant_id = request.POST.get("restaurant_id")
    name = request.POST.get("feedbackName")
    message = request.POST.get("feedbackMessage")
    reaction = request.POST.get("reaction")

    restaurant = Restaurant.objects.get(pk=restaurant_id)

    if not name or not message or not reaction:
        return JsonResponse({"error": "All fields are required"}, status=400)

    feedback = Feedback.objects.create(name=name, message=message, reaction=reaction, restaurant=restaurant)

    # Your further logic goes here

    return JsonResponse({"success": "Feedback submitted successfully"})


class UserLogoutView(View):
    def get(self, request, *args, **kwargs):
        logout(request)
        return redirect("main:index")


class DefaultCategoryListView(RestaurantRequiredMixin, generic.ListView):
    template_name = "main/category_list.html"
    context_object_name = "categories"
    paginate_by = 100
    model = DefaultCategory

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Default Categories"
        return context


class DefaultSubcategoryListView(RestaurantRequiredMixin, generic.ListView):
    template_name = "main/subcategory_list.html"
    context_object_name = "subcategories"
    paginate_by = 100
    model = DefaultSubcategory

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Categories"
        return context


class DefaultProductListView(RestaurantRequiredMixin, generic.ListView):
    template_name = "main/product_list.html"
    context_object_name = "products"
    paginate_by = 300
    model = DefaultProduct

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Default Products"
        return context


class MyCategoryListView(RestaurantRequiredMixin, generic.ListView):
    template_name = "main/category_list.html"
    context_object_name = "categories"
    paginate_by = 100

    def get_queryset(self):
        restaurant = Restaurant.objects.get(user=self.request.user)
        return Category.objects.filter(restaurant=restaurant)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "My Categories"
        return context
