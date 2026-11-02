from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Category(models.Model):
    """Expense category (per user)."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='categories')
    name = models.CharField(max_length=100)
    icon = models.CharField(max_length=50, default='bi-tag', help_text='Bootstrap Icons class name')
    color = models.CharField(max_length=7, default='#6c757d', help_text='Hex color code')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'categories'
        ordering = ['name']
        unique_together = ('user', 'name')

    def __str__(self):
        return self.name


class Expense(models.Model):
    """A single expense entry."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='expenses')
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='expenses'
    )
    title = models.CharField(max_length=200)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField(default=timezone.now)
    notes = models.TextField(blank=True)
    receipt = models.ImageField(upload_to='receipts/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date', '-created_at']

    def __str__(self):
        return f'{self.title} - Rs.{self.amount}'


class Budget(models.Model):
    """Monthly budget per category."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='budgets')
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name='budgets'
    )
    month = models.DateField(help_text='First day of the month, e.g. 2026-11-01')
    limit = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        unique_together = ('user', 'category', 'month')
        ordering = ['-month']

    def __str__(self):
        return f'{self.category} - {self.month:%b %Y} - Rs.{self.limit}'
