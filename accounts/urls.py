from django.urls import path
from .views import accounts, edit_fee_structure, enter_closing_balance, enter_closing_balance_class, edit_fee_structure

urlpatterns = [
    path('',accounts, name = "accounts"),
    path('edit_fee_structure/', edit_fee_structure, name = "edit_fee_structure"),
    path("enter_closing_balance/", enter_closing_balance, name = "enter_closing_balance"),
    path("enter_closing_balance_class/<int:form>/<str:stream>/", enter_closing_balance_class, name = "enter_closing_balance_class"),
    path("edit_fee_structure/", edit_fee_structure, name = "edit_fee_structure"),
]