from decimal import Decimal
from collections import defaultdict
from parser_and_calculator.models import Variant, VariantItem, Product, Quote
from parser_and_calculator.constants import SIGN_NAMES

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
    "uv_print": "УФ печать",
    "uv_print_oracal": "Уф печать оракал",
    "banner_340g": "Баннер 340 гр печать",
    "spacers_transparent": "Дистанционные держатели прозрачные",
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
    "transformer_250w": "Трансформатор  Т-250W",
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
    "acrylic_3mm_stripes": "Акрил 3мм полоски",
    "uv_print_base": "УФ печать Подложка",
}


PSEUDO_PVC_MAP = {
    "pvc_8mm": lambda q, items: Decimal(str(q.total_pvc)) / Decimal("2.8"),
    "silicone": lambda q, items: items["pvc_8mm"] * Decimal("0.5"),
    "oracal_641": lambda q, items: items["pvc_8mm"] * Decimal("2.8"),
    "multiam_cutting": lambda q, items: items["pvc_8mm"],
    "metises": lambda q, items: Decimal("0.5"),
    "autoheight": lambda q, items: Decimal(str(q.special_technique)),
    "transport": lambda q, items: Decimal("1.0"),
    "crafting_relative_to_materials_cost": lambda q, items: Decimal("65"),
    "installation": lambda q, items: Decimal("33"),
}

PSEUDO_PVC_ACRYLIC = {
    "pvc_8mm": lambda q, items: Decimal(str(q.total_pvc)) / Decimal("2.8"),
    "silicone": lambda q, items: items["pvc_8mm"] * Decimal("0.5"),
    "acrylic_3mm": lambda q, items: Decimal(str(q.face_sheets)),
    "tape_sheet_roll": lambda q, items: items["acrylic_3mm"],
    "multiam_cutting": lambda q, items: items["pvc_8mm"] + items["acrylic_3mm"],
    "uv_print_base": lambda q, items: Decimal(str(q.ultrafiolet_letters_print)) * Decimal(str(q.total_acrylic)),
    "metises": lambda q, items: Decimal("0.5"),
    "autoheight": lambda q, items: Decimal(str(q.special_technique)),
    "transport": lambda q, items: Decimal("1.0"),
    "crafting_relative_to_materials_cost": lambda q, items: Decimal("65"),
    "installation": lambda q, items: Decimal("33"),
}

PSEUDO_15_30MM_COLORED = {
    "mdf_22": lambda q, items: Decimal(str(q.total_pvc)) / Decimal("2.8"),
    "silicone": lambda q, items: items["mdf_22"] * Decimal("0.5"),
    "paint_acrylic": lambda q, items: (
            (Decimal(str(q.total_acrylic))
             + (Decimal(str(q.total_stripes)) / 25)
             + Decimal(str(q.total_pvc))) / Decimal("5.0")
    ),
    "primer_auto": lambda q, items: (
            (Decimal(str(q.total_acrylic))
             + (Decimal(str(q.total_stripes)) / 25)
             + Decimal(str(q.total_pvc))) / Decimal("5.0")
    ),
    "lacquer_acrylic": lambda q, items: (
            (Decimal(str(q.total_acrylic))
             + (Decimal(str(q.total_stripes)) / 25)
             + Decimal(str(q.total_pvc))) / Decimal("5.0")
    ),
    "tape_sheet_roll": lambda q, items: items["paint_acrylic"],
    "multiam_cutting": lambda q, items: items["mdf_22"] + items["paint_acrylic"],
    "metises": lambda q, items: Decimal("0.5"),
    "autoheight": lambda q, items: Decimal(str(q.special_technique)),
    "transport": lambda q, items: Decimal("1.0"),
    "crafting_relative_to_materials_cost": lambda q, items: Decimal("65.0"),
    "installation": lambda q, items: Decimal("33"),
}

VOLUMETIC_NONLIGHT = {
    "acrylic_3mm": lambda q, items: Decimal(str(q.total_acrylic)) / Decimal("2.8"),
    "pvc_8mm": lambda q, items: Decimal(str(q.total_pvc)) / Decimal("2.8"),
    "pvc_5mm": lambda q, items: Decimal(str(q.total_stripes)) / Decimal("25.0"),
    "oracal_641": lambda q, items: items["pvc_5mm"] * Decimal("3.0"),
    "glue_201": lambda q, items: Decimal(str(q.total_glue)),
    "uv_print_base": lambda q, items: Decimal(str(q.ultrafiolet_letters_print)) * Decimal(str(q.total_acrylic)),
    "multiam_cutting": lambda q, items: items["pvc_8mm"] + items["acrylic_3mm"] + items["pvc_5mm"],
    "metises": lambda q, items: Decimal("1.0"),
    "autoheight": lambda q, items: Decimal(str(q.special_technique)),
    "transport": lambda q, items: Decimal("1.0"),
    "crafting_relative_to_materials_cost": lambda q, items: Decimal("80"),
    "installation": lambda q, items: Decimal("36"),
}

