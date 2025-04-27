from decimal import Decimal
from parser_and_calculator.models import Variant, VariantItem, Product, Quote


PRODUCT_NAME_MAPPING = {
    "autoheight": "Автовышка",
    "transport": "Транспорт",
    "metises": "Метизы",
    "laser_metal": "Лазер метал",
    "laser_cutting_sheet": "Лазер распил листа",
    "multiam_cutting": "Мультиам распил",
    "stabilizer_8kw": "Стабилизатор 8 кВт",
    "stabilizer_5kw": "Стабилизатор 5 кВт",
    "stabilizer_3kw": "Стабилизатор 3 кВт",
    "photorelay": "Фоторэле",
    "metal_20x40x3": "Металл 20*40*3мм",
    "metal_20x20x2": "Металл 20*20*2мм",
    "lacquer_acrylic": "Лак Акриловый",
    "paint_acrylic": "Краска Акриловая",
    "primer_auto": "Грунтовка автомобильная",
    "paint_metal": "Краска для металла",
    "primer_metal": "Грунтовка для металла",
    "glue_201": "Клей 201",
    "uv_print": "Уф печать",
    "uv_print_oracal": "Уф печать оракал",
    "banner_340g": "Баннер 340 гр печать",
    "spacers_transparent": "Дистонционные держатели прозрачные",
    "stainless_1_5mm_304": "Нержавеющая сталь 1.5 мм 304",
    "stainless_1mm_304": "Нержавеющая сталь 1 мм 304",
    "stainless_0_75mm_304": "Нержавеющая сталь 0,75 мм 304",
    "tubing_25x50": "Тюбинг 25*50",
    "silicone": "Силикон",
    "glue_two_component": "Двух компонентный клей",
    "tape_sheet_roll": "Скотч рулонный листовой",
    "tape_2x50_black": "Скотч рулонный 2*50 черный",
    "wires": "Провода",
    "led_module_9dots_pro": "Светодиодный модуль 9 точек Pro",
    "led_module_edge_2_4": "Светодиодный модуль торцевой 2,4",
    "led_strip_5050": "Светодиодная лента 50*50",
    "led_module_0_72_pro": "Светодиодный модуль 0,72 pro",
    "transformer_300w": "Трансформатор Т-300W",
    "transformer_250w": "Трансформатор Т-250W",
    "transformer_200w": "Трансформатор Т-200W",
    "transformer_150w": "Трансформатор Т-150W",
    "transformer_100w": "Трансформатор Т-100W",
    "transformer_80w": "Трансформатор Т-80W",
    "transformer_60w": "Трансформатор Т-60W",
    "oracal_8100": "Оракал серия 8100",
    "oracal_641": "Оракал серия 641",
    "mdf_22": "Мдф 22",
    "acrylic_20mm": "Акрил 20мм",
    "acrylic_15mm": "Акрил 15мм",
    "acrylic_8mm": "Акрил 8мм",
    "acrylic_5mm": "Акрил 5мм",
    "acrylic_4mm": "Акрил 4мм",
    "acrylic_3mm": "Акрил 3мм",
    "alyukobond_021": "Алюкобонд 0,21",
    "alyukobond_018": "Алюкобонд 0,18",
    "pvc_30mm": "ПВХ 30мм",
    "pvc_20mm": "ПВХ 20мм",
    "pvc_15mm": "ПВХ 15мм",
    "pvc_10mm": "ПВХ 10мм",
    "pvc_8mm": "ПВХ 8мм",
    "pvc_5mm": "ПВХ 5мм",
    "pvc_3mm": "ПВХ 3мм",
    "acrylic_3mm_stripes": "Акрил 3мм"
}


PSEUDO_PVC_MAP = {
    "pvc_8mm": lambda q: q.total_pvc / Decimal("2.8"),
    "silicone": lambda q, items: items["pvc_8mm"] * Decimal("0.5"),
    "oracal_641": lambda q, items: items["pvc_8mm"] * Decimal("2.8"),
    "multiam_cutting": lambda q, items: items["pvc_8mm"],
    "metises": lambda q, items: Decimal("0.5"),
    "autoheight": lambda q: q.special_technique,
    "transport": lambda q, items: Decimal("1.0"),
    "crafting_relative_to_materials_cost": lambda q, items: Decimal("65.0"),
    "installation": lambda q, items: Decimal("20.0"),
}

