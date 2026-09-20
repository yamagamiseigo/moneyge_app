from django import forms
from .models import Debt_Information

class DebtForm(forms.ModelForm):
    class Meta:
        model = Debt_Information

        fields = ['name_lender', 'current_balance', 'annual_interest_rate', 'monthly_repayment', 'monthly_payment_date', 'editor_owner']