LIGHT_FACE = {
    "acrylic_3mm": lambda q, items: Decimal(str(q.total_acrylic)) / Decimal("2.8"),
    "pvc_8mm": lambda q, items: Decimal(str(q.total_pvc)) / Decimal("2.8"),
    "pvc_5mm": lambda q, items: Decimal(str(q.total_stripes)) / Decimal("25"),
    "led_module_0_72_pro": lambda q, items: Decimal(str(q.total_diodes)),
    "transformer_250w": lambda q, items: items["led_module_0_72_pro"] / Decimal("290.0"),
    "oracal_641": lambda q, items: items["pvc_5mm"] * Decimal("3.0"),
    "glue_201": lambda q, items: Decimal(str(q.total_glue)),
    "wires": lambda q, items: Decimal(str(q.total_wire_m)),
    "uv_print_base": lambda q, items: Decimal(str(q.ultrafiolet_letters_print)) * Decimal(str(q.total_acrylic)),
    "multiam_cutting": lambda q, items: items["pvc_8mm"] + items["acrylic_3mm"] + items["pvc_5mm"],
    "metises": lambda q, items: Decimal("1.0"),
    "photorelay": lambda q, items: Decimal("1.0"),
    "autoheight": lambda q, items: Decimal(str(q.special_technique)),
    "transport": lambda q, items: Decimal("1.0"),
    "crafting_relative_to_materials_cost": lambda q, items: Decimal("65"),
    "installation": lambda q, items: Decimal("33"),
}

THREEDIMENSION_LETTERS = {
    "acrylic_3mm": lambda q, items: Decimal(str(q.total_acrylic)) / Decimal("2.8"),
    "acrylic_3mm_stripes": lambda q, items: Decimal(str(q.total_stripes)) / Decimal("25.0"),
    "pvc_8mm": lambda q, items: Decimal(str(q.total_pvc)) / Decimal("2.8"),
    "led_module_0_72_pro": lambda q, items: Decimal(str(q.total_diodes)),
    "transformer_250w": lambda q, items: items["led_module_0_72_pro"] / Decimal("290.0"),
    "oracal_641": lambda q, items: items["acrylic_3mm_stripes"] * Decimal("3.0"),
    "glue_201": lambda q, items: Decimal(str(q.total_glue)),
    "wires": lambda q, items: Decimal(str(q.total_wire_m)),
    "uv_print_base": lambda q, items: Decimal(str(q.ultrafiolet_letters_print)) * Decimal(str(q.total_acrylic)),
    "multiam_cutting": lambda q, items: items["pvc_8mm"] + items["acrylic_3mm"] + items["acrylic_3mm_stripes"],
    "metises": lambda q, items: Decimal("1.0"),
    "photorelay": lambda q, items: Decimal("1.0"),
    "autoheight": lambda q, items: Decimal(str(q.special_technique)),
    "transport": lambda q, items: Decimal("1.0"),
    "crafting_relative_to_materials_cost": lambda q, items: Decimal("65"),
    "installation": lambda q, items: Decimal("33"),
}

LIGHT_ACRYLIC_20MM = {
    "silicone": lambda q, items: Decimal("1.0"),
    "acrylic_20mm": lambda q, items: Decimal(str(q.total_acrylic)) / Decimal("2.8") * Decimal("0.8"),
    "led_strip_5050": lambda q, items: Decimal(str(q.total_stripes)) * Decimal("0.8"),
    "transformer_250w": lambda q, items: (items["led_strip_5050"] * Decimal("15.0")) / Decimal("250.0"),
    "glue_201": lambda q, items: Decimal(str(q.total_glue)) * Decimal("2.0"),
    "wires": lambda q, items: Decimal(str(q.total_wire_m)) * Decimal("2.0"),
    "uv_print_base": lambda q, items: Decimal(str(q.ultrafiolet_letters_print)) * Decimal(str(q.total_acrylic)),
    "multiam_cutting": lambda q, items: items["acrylic_20mm"] * Decimal("2.0"),
    "metises": lambda q, items: Decimal("1.0"),
    "photorelay": lambda q, items: Decimal("1.0"),
    "transport": lambda q, items: Decimal("1.0"),
    "autoheight": lambda q, items: Decimal(str(q.special_technique)),
    "crafting_relative_to_materials_cost": lambda q, items: Decimal("65"),
    "installation": lambda q, items: Decimal("33"),
}

