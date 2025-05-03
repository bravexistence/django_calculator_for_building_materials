def quote_required_missing(quote):
    need = [
        ("special_technique", quote.special_technique),
        ("ultrafiolet_letters_print", quote.ultrafiolet_letters_print),
        ("ultrafiolet_base", quote.ultrafiolet_base),
    ]

    mats = set(quote.materials)
    if "пвх" in mats:
        need += [("width_pvh", quote.width_pvh),
                 ("height_pvh", quote.height_pvh)]
    if "алюк" in mats:
        need += [("width_alyuk", quote.width_alyuk),
                 ("height_alyuk", quote.height_alyuk)]

    return [name for name, val in need if val in (None, "")]
