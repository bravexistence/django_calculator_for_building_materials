import threading
from contextlib import contextmanager
from django.core.cache import cache
from django.urls import path
from django.shortcuts import redirect
from django.contrib import admin, messages
from .models import Product
from .parser import ORMProductParser


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ["name", "price", "add_margin", "final_price", "url"]
    readonly_fields = ["final_price"]
    actions = ["delete_selected"]
    LOCK_KEY = "product_update_in_progress"

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
        return cache.get(self.LOCK_KEY, False)

    def set_updating(self, status: bool):
        if status:
            cache.set(self.LOCK_KEY, True, timeout=None)
        else:
            cache.delete(self.LOCK_KEY)

    @contextmanager
    def _lock(self, ttl=None):
        acquired = cache.add(self.LOCK_KEY, True, timeout=ttl)
        try:
            yield acquired
        finally:
            if not acquired:
                pass

    def update_all_prices(self, request):
        with self._lock() as acquired:
            if not acquired:
                self.message_user(request, "Обновление уже запущено.", level=messages.WARNING)
                return redirect("..")

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

        if self.is_updating():
            self.message_user(request, "Обновление уже запущено.", level=messages.WARNING)
            return redirect("..")

        self.set_updating(True)

        def run_parser():
            try:
                parser = ORMProductParser()
                queryset = Product.objects.filter(pk__in=ids_list)
                parser.parse_queryset_and_save(queryset)
            finally:
                self.set_updating(False)

        threading.Thread(target=run_parser).start()
        self.message_user(
            request,
            f"Запущено обновление цен для {len(ids_list)} выбранных товаров (в фоне)."
        )
        return redirect("..")
