from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from parser_and_calculator.models import SignBlock

@receiver([post_save, post_delete], sender=SignBlock)
def update_quote_totals(sender, instance, **kwargs):
    instance.quote.save(update_fields=[])