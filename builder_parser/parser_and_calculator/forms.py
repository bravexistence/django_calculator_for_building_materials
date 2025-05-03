from django import forms
from django.forms import inlineformset_factory
from parser_and_calculator.models import Quote, SignBlock


class QuoteFrontForm(forms.ModelForm):
    class Meta:
        model = Quote
        fields = (
            "materials",
            "width_pvh", "height_pvh",
            "width_alyuk", "height_alyuk",
            "special_technique",
            "ultrafiolet_base",
            "ultrafiolet_letters_print",
        )
        widgets = {
            "materials": forms.CheckboxSelectMultiple,
            "width_pvh":  forms.NumberInput(attrs={"step": 0.01, "min": 0}),
            "height_pvh": forms.NumberInput(attrs={"step": 0.01, "min": 0}),
            "width_alyuk":  forms.NumberInput(attrs={"step": 0.01, "min": 0}),
            "height_alyuk": forms.NumberInput(attrs={"step": 0.01, "min": 0}),
            "special_technique": forms.NumberInput(attrs={"step": "0.1"}),
            "ultrafiolet_base": forms.Select(choices=[(0.0, "Нет (0)"), (1.0, "Да (1)")]),
            "ultrafiolet_letters_print": forms.NumberInput(attrs={"step": "0.1"}),
        }



SignBlockFormSet = inlineformset_factory(
    Quote,
    SignBlock,
    fields=("letter_size", "letter_count",),
    extra=0,
    can_delete=True,
)


