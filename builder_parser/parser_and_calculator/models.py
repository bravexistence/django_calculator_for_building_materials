from django.db import models

class Product(models.Model):
    name = models.CharField(max_length=255)
    url = models.URLField(null=True, blank=True)
    price = models.FloatField(null=True, blank=True, verbose_name="Цена")
    add_margin = models.BooleanField(default=False, verbose_name="20%")
    final_price = models.FloatField(null=True, blank=True, editable=False, verbose_name="Итоговая цена")

    def save(self, *args, **kwargs):
        if self.price is not None:
            self.final_price = self.price * 1.2 if self.add_margin else self.price
        else:
            self.final_price = None
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.final_price})"