PSEUDO_PVC_WITH_ACRYLIC_MAP = {
    "pvc_5mm": lambda q: q.total_pvc / Decimal("2.8"),
    "silicone": lambda q, items: items["pvc_8mm"] * Decimal("0.5"),
    "acrylic_3mm": lambda q: q.total_acrylic,
    "tape_sheet_roll": lambda q, items: items["acrylic_3mm"],
    "multiam_cutting": lambda q, items: items["pvc_8mm"] + items["acrylic_3mm"],
    "uv_print": lambda q, items: q.ultrafiolet_letters_print * q.total_acrylic,
    "metises": lambda q, items: Decimal("0.5"),
    "autoheight": lambda q: q.special_technique,
    "transport": lambda q, items: Decimal("1.0"),
    "crafting_relative_to_materials_cost": lambda q, items: Decimal("65.0"),
    "installation": lambda q, items: Decimal("20"),
}

PSEUDO_15_30MM_COLORED = {
    "mdf_22": lambda q: q.total_pvc / Decimal("2.8"),
    "paint_acrylic": lambda q, items: (q.total_acrylic + (q.total_stripes / 25) + q.total_pvc) / Decimal("5.0"),
    "primer_auto": lambda q, items: (q.total_acrylic + (q.total_stripes / 25) + q.total_pvc) / Decimal("5.0"),
    "lacquer_acrylic": lambda q, items: (q.total_acrylic + (q.total_stripes / 25) + q.total_pvc) / Decimal("5.0"),
    "tape_sheet_roll": lambda q, items: items["paint_acrylic"],
    "multiam_cutting": lambda q, items: items["mdf_22"] + items["paint_acrylic"],
    "metises": lambda q, items: Decimal("0.5"),
    "autoheight": lambda q: q.special_technique,
    "transport": lambda q, items: Decimal("1.0"),
    "crafting_relative_to_materials_cost": lambda q, items: Decimal("65.0"),
    "installation": lambda q, items: Decimal("20"),
}

VOLUMETIC_NONLIGHT = {
    "acrylic_3mm": lambda q: q.total_acrylic / Decimal("2.8"),
    "pvc_8mm": lambda q: q.total_pvc / Decimal("2.8"),
    "pvc_5mm": lambda q: q.total_stripes / Decimal("25.0"),
    "oracal_641": lambda q, items: items["pvc_5mm"] * Decimal("3.0"),
    "glue_201": lambda q, items: q.total_glue,
    "uv_print": lambda q, items: q.ultrafiolet_letters_print * q.total_acrylic,
    "multiam_cutting": lambda q, items: items["pvc_8mm"] + items["acrylic_3mm"] + items["pvc_5mm"],
    "metises": lambda q, items: Decimal("1.0"),
    "autoheight": lambda q: q.special_technique,
    "transport": lambda q, items: Decimal("1.0"),
    "crafting_relative_to_materials_cost": lambda q, items: Decimal("65.0"),
    "installation": lambda q, items: Decimal("20"),
}

LIGHT_FACE = {
    "acrylic_3mm": lambda q: q.total_acrylic / Decimal("2.8"),
    "pvc_8mm": lambda q: q.total_pvc / Decimal("2.8"),
    "pvc_5mm": lambda q: q.total_stripes / Decimal("25.0"),
    "led_module_0_72_pro": lambda q: q.total_diodes,
    "transformer_250w": lambda q, items: items["led_module_0_72_pro"] / Decimal("290.0"),
    "oracal_641": lambda q, items: items["pvc_5mm"] * Decimal("3.0"),
    "glue_201": lambda q, items: q.total_glue,
    "wires": lambda q: q.total_wire_m,
    "uv_print": lambda q, items: q.ultrafiolet_letters_print * q.total_acrylic,
    "multiam_cutting": lambda q, items: items["pvc_8mm"] + items["acrylic_3mm"] + items["pvc_5mm"],
    "metises": lambda q, items: Decimal("1.0"),
    "photorelay": lambda q: Decimal("1.0"),
    "autoheight": lambda q: q.special_technique,
    "transport": lambda q, items: Decimal("1.0"),
    "crafting_relative_to_materials_cost": lambda q, items: Decimal("65.0"),
    "installation": lambda q, items: Decimal("20"),
}




