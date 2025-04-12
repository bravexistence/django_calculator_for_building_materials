import json
from django.core.management.base import BaseCommand
from parser_and_calculator.models import Product

class Command(BaseCommand):
    help = "Импортирует продукты из JSON в базу данных"

    def add_arguments(self, parser):
        parser.add_argument("json_path", type=str, help="Путь к JSON-файлу")

    def handle(self, *args, **kwargs):
        json_path = kwargs["json_path"]

        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        for item in data:
            name = item.get("name")
            url = item.get("url")

            obj, created = Product.objects.get_or_create(
                url=url,
                defaults={"name": name}
            )

            if created:
                self.stdout.write(self.style.SUCCESS(f"Добавлен: {name}"))
            else:
                self.stdout.write(self.style.WARNING(f"Уже существует: {name}"))