BACLIGHT_COUNTOUR = {
    "acrylic_3mm": lambda q, items: (Decimal(str(q.total_acrylic)) / Decimal("2.8")) * Decimal("2.0"),
    "led_module_0_72_pro": lambda q, items: Decimal(str(q.total_diodes)),
    "transformer_250w": lambda q, items: items["led_module_0_72_pro"] / Decimal("290.0"),
    "uv_print_base": lambda q, items: Decimal(str(q.ultrafiolet_letters_print)) * Decimal(str(q.total_acrylic)),
    "glue_201": lambda q, items: Decimal(str(q.total_glue)),
    "wires": lambda q, items: Decimal(str(q.total_wire_m)),
    "spacers_transparent": lambda q, items: Decimal(str(q.total_letters)) * Decimal("5.0"),
    "multiam_cutting": lambda q, items: items["acrylic_3mm"],
    "metises": lambda q, items: Decimal("1.0"),
    "photorelay": lambda q, items: Decimal("1.0"),
    "transport": lambda q, items: Decimal("1.0"),
    "autoheight": lambda q, items: Decimal(str(q.special_technique)),
    "crafting_relative_to_materials_cost": lambda q, items: Decimal("65"),
    "installation": lambda q, items: Decimal("33"),
}

STEEL_LETTERS = {
    "stainless_0_75mm_304": lambda q, items: Decimal(str(q.total_acrylic)) / Decimal("2.8") + Decimal(str(q.total_stripes)) / Decimal("60.0"),
    "silicone": lambda q, items: Decimal(str(q.silicone)),
    "pvc_8mm": lambda q, items: Decimal(str(q.total_pvc)) / Decimal("2.8"),
    "pvc_5mm": lambda q, items: Decimal(str(q.total_stripes)) / Decimal("25"),
    "glue_201": lambda q, items: Decimal(str(q.total_glue)),
    "spacers_transparent": lambda q, items: Decimal(str(q.total_letters)) * Decimal("5.0"),
    "laser_metal": lambda q, items: Decimal(str(q.total_letters)) + Decimal(str(q.total_stripes)),
    "multiam_cutting": lambda q, items: items["stainless_0_75mm_304"] + items["pvc_8mm"] + items["pvc_5mm"],
    "metises": lambda q, items: Decimal("1.0"),
    "transport": lambda q, items: Decimal("1.0"),
    "autoheight": lambda q, items: Decimal(str(q.special_technique)),
    "crafting_relative_to_materials_cost": lambda q, items: Decimal("65"),
    "installation": lambda q, items: Decimal("33"),
}

STEEL_LETTERS_LIGHT = {
    "stainless_0_75mm_304": lambda q, items: Decimal(str(q.total_acrylic)) / Decimal("2.8") + Decimal(str(q.total_stripes)) / Decimal("60.0"),
    "silicone": lambda q, items: Decimal(str(q.silicone)),
    "acrylic_3mm": lambda q, items: Decimal(str(q.total_acrylic)) / Decimal("2.8"),
    "pvc_8mm": lambda q, items: Decimal(str(q.total_pvc)) / Decimal("2.8"),
    "pvc_5mm": lambda q, items: Decimal(str(q.total_stripes)) / Decimal("25"),
    "led_module_0_72_pro": lambda q, items: Decimal(str(q.total_diodes)),
    "transformer_250w": lambda q, items: items["led_module_0_72_pro"] / Decimal("290.0"),
    "glue_201": lambda q, items: Decimal(str(q.total_glue)),
    "wires": lambda q, items: Decimal(str(q.total_wire_m)),
    "spacers_transparent": lambda q, items: Decimal(str(q.total_letters)) * Decimal("5.0"),
    "laser_metal": lambda q, items: Decimal(str(q.total_letters)) + Decimal(str(q.total_stripes)),
    "multiam_cutting": lambda q, items: items["stainless_0_75mm_304"] + items["pvc_8mm"] + items["pvc_5mm"] + items["acrylic_3mm"],
    "metises": lambda q, items: Decimal("1.0"),
    "photorelay": lambda q, items: Decimal("1.0"),
    "transport": lambda q, items: Decimal("1.0"),
    "autoheight": lambda q, items: Decimal(str(q.special_technique)),
    "crafting_relative_to_materials_cost": lambda q, items: Decimal("65"),
    "installation": lambda q, items: Decimal("33"),
}

