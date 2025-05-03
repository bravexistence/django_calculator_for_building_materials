from django.db import models
import math
from multiselectfield import MultiSelectField
from decimal import Decimal
from django.core.exceptions import ValidationError

class Product(models.Model):
    name = models.CharField(max_length=255)
    url = models.URLField(null=True, blank=True)
    price = models.FloatField(null=True, blank=True, verbose_name="Цена")
    add_margin = models.BooleanField(default=False, verbose_name="20%")
    final_price = models.FloatField(null=True, blank=True, editable=False, verbose_name="Итоговая цена")

    def clean(self):
        if self.pk:
            orig = Product.objects.get(pk=self.pk)
            if self.name != orig.name:
                raise ValidationError({"name": "Редактирование названия запрещено. Создайте новый продукт."})

    def save(self, *args, **kwargs):
        self.full_clean()  # вызывает clean()
        if self.price is not None:
            price = self.price
            if self.add_margin:
                price *= 1.2
            if self.name.lower().strip() == "провода":
                price *= 1.3334
            self.final_price = round(price, 2)
        else:
            self.final_price = None

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.final_price})"


class Quote(models.Model):
    MATERIAL_CHOICES = [
        ("пвх", "ПВХ"),
        ("алюк", "Алюкобонд"),
    ]

    materials = MultiSelectField("Материалы", choices=MATERIAL_CHOICES, default="пвх")

    client_name = models.CharField("Клиент", max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    area = models.FloatField("Площадь вывески", blank=True, null=True, editable=False)

    width_pvh = models.FloatField("Ширина ПВХ (м)", blank=True, null=True)
    height_pvh = models.FloatField("Высота ПВХ (м)", blank=True, null=True)
    area_pvh = models.FloatField("Площадь ПВХ", blank=True, null=True, editable=False)

    width_alyuk = models.FloatField("Ширина Алюкобонда (м)", blank=True, null=True)
    height_alyuk = models.FloatField("Высота Алюкобонда (м)", blank=True, null=True)
    area_alyuk = models.FloatField("Площадь Алюкобонда", blank=True, null=True, editable=False)

    special_technique = models.FloatField("Специальная техника (минимальный выезд 3 часа)", blank=True, null=True)
    ultrafiolet_base = models.FloatField("УФ печать подложка (1 или 0)", blank=True, null=True)
    ultrafiolet_letters_print = models.FloatField("УФ печать букв", blank=True, null=True)

    total_letters = models.PositiveIntegerField("Всего букв", editable=False, default=0)
    total_diodes = models.FloatField("Кол-во диодов", blank=True, null=True, editable=False)
    total_glue = models.FloatField("Кол-во клея", blank=True, null=True, editable=False)
    total_acrylic = models.FloatField("Акрил м²", blank=True, null=True, editable=False)
    total_pvc = models.FloatField("ПВХ м²", blank=True, null=True, editable=False)
    total_stripes = models.FloatField("Кол-во полос", blank=True, null=True, editable=False)
    total_oracal_m2 = models.FloatField("Оракал м²", blank=True, null=True, editable=False)
    total_wire_m = models.FloatField("Провода м.п.", blank=True, null=True, editable=False)
    total_power_watt = models.FloatField("Мощность трансформатора (Вт)", blank=True, null=True, editable=False)
    sheets = models.FloatField("Листов", blank=True, null=True, editable=False)
    profile = models.FloatField("Профиль ШТ", blank=True, null=True, editable=False)
    silicone = models.FloatField("Силикон", blank=True, null=True, editable=False)
    oracal = models.FloatField("Оракал", blank=True, null=True, editable=False)
    total_back = models.FloatField("Задники", blank=True, null=True, editable=False)
    face_sheets = models.FloatField("Листов на лицевые", blank=True, null=True, editable=False)
    stripe_sheets = models.FloatField("Листов на полосы", blank=True, null=True, editable=False)
    oracal_pm_1m = models.FloatField("П/м оракал 1 метр ширина", blank=True, null=True, editable=False)
    oracal_pm_1_2m = models.FloatField("П/м оракал 1.2 метра ширина", blank=True, null=True, editable=False)

    def __str__(self):
        return f"КП для {self.client_name} от {self.created_at:%Y-%m-%d}"

    def save(self, *args, **kwargs):
        if "пвх" not in self.materials:
            self.width_pvh = None
            self.height_pvh = None
        if "алюк" not in self.materials:
            self.width_alyuk = None
            self.height_alyuk = None
        self.area_pvh = round((self.width_pvh or 0) * (self.height_pvh or 0), 2) if "пвх" in self.materials else None
        self.area_alyuk = round((self.width_alyuk or 0) * (self.height_alyuk or 0),
                                2) if "алюк" in self.materials else None
        self.area = round((self.area_pvh or 0) + (self.area_alyuk or 0), 2)

        super().save(*args, **kwargs)
        self._calculate_totals()
        super().save(update_fields=[
            "total_letters", "total_diodes", "total_glue", "total_acrylic",
            "total_pvc", "total_stripes", "total_oracal_m2", "total_wire_m",
            "total_power_watt", "sheets", "profile", "silicone", "oracal",
            "total_back", "face_sheets", "stripe_sheets",
            "oracal_pm_1m", "oracal_pm_1_2m",
        ])

    def _calculate_totals(self):
        blocks = self.blocks.all()
        self.total_letters = sum(b.letter_count for b in blocks)
        self.total_diodes = sum(b.diodes for b in blocks if b.diodes)
        self.total_glue = sum(b.glue for b in blocks if b.glue)
        self.total_acrylic = sum(b.acrylic for b in blocks if b.acrylic)
        self.total_pvc = sum(b.pvc for b in blocks if b.pvc)
        self.total_stripes = sum(b.stripes for b in blocks if b.stripes)
        self.total_oracal_m2 = sum(b.oracal_m2 for b in blocks if b.oracal_m2)
        self.total_wire_m = sum(b.wire_m for b in blocks if b.wire_m)
        self.total_power_watt = sum(b.power_watt for b in blocks if b.power_watt)
        self.sheets = round(
            (math.ceil(self.width_pvh / 2.4) if self.width_pvh else 0) +
            (math.ceil(self.width_alyuk / 2.3) if self.width_alyuk else 0),
            2
        )
        self.profile = round(math.ceil((self.sheets * 8.1)/5.8), 2)
        self.silicone = round(self.sheets * 2, 2)
        self.oracal = round(math.ceil(self.width_pvh / 2.4) * 2.7, 2) if self.width_pvh else 0
        self.total_back = round(self.sheets, 2) if self.sheets else 0
        self.face_sheets = round(self.total_acrylic / 2.8, 3) if self.total_acrylic else 0
        self.stripe_sheets = round(self.total_stripes * 0.031, 2)
        self.oracal_pm_1m = round(self.total_oracal_m2 / 1, 2) if self.total_oracal_m2 else 0
        self.oracal_pm_1_2m = round(self.total_oracal_m2 / 1.2, 2) if self.total_oracal_m2 else 0
        super().save()


class SignBlock(models.Model):
    """
    Model of different types of sign blocks, including different types of letters size and its amount
    """
    FORMULAS = {
        "15x15": {"diodes": 6, "glue": 0.25, "acrylic": 0.03, "pvc": 0.03, "stripes": 0.79, "oracal_k": 0.125,
                  "wire": 0.5, "watt_per_diode": 0.5},

        "20x20": {"diodes": 7, "glue": 0.325, "acrylic": 0.052, "pvc": 0.052, "stripes": 1.05, "oracal_k": 0.125,
                  "wire": 0.3, "watt_per_diode": 0.5},

        "25x25": {"diodes": 18, "glue": 0.35, "acrylic": 0.111, "pvc": 0.111, "stripes": 1.32, "oracal_k": 0.125,
                  "wire": 0.4, "watt_per_diode": 0.5},

        "35x35": {"diodes": 20, "glue": 0.4, "acrylic": 0.14, "pvc": 0.14, "stripes": 1.57, "oracal_k": 0.125,
                  "wire": 0.45, "watt_per_diode": 0.5},

        "40x40": {"diodes": 25, "glue": 0.4, "acrylic": 0.14, "pvc": 0.14, "stripes": 1.57, "oracal_k": 0.125,
                  "wire": 0.45, "watt_per_diode": 0.5},

        "50x50": {"diodes": 32, "glue": 0.45, "acrylic": 0.3, "pvc": 0.3, "stripes": 2.62, "oracal_k": 0.125,
                  "wire": 0.5, "watt_per_diode": 0.5},

        "60x60": {"diodes": 48, "glue": 0.5, "acrylic": 0.406, "pvc": 0.406, "stripes": 3.15, "oracal_k": 0.125,
                  "wire": 0.5, "watt_per_diode": 0.5},

        "70x70": {"diodes": 63, "glue": 0.7, "acrylic": 0.602, "pvc": 0.602, "stripes": 3.67, "oracal_k": 0.125,
                  "wire": 1.0, "watt_per_diode": 0.86},

        "80x80": {"diodes": 90, "glue": 0.8, "acrylic": 0.72, "pvc": 0.72, "stripes": 4.2, "oracal_k": 0.125,
                  "wire": 1.2, "watt_per_diode": 0.86},

        "90x90": {"diodes": 108, "glue": 1.25, "acrylic": 0.99, "pvc": 0.99, "stripes": 4.72, "oracal_k": 0.125,
                  "wire": 1.2, "watt_per_diode": 0.86},

        "100x100": {"diodes": 110, "glue": 1.5, "acrylic": 1.2, "pvc": 1.2, "stripes": 5.25, "oracal_k": 0.145,
                    "wire": 1.5, "watt_per_diode": 0.86},

        "110x110": {"diodes": 145, "glue": 1.5, "acrylic": 1.43, "pvc": 1.43, "stripes": 5.77, "oracal_k": 0.145,
                    "wire": 1.5, "watt_per_diode": 0.86},

        "120x120": {"diodes": 149, "glue": 1.6, "acrylic": 1.68, "pvc": 1.68, "stripes": 6.6, "oracal_k": 0.145,
                    "wire": 1.6, "watt_per_diode": 0.86},

        "130x130": {"diodes": 211, "glue": 1.8, "acrylic": 2.08, "pvc": 2.08, "stripes": 6.82, "oracal_k": 0.145,
                    "wire": 2.0, "watt_per_diode": 0.86},

        "140x140": {"diodes": 232, "glue": 2.0, "acrylic": 2.38, "pvc": 2.38, "stripes": 7.35, "oracal_k": 0.145,
                    "wire": 2.0, "watt_per_diode": 0.86},

        "150x150": {"diodes": 245, "glue": 2.0, "acrylic": 2.7, "pvc": 2.7, "stripes": 7.87, "oracal_k": 0.145,
                    "wire": 2.3, "watt_per_diode": 0.86},

        "160x160": {"diodes": 315, "glue": 2.2, "acrylic": 3.04, "pvc": 3.04, "stripes": 7.87, "oracal_k": 0.145,
                    "wire": 2.3, "watt_per_diode": 0.86},

        "170x170": {"diodes": 325, "glue": 2.5, "acrylic": 3.4, "pvc": 3.4, "stripes": 7.87, "oracal_k": 0.145,
                    "wire": 2.3, "watt_per_diode": 0.86},

        "180x180": {"diodes": 372, "glue": 3.0, "acrylic": 3.96, "pvc": 3.96, "stripes": 7.87, "oracal_k": 0.145,
                    "wire": 2.3, "watt_per_diode": 0.86},

        "190x190": {"diodes": 463, "glue": 3.5, "acrylic": 4.37, "pvc": 4.37, "stripes": 7.87, "oracal_k": 0.145,
                    "wire": 3.0, "watt_per_diode": 0.86},

        "200x200": {"diodes": 498, "glue": 4.0, "acrylic": 4.8, "pvc": 4.8, "stripes": 10.5, "oracal_k": 0.145,
                    "wire": 3.5, "watt_per_diode": 0.86},

    }

    LETTER_SIZE_CHOICES = [
        ("15x15", "15×15 см"),
        ("20x20", "20×20 см"),
        ("25x25", "25×25 см"),
        ("35x35", "35×35 см"),
        ("40x40", "40×40 см"),
        ("50x50", "50×50 см"),
        ("60x60", "60×60 см"),
        ("70x70", "70×70 см"),
        ("80x80", "80×80 см"),
        ("90x90", "90×90 см"),
        ("100x100", "100×100 см"),
        ("110x110", "110×110 см"),
        ("120x120", "120×120 см"),
        ("130x130", "130×130 см"),
        ("140x140", "140×140 см"),
        ("150x150", "150×150 см"),
        ("160x160", "160×160 см"),
        ("170x170", "170×170 см"),
        ("180x180", "180×180 см"),
        ("190x190", "190×190 см"),
        ("200x200", "200×200 см"),
    ]

    quote = models.ForeignKey(Quote, on_delete=models.CASCADE, related_name="blocks")
    letter_size = models.CharField("Размер букв", max_length=20, choices=LETTER_SIZE_CHOICES)
    letter_count = models.PositiveIntegerField("Кол-во букв")

    diodes = models.FloatField("Кол-во диодов", editable=False, null=True)
    glue = models.FloatField("Кол-во клея", editable=False, null=True)
    acrylic = models.FloatField("Акрил м²", editable=False, null=True)
    pvc = models.FloatField("ПВХ м²", editable=False, null=True)
    stripes = models.FloatField("Кол-во полос", editable=False, null=True)
    oracal_m2 = models.FloatField("Оракал м²", editable=False, null=True)
    wire_m = models.FloatField("Провода м.п.", editable=False, null=True)
    power_watt = models.FloatField("Вт", editable=False, null=True)

    def save(self, *args, **kwargs):
        self._calculate()
        super().save(*args, **kwargs)

    def _calculate(self):
        D = self.letter_count
        f = self.FORMULAS.get(self.letter_size)
        if not f:
            return
        self.diodes = round(D * f["diodes"], 2)
        self.glue = round(D * f["glue"], 2)
        self.acrylic = round(D * f["acrylic"], 3)
        self.pvc = round(D * f["pvc"], 3)
        self.stripes = round(D * f["stripes"], 2)
        self.oracal_m2 = round(self.stripes * f["oracal_k"], 2)
        self.wire_m = round(D * f["wire"], 2)
        self.power_watt = round(self.diodes * f["watt_per_diode"], 2)


SIGN_TYPES = [
    # База
    ("pseudo_pvc", "Псевдообъем ПВХ 8мм"),
    ("pseudo_pvc_acrylic", "Псевдообъем 8мм + акрил 3мм"),
    ("pseudo_15_30mm", "Псевдообъем 15-30мм крашенный"),
    ("volume_nonsvet", "Объемная несветовая вывеска"),
    ("light_face", "Световое лицо"),
    ("3d_letters", "3D буквы"),
    ("light_acrylic_20mm", "Световая из акрила 20мм"),
    ("backlight_contour", "Контражур подсветка"),
    ("steel_letters", "Буквы из нержавейки"),
    ("steel_letters_light", "Буквы из нержавейки световые"),

    # Облачко ПВХ
    ("pvc_cloud_w_light_face", "Облачко + Буквы световые"),
    ("pvc_cloud_w_3d_letters", "Облачко ПВХ + Буквы 3D"),

    # ПВХ Подложка
    ("pvc_base_w_light_face", "Подложка ПВХ + Буквы световые"),
    ("pvc_base_w_3d_letters", "Подложка ПВХ + Буквы 3D"),
    ("pvc_base_w_backlight_contour", "Подложка ПВХ + Буквы контражур"),
    ("pvc_base_w_steel_letters", "Подложка ПВХ + Буквы нержавейка"),
    ("pvc_base_w_steel_letters_light", "Подложка ПВХ + Буквы + Контражур"),

    # Алюкобонд подложка
    ("alucobond_w_light_face", "Подложка алюкобонд + Буквы световые"),
    ("alucobond_w_3d_letters", "Подложка алюкобонд + Буквы 3D"),
    ("alucobond_w_backlight_contour", "Подложка алюкобонд + Буквы контражур"),
    ("alucobond_w_steel_letters", "Подложка алюкобонд + Буквы нержавейка"),
    ("alucobond_w_steel_letters_light", "Подложка алюкобонд + Буквы + Контражур"),

    # Металлорамка
    ("metal_frame_w_light_face", "Металлорамка + Буквы световые"),
    ("metal_frame_w_3d_letters", "Металлорамка + Буквы 3D"),
    ("metal_frame_w_backlight_contour", "Металлорамка + Буквы контражур"),
    ("metal_frame_w_steel_letters", "Металлорамка + Буквы нержавейка"),
    ("metal_frame_w_steel_letters_light", "Металлорамка + Буквы + Контражур"),

    # Лайтбоксы
    ("banner_lightbox", "Баннерный лайтбокс"),
    ("acrylic_lightbox", "Акрил Лайтбокс"),
    ("acrylic_lightbox_3mm", "Акрил Лайтбокс + Инкрустация 3мм."),
    ("acrylic_lightbox_8mm", "Акрил Лайтбокс + Инкрустация 8мм."),
    ("acrylic_lightbox_8mm_3mm", "Акрил Лайтбокс + Инкрустация 8мм.+3мм."),
    ("alucobond_lightbox_3mm", "Алюкобонд + Инкрустация 3мм. акрил"),
    ("alucobond_lightbox_8mm", "Алюкобонд + Инкрустация 8мм. акрил"),
    ("alucobond_lightbox_8mm_3mm", "Алюкобонд + Инкрустация 8мм.+3мм. акрил"),
]

class Variant(models.Model):
    quote = models.ForeignKey(Quote, related_name="variants", on_delete=models.CASCADE)
    type_code = models.CharField(max_length=100, choices=SIGN_TYPES)
    use_in_offer = models.BooleanField(default=True)
    margin_pct = models.PositiveSmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("quote", "type_code")

    @property
    def subtotal(self):
        return sum(item.subtotal for item in self.items.all())

class VariantItem(models.Model):
    variant = models.ForeignKey(Variant, related_name="items", on_delete=models.CASCADE)
    product = models.ForeignKey(Product, null=True, blank=True, on_delete=models.SET_NULL)
    name = models.CharField(max_length=255)
    qty = models.DecimalField(max_digits=10, decimal_places=3)
    unit = models.CharField(max_length=10, default="шт")
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, editable=False)

    def save(self, *a, **kw):
        if self.unit_price is None and self.product:
            self.unit_price = self.product.final_price
        self.subtotal = round(self.qty * self.unit_price, 2)
        super().save(*a, **kw)

