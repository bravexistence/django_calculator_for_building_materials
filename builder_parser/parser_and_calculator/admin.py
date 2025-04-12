import threading
from django.core.cache import cache
from django.urls import path
from django.shortcuts import redirect
from django.contrib import admin, messages
from .models import Product
from .parser import ORMProductParser

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """
    Admin class for Product, providing:
    - two top buttons: "Обновить всё" and "Обновить выделенные"
    - only "Удалить выбранные" in the dropdown (actions)
    """
    list_display = ["name", "price", "add_margin", "final_price", "url"]
    readonly_fields = ["final_price"]
    actions = ["delete_selected"]  # только удаление в выпадающем списке

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "update_all_prices/",
                self.admin_site.admin_view(self.update_all_prices),
                name="update_all_prices"
            ),
            path(
                "update_selected_prices/",
                self.admin_site.admin_view(self.update_selected_prices),
                name="update_selected_prices"
            ),
        ]
        return custom_urls + urls

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context["custom_buttons"] = True
        extra_context["is_updating"] = self.is_updating()
        return super().changelist_view(request, extra_context=extra_context)

    def is_updating(self):
        return cache.get("product_update_in_progress", False)

    def set_updating(self, status: bool):
        cache.set("product_update_in_progress", status, timeout=3600)  # 1 час максимум

    def update_all_prices(self, request):
        self.set_updating(True)

        def run_parser():
            try:
                parser = ORMProductParser()
                queryset = Product.objects.all()
                parser.parse_queryset_and_save(queryset)
            finally:
                self.set_updating(False)

        threading.Thread(target=run_parser).start()
        self.message_user(request, "Запущено обновление цен для всех товаров.")
        return redirect("..")

    def update_selected_prices(self, request):
        ids_str = request.GET.get("ids")
        if not ids_str:
            self.message_user(request, "Не выбраны товары для обновления.", level=messages.WARNING)
            return redirect("..")

        ids_list = [int(pk) for pk in ids_str.split(",") if pk.isdigit()]
        self.set_updating(True)  # <--- Добавлено

        def run_parser():
            try:
                parser = ORMProductParser()
                queryset = Product.objects.filter(pk__in=ids_list)
                parser.parse_queryset_and_save(queryset)
            finally:
                self.set_updating(False)  # <--- Добавлено

        threading.Thread(target=run_parser).start()
        self.message_user(
            request,
            f"Запущено обновление цен для {len(ids_list)} выбранных товаров (в фоне)."
        )
        return redirect("..")