# Отдельные базы
PVC_CLOUD = {
    "pvc_10mm": lambda q, items: Decimal(str(q.sheets)),
    "oracal_641": lambda q, items: Decimal(str(q.oracal)),
    "multiam_cutting": lambda q, items: items["pvc_10mm"],
    "metises": lambda q, items: Decimal("0.5"),
    "transport": lambda q, items: Decimal("0.5"),
    "autoheight": lambda q, items: Decimal(str(q.special_technique)),
    "crafting_relative_to_materials_cost": lambda q, items: Decimal("65"),
    "installation": lambda q, items: Decimal("33"),
}

PVC_BASE = {
    "pvc_10mm": lambda q, items: Decimal(str(q.sheets)),
    "tubing_25x50": lambda q, items: Decimal(str(q.profile)),
    "silicone": lambda q, items: Decimal(str(q.silicone)),
    "oracal_641": lambda q, items: Decimal(str(q.oracal)),
    "uv_print_oracal": lambda q, items: Decimal(str(q.area)) * Decimal(str(q.ultrafiolet_base)),
    "multiam_cutting": lambda q, items: items["pvc_10mm"],
    "metises": lambda q, items: Decimal("1.0"),
    "transport": lambda q, items: Decimal("1.0"),
    "autoheight": lambda q, items: Decimal(str(q.special_technique)),
    "crafting_relative_to_materials_cost": lambda q, items: Decimal("65"),
    "installation": lambda q, items: Decimal("33"),
}

ALUCOBOND_BASE = {
    "alyukobond_021": lambda q, items: Decimal(str(q.sheets)),
    "tubing_25x50": lambda q, items: Decimal(str(q.profile)),
    "silicone": lambda q, items: Decimal(str(q.silicone)),
    "uv_print_base": lambda q, items: Decimal(str(q.area)) * Decimal(str(q.ultrafiolet_base)),
    "multiam_cutting": lambda q, items: items["alyukobond_021"],
    "metises": lambda q, items: Decimal("1.0"),
    "transport": lambda q, items: Decimal("1.0"),
    "autoheight": lambda q, items: Decimal(str(q.special_technique)),
    "crafting_relative_to_materials_cost": lambda q, items: Decimal("65"),
    "installation": lambda q, items: Decimal("33"),
}

METAL_FRAME = {
    "metal_20x40x3": lambda q, items: Decimal(str(q.profile)),
    "paint_metal": lambda q, items: items["metal_20x40x3"] / Decimal("5.0"),
    "primer_metal": lambda q, items: items["metal_20x40x3"] / Decimal("5.0"),
    "metises": lambda q, items: Decimal("0.5"),
    "transport": lambda q, items: Decimal("0.5"),
    "autoheight": lambda q, items: Decimal(str(q.special_technique)),
    "crafting_relative_to_materials_cost": lambda q, items: Decimal("65"),
    "installation": lambda q, items: Decimal("33"),
}


BANNER_LIGHTBOX = {
    "metal_20x40x3": lambda q, items: Decimal(str(q.width_pvh)) * Decimal("3") / Decimal("6"),
    "paint_metal": lambda q, items: items["metal_20x40x3"] / Decimal("5"),
    "primer_metal": lambda q, items: items["metal_20x40x3"] / Decimal("5"),
    "pvc_8mm": lambda q, items: Decimal(str(q.sheets)) * Decimal("1.5"),
    "banner_340g": lambda q, items: Decimal(str(q.width_pvh)) * Decimal(str(q.height_pvh)),
    "pvc_5mm": lambda q, items: Decimal(str(q.total_stripes)) / Decimal("25"),
    "led_module_9dots_pro": lambda q, items: items["banner_340g"] * Decimal("6"),
    "transformer_250w": lambda q, items: items["led_module_9dots_pro"] * Decimal("10.8") / Decimal("250"),
    "glue_201": lambda q, items: Decimal(str(q.total_glue)),
    "wires": lambda q, items: Decimal(str(q.total_wire_m)),
    "multiam_cutting": lambda q, items: items["pvc_8mm"],
    "metises": lambda q, items: Decimal("1.0"),
    "photorelay": lambda q, items: Decimal("1.0"),
    "transport": lambda q, items: Decimal("1.0"),
    "autoheight": lambda q, items: Decimal(str(q.special_technique)),
    "crafting_relative_to_materials_cost": lambda q, items: Decimal("65"),
    "installation": lambda q, items: Decimal("33"),
}



