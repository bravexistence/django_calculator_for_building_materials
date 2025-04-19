from django.apps import AppConfig


class ParserAndCalculatorConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "parser_and_calculator"

    def ready(self):
        import parser_and_calculator.signals