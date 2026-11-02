from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Q
from django.utils import timezone
from decimal import Decimal
from .models import Expense, Category, Budget
from .forms import ExpenseForm, CategoryForm, BudgetForm, ExpenseFilterForm


# ───────────────────────────── Dashboard ──────────────────────────────────────

@login_required
def dashboard(request):
    today = timezone.localdate()
    qs = Expense.objects.filter(user=request.user)

    # This-month totals
    month_qs = qs.filter(date__year=today.year, date__month=today.month)
    total_month = month_qs.aggregate(t=Sum('amount'))['t'] or Decimal('0')

    # Spending by category this month
    by_category = (
        month_qs.values('category__name', 'category__color')
        .annotate(total=Sum('amount'))
        .order_by('-total')
    )

    # Recent expenses
    recent = qs.select_related('category')[:5]

    # Budget status this month
    budgets = Budget.objects.filter(
        user=request.user,
        month__year=today.year,
        month__month=today.month,
    ).select_related('category')

    budget_data = []
    for b in budgets:
        spent = month_qs.filter(category=b.category).aggregate(t=Sum('amount'))['t'] or Decimal('0')
        pct = min(int((spent / b.limit) * 100), 100) if b.limit else 0
        budget_data.append({'budget': b, 'spent': spent, 'pct': pct})

    context = {
        'total_month': total_month,
        'by_category': by_category,
        'recent': recent,
        'budget_data': budget_data,
        'today': today,
    }
    return render(request, 'expenses/dashboard.html', context)


# ───────────────────────────── Expenses ───────────────────────────────────────

@login_required
def expense_list(request):
    qs = Expense.objects.filter(user=request.user).select_related('category')
    filter_form = ExpenseFilterForm(request.user, request.GET or None)

    if filter_form.is_valid():
        data = filter_form.cleaned_data
        if data.get('category'):
            qs = qs.filter(category=data['category'])
        if data.get('month'):
            qs = qs.filter(date__month=data['month'])
        if data.get('year'):
            qs = qs.filter(date__year=data['year'])
        if data.get('search'):
            qs = qs.filter(
                Q(title__icontains=data['search']) | Q(notes__icontains=data['search'])
            )

    total = qs.aggregate(t=Sum('amount'))['t'] or Decimal('0')
    context = {'expenses': qs, 'filter_form': filter_form, 'total': total}
    return render(request, 'expenses/expense_list.html', context)


@login_required
def expense_create(request):
    form = ExpenseForm(request.user, request.POST or None, request.FILES or None)
    if form.is_valid():
        expense = form.save(commit=False)
        expense.user = request.user
        expense.save()
        messages.success(request, 'Expense added successfully!')
        return redirect('expenses:list')
    return render(request, 'expenses/expense_form.html', {'form': form, 'title': 'Add Expense'})


@login_required
def expense_edit(request, pk):
    expense = get_object_or_404(Expense, pk=pk, user=request.user)
    form = ExpenseForm(request.user, request.POST or None, request.FILES or None, instance=expense)
    if form.is_valid():
        form.save()
        messages.success(request, 'Expense updated!')
        return redirect('expenses:list')
    return render(request, 'expenses/expense_form.html', {'form': form, 'title': 'Edit Expense', 'expense': expense})


@login_required
def expense_delete(request, pk):
    expense = get_object_or_404(Expense, pk=pk, user=request.user)
    if request.method == 'POST':
        expense.delete()
        messages.success(request, 'Expense deleted.')
        return redirect('expenses:list')
    return render(request, 'expenses/expense_confirm_delete.html', {'expense': expense})


# ───────────────────────────── Categories ─────────────────────────────────────

@login_required
def category_list(request):
    categories = Category.objects.filter(user=request.user).annotate(
        total=Sum('expenses__amount')
    )
    return render(request, 'expenses/category_list.html', {'categories': categories})


@login_required
def category_create(request):
    form = CategoryForm(request.POST or None)
    if form.is_valid():
        cat = form.save(commit=False)
        cat.user = request.user
        cat.save()
        messages.success(request, f'Category "{cat.name}" created!')
        return redirect('expenses:categories')
    return render(request, 'expenses/category_form.html', {'form': form, 'title': 'New Category'})


@login_required
def category_edit(request, pk):
    cat = get_object_or_404(Category, pk=pk, user=request.user)
    form = CategoryForm(request.POST or None, instance=cat)
    if form.is_valid():
        form.save()
        messages.success(request, 'Category updated!')
        return redirect('expenses:categories')
    return render(request, 'expenses/category_form.html', {'form': form, 'title': 'Edit Category', 'category': cat})


@login_required
def category_delete(request, pk):
    cat = get_object_or_404(Category, pk=pk, user=request.user)
    if request.method == 'POST':
        cat.delete()
        messages.success(request, 'Category deleted.')
        return redirect('expenses:categories')
    return render(request, 'expenses/category_confirm_delete.html', {'category': cat})


# ───────────────────────────── Budgets ────────────────────────────────────────

@login_required
def budget_list(request):
    budgets = Budget.objects.filter(user=request.user).select_related('category')
    return render(request, 'expenses/budget_list.html', {'budgets': budgets})


@login_required
def budget_create(request):
    form = BudgetForm(request.user, request.POST or None)
    if form.is_valid():
        budget = form.save(commit=False)
        budget.user = request.user
        budget.save()
        messages.success(request, 'Budget set!')
        return redirect('expenses:budgets')
    return render(request, 'expenses/budget_form.html', {'form': form, 'title': 'Set Budget'})


@login_required
def budget_delete(request, pk):
    budget = get_object_or_404(Budget, pk=pk, user=request.user)
    if request.method == 'POST':
        budget.delete()
        messages.success(request, 'Budget removed.')
        return redirect('expenses:budgets')
    return render(request, 'expenses/budget_confirm_delete.html', {'budget': budget})
