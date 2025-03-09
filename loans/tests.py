from datetime import date, timedelta
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from loans.models import User, LoanFund, Loan, Payment, LoanConfig
from django.db.models import Sum

class LoanApprovalTestCase(TestCase):
    def setUp(self):
        self.bp_user = User.objects.create_user(username='bp', password='pass', role='BP')
        self.lc_user = User.objects.create_user(username='lc', password='pass', role='LC')
        
        
        self.loan_fund = LoanFund.objects.create(provider=self.bp_user, amount=10000, status='A')
        
       
        self.loan = Loan.objects.create(
            customer=self.lc_user,
            amount=5000,
            term_months=12,
            interest_rate=10,
            remaining_amount=5000,
            status='P'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.bp_user)

    def test_approve_loan_within_funds(self):
        url = reverse('loanapproval-detail', args=[self.loan.id])
        response = self.client.patch(url, {'status': 'A'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.loan.refresh_from_db()
        self.assertEqual(self.loan.status, 'A')

    def test_approve_loan_exceeding_funds(self):
      
        url = reverse('loanapproval-detail', args=[self.loan.id])
        response = self.client.patch(url, {'status': 'A'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
      
        loan2 = Loan.objects.create(
            customer=self.lc_user,
            amount=6000,
            term_months=12,
            interest_rate=10,
            remaining_amount=6000,
            status='P'
        )
        url2 = reverse('loanapproval-detail', args=[loan2.id])
        response2 = self.client.patch(url2, {'status': 'A'}, format='json')
        self.assertEqual(response2.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('exceeds available funds', response2.data.get('error', ''))

class LoanFundApprovalTestCase(TestCase):
    def setUp(self):
       
        self.bp_user = User.objects.create_user(username='bp', password='pass', role='BP')
        self.lp_user = User.objects.create_user(username='lp', password='pass', role='LP')
        self.loan_fund = LoanFund.objects.create(provider=self.lp_user, amount=8000, status='P')
        self.client = APIClient()
        self.client.force_authenticate(user=self.bp_user)
    
    def test_approve_loan_fund(self):
        url = reverse('loanfundapproval-detail', args=[self.loan_fund.id])
        response = self.client.patch(url, {'status': 'A'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.loan_fund.refresh_from_db()
        self.assertEqual(self.loan_fund.status, 'A')

class PaymentCreateTestCase(TestCase):
    def setUp(self):
        
        self.lc_user = User.objects.create_user(username='lc', password='pass', role='LC')
        self.bp_user = User.objects.create_user(username='bp', password='pass', role='BP')
       
        LoanConfig.objects.create(min_amount=1000, max_amount=10000, interest_rate=10, duration_months=12, compound_frequency='M')
        self.loan = Loan.objects.create(
            customer=self.lc_user,
            amount=5000,
            term_months=12,
            interest_rate=10,
            remaining_amount=5000,
            status='P'
        )
        self.client = APIClient()
   
        self.client.force_authenticate(user=self.lc_user)

    def test_make_payment_within_balance(self):
        url = reverse('payment-create')
        payment_data = {
            'loan': self.loan.id,
            'amount': 2000
        }
        response = self.client.post(url, payment_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.loan.refresh_from_db()
  
        self.assertEqual(float(self.loan.remaining_amount), 3000)
   
        self.assertIn('reference_number', response.data)
        self.assertIn('remaining_amount', response.data)

    def test_payment_exceeding_remaining_amount(self):
        url = reverse('payment-create')

        payment_data = {
            'loan': self.loan.id,
            'amount': 6000
        }
        response = self.client.post(url, payment_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Payment exceeds remaining loan balance', str(response.data))

class PaymentScheduleTestCase(TestCase):
    def setUp(self):
       
        self.lc_user = User.objects.create_user(username='lc', password='pass', role='LC')
        self.loan = Loan.objects.create(
            customer=self.lc_user,
            amount=12000,
            term_months=12,
            interest_rate=10,
            remaining_amount=12000,
            status='A',
          
            start_date=date.today()
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.lc_user)
    
        if not LoanConfig.objects.exists():
            LoanConfig.objects.create(min_amount=1000, max_amount=20000, interest_rate=10, duration_months=12, compound_frequency='M')

    def test_get_payment_schedule(self):
        url = reverse('paymentschedule', args=[self.loan.id])
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('schedule', response.data)
    
        self.assertGreater(len(response.data['schedule']), 0)

    def test_payment_schedule_not_allowed_for_wrong_user(self):
        other_user = User.objects.create_user(username='other', password='pass', role='LC')
        self.client.force_authenticate(user=other_user)
        url = reverse('paymentschedule', args=[self.loan.id])
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn('Not allowed', str(response.data))

class SampleViewTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_sample_view(self):
        url = reverse('sample')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('message'), 'Hello, DRF is working with custom models!')