THREEDIMENSION_LETTERS = {
    "acrylic_3mm": lambda q: q.total_acrylic / Decimal("2.8"),
    "acrylic_3mm_stripes": lambda q: q.total_stripes / Decimal("25.0"),
    "pvc_8mm": lambda q: q.total_pvc / Decimal("2.8"),
    "led_module_0_72_pro": lambda q: q.total_diodes,
    "transformer_250w": lambda q, items: items["led_module_0_72_pro"] / Decimal("290.0"),
    "oracal_641": lambda q, items: items["acrylic_3mm_stripes"] * Decimal("3.0"),
    "glue_201": lambda q, items: q.total_glue,
    "wires": lambda q: q.total_wire_m,
    "uv_print": lambda q, items: q.ultrafiolet_letters_print * q.total_acrylic,
    "multiam_cutting": lambda q, items: items["pvc_8mm"] + items["acrylic_3mm"] + items["pvc_5mm"],
    "metises": lambda q, items: Decimal("1.0"),
    "photorelay": lambda q: Decimal("1.0"),
    "autoheight": lambda q: q.special_technique,
    "transport": lambda q, items: Decimal("1.0"),
    "crafting_relative_to_materials_cost": lambda q, items: Decimal("65.0"),
    "installation": lambda q, items: Decimal("20"),
}

# UP IS DONE


VARIANT_CALCS = {
    "pseudo_pvc": PSEUDO_PVC_MAP,
    "pseudo_pvc_acrylic": PSEUDO_PVC_WITH_ACRYLIC_MAP,
    "pseudo_15_30mm": PSEUDO_15_30MM_COLORED,
    "volume_nonsvet": VOLUMETIC_NONLIGHT,
    "light_face": LIGHT_FACE,
    "3d_letters": THREEDIMENSION_LETTERS,
    #"light_acrylic_20mm": LIGHT_ACRYLIC_20MM,
    #"backlight_contour": BACLIGHT_COUNTOUR,
    #"steel_letters": STEEL_LETTERS,
    #"steel_letters_light": STEEL_LETTERS_LIGHT
}


def find_product(key: str) -> Product:
    prod_name = PRODUCT_NAME_MAPPING.get(key)
    if not prod_name:
        raise ValueError(f"Нет маппинга для ключа '{key}'")

    prod = Product.objects.filter(name__icontains=prod_name).first()
    if not prod:
        raise ValueError(f"Товар '{prod_name}' не найден в базе для ключа '{key}'")

    return prod


def apply_margin(variant: Variant, margin_pct: int):
    """
    Counting additional margin percents
    """
    coef = Decimal(1) + (Decimal(margin_pct) / Decimal(100))
    for item in variant.items.all():
        item.unit_price = round(item.unit_price * coef, 2)
        item.subtotal   = round(item.qty * item.unit_price, 2)
        item.save(update_fields=["unit_price", "subtotal"])


def build_variant(quote: Quote, type_code: str) -> Variant:
    v, _ = Variant.objects.get_or_create(quote=quote, type_code=type_code)
    calculators = VARIANT_CALCS[type_code]

    qty_cache = {}
    items_created = {}

    # --- Step 1: simple materials, except special values
    for key, fn in calculators.items():
        if key in ["crafting_relative_to_materials_cost", "installation"]:
            continue

        qty = fn(quote, qty_cache)
        qty_cache[key] = qty

        prod = find_product(key)
        unit_price = Decimal(prod.final_price)

        item, _ = VariantItem.objects.update_or_create(
            variant=v,
            name=PRODUCT_NAME_MAPPING[key],
            defaults=dict(product=prod, qty=qty, unit="шт", unit_price=unit_price)
        )
        items_created[key] = item

    # --- Step 2: summarizing materials sum
    material_sum = sum(item.subtotal for item in items_created.values())

    # --- Step 3: non-material prices, i.e. crafting and installing
    if "crafting_relative_to_materials_cost" in calculators:
        crafting_pct = calculators["crafting_relative_to_materials_cost"](quote, qty_cache)
        crafting_price = material_sum * (crafting_pct / Decimal("100"))
        VariantItem.objects.update_or_create(
            variant=v, name="Изготовление",
            defaults=dict(
                product=None,
                qty=1,
                unit="усл.",
                unit_price=round(crafting_price, 2),
            )
        )

    if "installation" in calculators:
        installation_pct = calculators["installation"](quote, qty_cache)
        installation_price = material_sum * (installation_pct / Decimal("100"))
        VariantItem.objects.update_or_create(
            variant=v, name="Монтаж",
            defaults=dict(
                product=None,
                qty=1,
                unit="усл.",
                unit_price=round(installation_price, 2),
            )
        )

    # --- Step 4: Additional margin
    if v.margin_pct:
        apply_margin(v, v.margin_pct)

    return v
