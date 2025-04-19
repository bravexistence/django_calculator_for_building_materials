from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django import forms
from parser_and_calculator.models import Quote, SignBlock
from parser_and_calculator.forms import QuoteFrontForm, SignBlockFormSet
from django.db import transaction

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
        user = authenticate(request,
                            username=form.cleaned_data["username"],
                            password=form.cleaned_data["password"])
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

    return render(request, "dashboard.html", {
        "quotes": quotes,
    })

@login_required
def quote_detail_view(request, quote_id):
    quote = get_object_or_404(Quote, pk=quote_id)

    if request.method == "POST":
        form    = QuoteFrontForm(request.POST, instance=quote)
        formset = SignBlockFormSet(request.POST, instance=quote)

        if form.is_valid() and formset.is_valid():
            with transaction.atomic():
                form.save()
                formset.save()
            return redirect("quote_detail", quote_id=quote.id)
    else:
        form    = QuoteFrontForm(instance=quote)
        formset = SignBlockFormSet(instance=quote)

    return render(request, "quote_detail.html", {
        "form": form,
        "formset": formset,
        "quote": quote,
    })
