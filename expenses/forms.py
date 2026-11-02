from django import forms
from django.core.exceptions import ValidationError
from .models import Expense, Category, Budget
import datetime


class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ['title', 'amount', 'date', 'category', 'notes', 'receipt']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].queryset = Category.objects.filter(user=user)
        self.fields['category'].empty_label = 'Uncategorised'


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'icon', 'color']
        widgets = {
            'color': forms.TextInput(attrs={'type': 'color'}),
        }


class BudgetForm(forms.ModelForm):
    # Use a plain text field so we can accept browser's YYYY-MM format
    month = forms.CharField(
        widget=forms.TextInput(attrs={
            'type': 'month',
            'placeholder': 'YYYY-MM',
        }),
        help_text='Select the month for this budget (e.g. 2026-11)',
        label='Month',
    )

    class Meta:
        model = Budget
        fields = ['category', 'month', 'limit']

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].queryset = Category.objects.filter(user=user)
        # Pre-fill month field if editing an existing instance
        if self.instance and self.instance.pk and self.instance.month:
            self.fields['month'].initial = self.instance.month.strftime('%Y-%m')

    def clean_month(self):
        """
        Convert browser's YYYY-MM string → date(YYYY, MM, 1).
        Also accepts full YYYY-MM-DD strings for safety.
        """
        value = self.cleaned_data.get('month', '').strip()
        # Accept "YYYY-MM" (browser month input)
        if value and len(value) == 7:
            try:
                return datetime.date(int(value[:4]), int(value[5:7]), 1)
            except (ValueError, IndexError):
                raise ValidationError('Enter a valid month in YYYY-MM format, e.g. 2026-11.')
        # Accept full date "YYYY-MM-DD" as fallback
        if value and len(value) == 10:
            try:
                parsed = datetime.date.fromisoformat(value)
                return parsed.replace(day=1)
            except ValueError:
                raise ValidationError('Enter a valid month in YYYY-MM format, e.g. 2026-11.')
        raise ValidationError('Enter a valid month in YYYY-MM format, e.g. 2026-11.')


class ExpenseFilterForm(forms.Form):
    MONTH_CHOICES = [('', 'All months')] + [
        (str(i), name) for i, name in enumerate(
            ['Jan','Feb','Mar','Apr','May','Jun',
             'Jul','Aug','Sep','Oct','Nov','Dec'], 1
        )
    ]
    category = forms.ModelChoiceField(queryset=None, required=False, empty_label='All categories')
    month = forms.ChoiceField(choices=MONTH_CHOICES, required=False)
    year = forms.IntegerField(required=False, widget=forms.NumberInput(attrs={'placeholder': 'Year'}))
    search = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder': 'Search...'}))

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].queryset = Category.objects.filter(user=user)