ACRYLIC_LIGHTBOX = {
    "metal_20x40x3": lambda q, items: Decimal(str(q.width_pvh)) * Decimal("3") / Decimal("6"),
    "paint_metal": lambda q, items: items["metal_20x40x3"] / Decimal("5"),
    "primer_metal": lambda q, items: items["metal_20x40x3"] / Decimal("5"),
    "pvc_8mm": lambda q, items: Decimal(str(q.sheets)) * Decimal("1.5"),
    "acrylic_3mm": lambda q, items: Decimal(str(q.sheets)),
    "pvc_5mm": lambda q, items: Decimal(str(q.total_stripes)) / Decimal("25") + Decimal(str(q.oracal)),
    "uv_print_base": lambda q, items: Decimal(str(q.area)) * Decimal(str(q.ultrafiolet_base)),
    "led_module_9dots_pro": lambda q, items: Decimal(str(q.width_pvh)) * Decimal(str(q.height_pvh)) * Decimal("6"),
    "transformer_250w": lambda q, items: items["led_module_9dots_pro"] * Decimal("10.8") / Decimal("250"),
    "glue_201": lambda q, items: Decimal(str(q.total_glue)),
    "wires": lambda q, items: Decimal(str(q.total_wire_m)),
    "multiam_cutting": lambda q, items: items["pvc_8mm"] + items["acrylic_3mm"],
    "metises": lambda q, items: Decimal("1.0"),
    "photorelay": lambda q, items: Decimal("1.0"),
    "transport": lambda q, items: Decimal("1.0"),
    "autoheight": lambda q, items: Decimal(str(q.special_technique)),
    "crafting_relative_to_materials_cost": lambda q, items: Decimal("65"),
    "installation": lambda q, items: Decimal("33"),
}


ACRYLIC_LIGHTBOX_3MM = {
    "metal_20x40x3": lambda q, items: Decimal(str(q.width_pvh)) * Decimal("3") / Decimal("6"),
    "paint_metal": lambda q, items: items["metal_20x40x3"] / Decimal("5"),
    "primer_metal": lambda q, items: items["metal_20x40x3"] / Decimal("5"),
    "pvc_8mm": lambda q, items: Decimal(str(q.sheets)) * Decimal("1.5"),
    "acrylic_4mm": lambda q, items: Decimal(str(q.sheets)) + Decimal(str(q.total_acrylic)) / Decimal("2.8"),
    "pvc_5mm": lambda q, items: Decimal(str(q.total_stripes)) / Decimal("25") + Decimal(str(q.oracal)),
    "uv_print_base": lambda q, items: Decimal(str(q.ultrafiolet_letters_print)) * Decimal(str(q.total_acrylic)),
    "led_module_9dots_pro": lambda q, items: Decimal(str(q.width_pvh)) * Decimal(str(q.height_pvh)) * Decimal("6"),
    "transformer_250w": lambda q, items: items["led_module_9dots_pro"] * Decimal("10.8") / Decimal("250"),
    "glue_201": lambda q, items: Decimal(str(q.total_glue)),
    "wires": lambda q, items: Decimal(str(q.total_wire_m)),
    "multiam_cutting": lambda q, items: items["pvc_8mm"],
    "metises": lambda q, items: Decimal("1.0"),
    "photorelay": lambda q, items: Decimal("1.0"),
    "transport": lambda q, items: Decimal("1.0"),
    "autoheight": lambda q, items: Decimal(str(q.special_technique)),
    "crafting_relative_to_materials_cost": lambda q, items: Decimal("65"),
    "installation": lambda q, items: Decimal("33"),
}

ACRYLIC_LIGHTBOX_8MM = {
    "metal_20x40x3": lambda q, items: Decimal(str(q.width_pvh)) * Decimal("3") / Decimal("6"),
    "paint_metal": lambda q, items: items["metal_20x40x3"] / Decimal("5"),
    "primer_metal": lambda q, items: items["metal_20x40x3"] / Decimal("5"),
    "pvc_8mm": lambda q, items: Decimal(str(q.sheets)) * Decimal("1.5"),
    "acrylic_4mm": lambda q, items: Decimal(str(q.sheets)),
    "acrylic_8mm": lambda q, items: Decimal(str(q.total_acrylic)) / Decimal("2.88"),
    "pvc_5mm": lambda q, items: Decimal(str(q.total_stripes)) / Decimal("25") + Decimal(str(q.oracal)),
    "uv_print_base": lambda q, items: Decimal(str(q.ultrafiolet_letters_print)) * Decimal(str(q.total_acrylic)),
    "led_module_9dots_pro": lambda q, items: Decimal(str(q.width_pvh)) * Decimal(str(q.height_pvh)) * Decimal("6"),
    "transformer_250w": lambda q, items: items["led_module_9dots_pro"] * Decimal("10.8") / Decimal("250"),
    "glue_201": lambda q, items: Decimal(str(q.total_glue)),
    "wires": lambda q, items: Decimal(str(q.total_wire_m)),
    "multiam_cutting": lambda q, items: items["pvc_8mm"],
    "metises": lambda q, items: Decimal("1.0"),
    "photorelay": lambda q, items: Decimal("1.0"),
    "transport": lambda q, items: Decimal("1.0"),
    "autoheight": lambda q, items: Decimal(str(q.special_technique)),
    "crafting_relative_to_materials_cost": lambda q, items: Decimal("65"),
    "installation": lambda q, items: Decimal("33"),
}

