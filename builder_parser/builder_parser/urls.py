"""
URL configuration for builder_parser project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from parser_and_calculator.views import (
    login_view, logout_view,
    dashboard_view, quote_detail_view,
    set_variants, quote_create_view, quote_delete_view,
    quote_pdf_view)

admin.site.site_header = "Калькулятор и расчет материалов"
admin.site.site_title = "Django"
admin.site.index_title = "Навигация по разделам"

urlpatterns = [
    path('grappelli/', include('grappelli.urls')),
    path("admin/", admin.site.urls),
    path("", login_view, name="login"),
    path("logout/", logout_view, name="logout"),
    path("dashboard/", dashboard_view, name="dashboard"),
    path("dashboard/quote/<int:quote_id>/", quote_detail_view, name="quote_detail"),
    path("quote/<int:quote_id>/variants/", set_variants, name="set_variants"),
    path("quote/create/", quote_create_view, name="quote_create"),
    path("quote/<int:quote_id>/delete/", quote_delete_view, name="quote_delete"),
    path("quote/<int:quote_id>/pdf/", quote_pdf_view, name="quote_pdf"),

]
