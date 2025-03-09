from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.core.validators import MinValueValidator
import numpy_financial as npf
import math
from datetime import date, timedelta
import numpy_financial as npf
from django.db import models

class User(AbstractUser):
    ROLES = (
        ('LP', 'Loan Provider'),
        ('LC', 'Loan Customer'),
        ('BP', 'Bank Personnel'),
    )
    role = models.CharField(max_length=2, choices=ROLES)

    groups = models.ManyToManyField(
        Group,
        blank=True,
        related_name="custom_user_set",
        help_text='The groups this user belongs to.',
        verbose_name='groups'
    )
    user_permissions = models.ManyToManyField(
        Permission,
        blank=True,
        related_name="custom_user_permissions_set",
        help_text='Specific permissions for this user.',
        verbose_name='user permissions'
    )

class LoanFund(models.Model):
    provider = models.ForeignKey(User, on_delete=models.PROTECT)
    amount = models.DecimalField(max_digits=15, decimal_places=2, validators=[MinValueValidator(1000)])
    status = models.CharField(max_length=1, choices=[('P', 'Pending'), ('A', 'Approved'), ('R', 'Rejected')], default='P')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class LoanConfig(models.Model):
    min_amount = models.DecimalField(max_digits=15, decimal_places=2)
    max_amount = models.DecimalField(max_digits=15, decimal_places=2)
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2)
    duration_months = models.IntegerField()
    compound_frequency = models.CharField(max_length=10, choices=[('M', 'Monthly'), ('Q', 'Quarterly'), ('A', 'Annually')], default='M')



class Loan(models.Model):
    customer = models.ForeignKey('loans.User', on_delete=models.PROTECT)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    term_months = models.IntegerField()
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2)
    start_date = models.DateField(null=True)
    end_date = models.DateField(null=True)
    remaining_amount = models.DecimalField(max_digits=15, decimal_places=2)
    status = models.CharField(
        max_length=1,
        choices=[('P', 'Pending'), ('A', 'Approved'), ('R', 'Rejected')],
        default='P'
    )
    payment_schedule = models.JSONField(default=dict)

    def calculate_emi(self):
        """
        Basic EMI calculation using numpy_financial.
        """
        rate = float(self.interest_rate) / 100 / 12
        return round(-npf.pmt(rate, self.term_months, float(self.amount)), 2)

    def calculate_sophisticated_emi(self):
        """
        Calculates EMI using compound frequency from LoanConfig.
        """
        from loans.models import LoanConfig
        config = LoanConfig.objects.first()  # Assume a single config object exists.
        if not config:
            raise Exception("Loan configuration not set.")

        # Determine compounding frequency
        frequency_map = {
            'M': 12,
            'Q': 4,
            'A': 1,
        }
        compound_periods = frequency_map.get(config.compound_frequency, 12)

        # Periodic interest rate (convert interest_rate to float)
        r = (float(self.interest_rate) / 100) / compound_periods
        n = self.term_months  # total number of months
        
        # EMI formula: If r is 0, avoid division by zero.
        if r == 0:
            return round(float(self.amount) / n, 2)
        numerator = float(self.amount) * r * math.pow(1 + r, n)
        denominator = math.pow(1 + r, n) - 1
        emi = numerator / denominator
        return round(emi, 2)

    def update_remaining_amount(self):
        """
        Updates the remaining amount after payments.
        """
        total_paid = sum(p.amount for p in self.payment_set.all())
        self.remaining_amount = float(self.amount) * (1 + float(self.interest_rate) / 100) - total_paid
        self.save()

    def generate_payment_schedule(self):
        """
        Generates an amortization schedule for the loan.
        Returns a list of dictionaries, each representing a payment installment.
        """
        schedule = []
        from loans.models import LoanConfig
        config = LoanConfig.objects.first()
        if not config:
            raise Exception("Loan configuration not set.")

        # Determine payment interval based on compound frequency (in months)
        frequency_map = {
            'M': 1,   # monthly: every 1 month
            'Q': 3,   # quarterly: every 3 months
            'A': 12,  # annually: every 12 months
        }
        interval = frequency_map.get(config.compound_frequency, 1)
        n = math.ceil(self.term_months / interval)
        # Calculate periodic interest rate; convert interest_rate to float for arithmetic
        r = (float(self.interest_rate) / 100) / (12 / interval)
        if r == 0:
            emi = float(self.amount) / n
        else:
            emi = float(self.amount) * r * math.pow(1 + r, n) / (math.pow(1 + r, n) - 1)
        remaining_balance = float(self.amount)
        due_date = self.start_date if self.start_date else date.today()

        for i in range(1, n + 1):
            interest_payment = remaining_balance * r
            principal_payment = emi - interest_payment
            remaining_balance -= principal_payment
            schedule.append({
                'installment': i,
                'due_date': (due_date + timedelta(days=interval * 30)).isoformat(),
                'total_installment': round(emi, 2),
                'principal_payment': round(principal_payment, 2),
                'interest_payment': round(interest_payment, 2),
                'remaining_balance': round(max(remaining_balance, 0), 2)
            })
            due_date = due_date + timedelta(days=interval * 30)
        
        self.payment_schedule = schedule
        self.save()
        return schedule


class Payment(models.Model):
    loan = models.ForeignKey(Loan, on_delete=models.PROTECT)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    payment_date = models.DateTimeField(auto_now_add=True)
    reference_number = models.CharField(max_length=50, unique=True)
