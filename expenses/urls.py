from django.urls import path
from . import views

app_name = 'expenses'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    # Expenses
    path('expenses/', views.expense_list, name='list'),
    path('expenses/add/', views.expense_create, name='add'),
    path('expenses/<int:pk>/edit/', views.expense_edit, name='edit'),
    path('expenses/<int:pk>/delete/', views.expense_delete, name='delete'),
    # Categories
    path('categories/', views.category_list, name='categories'),
    path('categories/add/', views.category_create, name='category-add'),
    path('categories/<int:pk>/edit/', views.category_edit, name='category-edit'),
    path('categories/<int:pk>/delete/', views.category_delete, name='category-delete'),
    # Budgets
    path('budgets/', views.budget_list, name='budgets'),
    path('budgets/add/', views.budget_create, name='budget-add'),
    path('budgets/<int:pk>/delete/', views.budget_delete, name='budget-delete'),
]

