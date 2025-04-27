from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django import forms
from django.db import transaction

from .models import Quote, SignBlock, Variant
from .forms import QuoteFrontForm, SignBlockFormSet
from .constants import SIGN_TYPES
from .services.sign_variants import build_variant

class LoginForm(forms.Form):
    username = forms.CharField(label="Логин")
    password = forms.CharField(label="Пароль", widget=forms.PasswordInput)


class QuoteForm(forms.ModelForm):
    class Meta:
        model = Quote
        fields = ["client_name"]


class SignBlockForm(forms.ModelForm):
    class Meta:
        model = SignBlock
        fields = ["letter_size", "letter_count"]


def login_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    form = LoginForm(request.POST or None)
    error_message = None
    if form.is_valid():
        user = authenticate(
            request,
            username=form.cleaned_data["username"],
            password=form.cleaned_data["password"]
        )
        if user:
            login(request, user)
            return redirect("dashboard")
        else:
            error_message = "Неверный логин или пароль"

    return render(request, "login.html", {"form": form, "error": error_message})


def logout_view(request):
    logout(request)
    return redirect("login")


@login_required
def dashboard_view(request):
    q = request.GET.get("q", "").strip()

    if q:
        quotes = Quote.objects.filter(client_name__icontains=q).order_by("-created_at")
    else:
        quotes = Quote.objects.order_by("-created_at")[:20]

    return render(request, "dashboard.html", {"quotes": quotes})


@login_required
def quote_detail_view(request, quote_id):
    quote = get_object_or_404(Quote, pk=quote_id)

    if request.method == "POST":
        form = QuoteFrontForm(request.POST, instance=quote)
        formset = SignBlockFormSet(request.POST, instance=quote)

        if form.is_valid() and formset.is_valid():
            with transaction.atomic():
                form.save()
                formset.save()
            return redirect("quote_detail", quote_id=quote.id)
    else:
        form = QuoteFrontForm(instance=quote)
        formset = SignBlockFormSet(instance=quote)

    return render(request, "quote_detail.html", {
        "form": form,
        "formset": formset,
        "quote": quote,
        "variants": quote.variants.all(),
        "sign_types": dict(SIGN_TYPES),  # передаем словарь для удобства
    })


@require_POST
@login_required
def set_variants(request, quote_id):
    quote = get_object_or_404(Quote, pk=quote_id)

    for code, _ in SIGN_TYPES:
        use_flag   = f"use_{code}" in request.POST
        margin_val = request.POST.get(f"margin_{code}", "0") or "0"

        variant, _ = Variant.objects.get_or_create(quote=quote, type_code=code)
        variant.use_in_offer = use_flag
        variant.margin_pct = int(margin_val)
        variant.save(update_fields=["use_in_offer", "margin_pct"])

        # Если пользователь включил шаблон впервые — сразу пересчитать вариант
        if use_flag and not variant.items.exists():
            build_variant(quote, code)

    return redirect("quote_detail", quote_id=quote.id)
