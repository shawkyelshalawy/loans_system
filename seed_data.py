from datetime import date
from django.db import transaction
from loans.models import User, LoanFund, LoanConfig, Loan, Payment

@transaction.atomic
def run():
    print("Deleting old seed data...")
    # Delete Payments, Loans, LoanFunds, LoanConfig, and non-superuser Users
    Payment.objects.all().delete()
    Loan.objects.all().delete()
    LoanFund.objects.all().delete()
    LoanConfig.objects.all().delete()
    User.objects.exclude(is_superuser=True).delete()

    print("Creating users...")
    # Create users (if already exist, they will be recreated)
    bp = User.objects.create_user(username='bp', password='pass', role='BP', is_staff=True)
    lp = User.objects.create_user(username='lp', password='pass', role='LP')
    lc = User.objects.create_user(username='lc', password='pass', role='LC')

    print("Creating LoanConfig...")
    config = LoanConfig.objects.create(
        min_amount=1000,
        max_amount=50000,
        interest_rate=5,
        duration_months=36,
        compound_frequency='M'
    )

    print("Creating LoanFunds...")
    loan_fund1 = LoanFund.objects.create(
        provider=lp,
        amount=20000,
        status='A'  # Approved
    )
    loan_fund2 = LoanFund.objects.create(
        provider=lp,
        amount=15000,
        status='P'  # Pending
    )

    print("Creating Loans...")
    loan1 = Loan.objects.create(
        customer=lc,
        amount=5000,
        term_months=12,
        interest_rate=5,
        start_date=date.today(),
        end_date=date.today(),
        remaining_amount=5000,
        status='A'  # Approved
    )
    loan2 = Loan.objects.create(
        customer=lc,
        amount=8000,
        term_months=24,
        interest_rate=6,
        start_date=date.today(),
        end_date=date.today(),
        remaining_amount=8000,
        status='P'  # Pending
    )

    print("Creating Payment for loan1...")
    payment1 = Payment.objects.create(
        loan=loan1,
        amount=1000,
        reference_number='PAY001'
    )

    print("Seed data created successfully!")

if __name__ == '__main__':
    run()