ACRYLIC_LIGHTBOX_8MM_3MM = {
    "metal_20x40x3": lambda q, items: Decimal(str(q.width_pvh)) * Decimal("3") / Decimal("6"),
    "paint_metal": lambda q, items: items["metal_20x40x3"] / Decimal("5"),
    "primer_metal": lambda q, items: items["metal_20x40x3"] / Decimal("5"),
    "pvc_8mm": lambda q, items: Decimal(str(q.sheets)) * Decimal("1.5"),
    "acrylic_4mm": lambda q, items: Decimal(str(q.sheets)),
    "acrylic_3mm": lambda q, items: Decimal(str(q.total_acrylic)) / Decimal("2.8"),
    "acrylic_8mm": lambda q, items: Decimal(str(q.total_acrylic)) / Decimal("2.88"),
    "pvc_5mm": lambda q, items: Decimal(str(q.total_acrylic)) / Decimal("2.88") * Decimal("1.5"),
    "uv_print_base": lambda q, items: Decimal(str(q.ultrafiolet_letters_print)) * Decimal(str(q.total_acrylic)),
    "led_module_9dots_pro": lambda q, items: Decimal(str(q.width_pvh)) * Decimal(str(q.height_pvh)) * Decimal("6"),
    "transformer_250w": lambda q, items: items["led_module_9dots_pro"] * Decimal("10.8") / Decimal("250"),
    "glue_201": lambda q, items: Decimal(str(q.total_glue)) * Decimal("2"),
    "wires": lambda q, items: Decimal(str(q.total_wire_m)) * Decimal("2"),
    "multiam_cutting": lambda q, items: items["pvc_8mm"],
    "metises": lambda q, items: Decimal("1.0"),
    "photorelay": lambda q, items: Decimal("1.0"),
    "transport": lambda q, items: Decimal("1.0"),
    "autoheight": lambda q, items: Decimal(str(q.special_technique)),
    "crafting_relative_to_materials_cost": lambda q, items: Decimal("65"),
    "installation": lambda q, items: Decimal("33"),
}

ALUCOBOND_LIGHTBOX_3MM = {
    "alyukobond_021": lambda q, items: Decimal(str(q.sheets)),
    "tubing_25x50": lambda q, items: Decimal(str(q.profile)),
    "silicone": lambda q, items: Decimal(str(q.silicone)),
    "pvc_8mm": lambda q, items: Decimal(str(q.sheets)) * Decimal("1.5"),
    "acrylic_3mm": lambda q, items: Decimal(str(q.sheets)) + Decimal(str(q.total_acrylic)) / Decimal("2.8"),
    "pvc_5mm": lambda q, items: Decimal(str(q.total_acrylic)) / Decimal("2.88"),
    "uv_print": lambda q, items: Decimal(str(q.area)) * Decimal(str(q.ultrafiolet_base)),
    "uv_print_base": lambda q, items: Decimal(str(q.ultrafiolet_letters_print)) * Decimal(str(q.total_acrylic)),
    "led_module_0_72_pro": lambda q, items: Decimal(str(q.total_diodes)),
    "transformer_250w": lambda q, items: items["led_module_0_72_pro"] * Decimal("0.86") / Decimal("250"),
    "glue_201": lambda q, items: Decimal(str(q.total_glue)) * Decimal("2"),
    "wires": lambda q, items: Decimal(str(q.total_wire_m)),
    "multiam_cutting": lambda q, items: items["pvc_8mm"],
    "metises": lambda q, items: Decimal("1.0"),
    "photorelay": lambda q, items: Decimal("1.0"),
    "transport": lambda q, items: Decimal("1.0"),
    "autoheight": lambda q, items: Decimal(str(q.special_technique)),
    "crafting_relative_to_materials_cost": lambda q, items: Decimal("65"),
    "installation": lambda q, items: Decimal("33"),
}

