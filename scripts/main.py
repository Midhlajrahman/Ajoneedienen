from django.apps import apps
from django.core.files.storage import default_storage
from main.models import Category, DefaultProduct, Product


def check_file(app, model_name, file_field_names=()):
    Model = apps.get_model(app, model_name)
    instances = Model.objects.all()

    for instance in instances:
        for file_field_name in file_field_names:
            file_field = getattr(instance, file_field_name)
            file_path = file_field.path if file_field else None

            if file_path and not default_storage.exists(file_path):
                print(f"{file_path}")


def run():
    # check_file(app="main", model_name="Restaurant", file_field_names=("logo", "feature_image"))
    # check_file(app="main", model_name="DefaultCategory", file_field_names=("image",))
    # check_file(app="main", model_name="DefaultSubcategory", file_field_names=("image",))
    # check_file(app="main", model_name="Category", file_field_names=("image",))
    # check_file(app="main", model_name="Subcategory", file_field_names=("image",))
    # check_file(app="main", model_name="Product", file_field_names=("image",))
    # check_file(app="main", model_name="Banner", file_field_names=("image",))
    # check_file(app="main", model_name="CatalogueAd", file_field_names=("image",))
    # check_file(app="main", model_name="CheckoutAd", file_field_names=("image",))
    # check_file(app="main", model_name="ProductAd", file_field_names=("image",))
    # check_file(app="main", model_name="VideoPageAd", file_field_names=("image",))