ALUCOBOND_LIGHTBOX_8MM = {
    "alyukobond_021": lambda q, items: Decimal(str(q.sheets)),
    "tubing_25x50": lambda q, items: Decimal(str(q.profile)),
    "silicone": lambda q, items: Decimal(str(q.silicone)),
    "pvc_8mm": lambda q, items: Decimal(str(q.sheets)) * Decimal("1.5"),
    "acrylic_8mm": lambda q, items: Decimal(str(q.total_acrylic)) / Decimal("2.88"),
    "pvc_5mm": lambda q, items: Decimal(str(q.total_acrylic)) / Decimal("2.88") * Decimal("1.5") + Decimal(str(q.total_acrylic)) / Decimal("2.88"),
    "uv_print": lambda q, items: Decimal(str(q.area)) * Decimal(str(q.ultrafiolet_base)),
    "uv_print_base": lambda q, items: Decimal(str(q.ultrafiolet_letters_print)) * Decimal(str(q.total_acrylic)),
    "led_module_9dots_pro": lambda q, items: Decimal(str(q.width_pvh)) * Decimal(str(q.height_pvh)) * Decimal("6"),
    "transformer_250w": lambda q, items: items["led_module_9dots_pro"] * Decimal("10.8") / Decimal("250"),
    "glue_201": lambda q, items: Decimal(str(q.total_glue)) * Decimal("2"),
    "wires": lambda q, items: Decimal(str(q.total_wire_m)) * Decimal("2"),
    "multiam_cutting": lambda q, items: items["pvc_8mm"],
    "metises": lambda q, items: Decimal("1.0"),
    "photorelay": lambda q, items: Decimal("1.0"),
    "transport": lambda q, items: Decimal("1.0"),
    "autoheight": lambda q, items: Decimal(str(q.special_technique)),
    "crafting_relative_to_materials_cost": lambda q, items: Decimal("65"),
    "installation": lambda q, items: Decimal("33"),
}

ALUCOBOND_LIGHTBOX_8MM_3MM = {
    "alyukobond_021": lambda q, items: Decimal(str(q.sheets)),
    "tubing_25x50": lambda q, items: Decimal(str(q.profile)),
    "silicone": lambda q, items: Decimal(str(q.silicone)),
    "pvc_8mm": lambda q, items: Decimal(str(q.sheets)) * Decimal("1.5"),
    "acrylic_8mm": lambda q, items: Decimal(str(q.total_acrylic)) / Decimal("2.88"),
    "acrylic_4mm": lambda q, items: Decimal(str(q.total_acrylic)) / Decimal("2.88"),
    "pvc_5mm": lambda q, items: Decimal(str(q.total_acrylic)) / Decimal("2.88") * Decimal("1.5"),
    "uv_print_base": lambda q, items: Decimal(str(q.area)) * Decimal(str(q.ultrafiolet_base)),
    "uv_print": lambda q, items: Decimal(str(q.ultrafiolet_letters_print)) * Decimal(str(q.total_acrylic)),
    "led_module_9dots_pro": lambda q, items: Decimal(str(q.width_pvh)) * Decimal(str(q.height_pvh)) * Decimal("6"),
    "transformer_250w": lambda q, items: items["led_module_9dots_pro"] * Decimal("10.8") / Decimal("250"),
    "glue_201": lambda q, items: Decimal(str(q.total_glue)) * Decimal("2"),
    "wires": lambda q, items: Decimal(str(q.total_wire_m)) * Decimal("2"),
    "multiam_cutting": lambda q, items: items["pvc_8mm"],
    "metises": lambda q, items: Decimal("1.0"),
    "photorelay": lambda q, items: Decimal("1.0"),
    "transport": lambda q, items: Decimal("1.0"),
    "autoheight": lambda q, items: Decimal(str(q.special_technique)),
    "crafting_relative_to_materials_cost": lambda q, items: Decimal("65"),
    "installation": lambda q, items: Decimal("33"),
}


VARIANT_CALCS = {
    # База
    "pseudo_pvc": PSEUDO_PVC_MAP,
    "pseudo_pvc_acrylic": PSEUDO_PVC_ACRYLIC,
    "pseudo_15_30mm": PSEUDO_15_30MM_COLORED,
    "volume_nonsvet": VOLUMETIC_NONLIGHT,
    "light_face": LIGHT_FACE,
    "3d_letters": THREEDIMENSION_LETTERS,
    "light_acrylic_20mm": LIGHT_ACRYLIC_20MM,
    "backlight_contour": BACLIGHT_COUNTOUR,
    "steel_letters": STEEL_LETTERS,
    "steel_letters_light": STEEL_LETTERS_LIGHT,

    "pvc_cloud": PVC_CLOUD,
    "pvc_base": PVC_BASE,
    "alucobond_base": ALUCOBOND_BASE,
    "metal_frame": METAL_FRAME,

    "banner_lightbox": BANNER_LIGHTBOX,
    "acrylic_lightbox": ACRYLIC_LIGHTBOX,
    "acrylic_lightbox_3mm": ACRYLIC_LIGHTBOX_3MM,
    "acrylic_lightbox_8mm": ACRYLIC_LIGHTBOX_8MM,
    "acrylic_lightbox_8mm_3mm": ACRYLIC_LIGHTBOX_8MM_3MM,
    "alucobond_lightbox_3mm": ALUCOBOND_LIGHTBOX_3MM,
    "alucobond_lightbox_8mm": ALUCOBOND_LIGHTBOX_8MM,
    "alucobond_lightbox_8mm_3mm": ALUCOBOND_LIGHTBOX_8MM_3MM,
}


COMBO_VARIANT_CALCS = {
    # Облако
    "pvc_cloud_w_light_face": ["pvc_cloud", "light_face"],
    "pvc_cloud_w_3d_letters": ["pvc_cloud", "3d_letters"],

    # Подложка ПВХ
    "pvc_base_w_light_face": ["pvc_base", "light_face"],
    "pvc_base_w_3d_letters": ["pvc_base", "3d_letters"],
    "pvc_base_w_backlight_contour": ["pvc_base", "backlight_contour"],
    "pvc_base_w_steel_letters": ["pvc_base", "steel_letters"],
    "pvc_base_w_steel_letters_light": ["pvc_base", "steel_letters_light"],

    # Подложка Алюкобонд
    "alucobond_w_light_face": ["alucobond_base", "light_face"],
    "alucobond_w_3d_letters": ["alucobond_base", "3d_letters"],
    "alucobond_w_backlight_contour": ["alucobond_base", "backlight_contour"],
    "alucobond_w_steel_letters": ["alucobond_base", "steel_letters"],
    "alucobond_w_steel_letters_light": ["alucobond_base", "steel_letters_light"],

    # Металлокаркас
    "metal_frame_w_light_face": ["metal_frame", "light_face"],
    "metal_frame_w_3d_letters": ["metal_frame", "3d_letters"],
    "metal_frame_w_backlight_contour": ["metal_frame", "backlight_contour"],
    "metal_frame_w_steel_letters": ["metal_frame", "steel_letters"],
    "metal_frame_w_steel_letters_light": ["metal_frame", "steel_letters_light"],
}


_SPECIALS = {
    "crafting_relative_to_materials_cost": "Изготовление",
    "installation":                       "Монтаж",
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
    coef = Decimal(1) + (Decimal(margin_pct) / Decimal(100))
    for item in variant.items.all():
        item.unit_price = round(item.unit_price * coef, 2)
        item.subtotal = round(item.qty * item.unit_price, 2)
        item.save(update_fields=["unit_price", "subtotal"])



def build_variant(quote: Quote, type_code: str) -> Variant:
    variant, _ = Variant.objects.get_or_create(quote=quote, type_code=type_code)
    variant.items.all().delete()

    base_codes = COMBO_VARIANT_CALCS.get(type_code, [type_code])
    is_combo = len(base_codes) > 1

    qty_cache = {}
    margin_pct = variant.margin_pct

    for origin in base_codes:
        calc = VARIANT_CALCS[origin]
        part_sum = Decimal("0")

        origin_label = SIGN_NAMES.get(origin, origin) if is_combo else None

        for key, fn in calc.items():
            if key in _SPECIALS:
                continue

            qty = fn(quote, qty_cache)
            qty_cache.setdefault(key, qty)
            qty_cache[f"{key}_{origin}"] = qty

            prod = find_product(key)
            unit_price = Decimal(prod.final_price)
            name = PRODUCT_NAME_MAPPING[key]
            if is_combo:
                name = f"{origin_label}: {name}"

            item = VariantItem.objects.create(
                variant=variant,
                name=name,
                product=prod,
                qty=qty,
                unit="шт",
                unit_price=unit_price
            )
            part_sum += item.subtotal

        for sp_key, label in _SPECIALS.items():
            if sp_key not in calc:
                continue
            pct = calc[sp_key](quote, qty_cache)
            price = part_sum * (pct / Decimal("100"))

            name = f"{origin_label}: {label}" if is_combo else label

            VariantItem.objects.create(
                variant=variant,
                name=name,
                product=None,
                qty=1,
                unit="усл.",
                unit_price=round(price, 2),
            )

    if margin_pct:
        apply_margin(variant, margin_pct)

    return variant