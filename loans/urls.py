from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns

from .views import (
    sample_view,
    LoanFundListView,
    LoanListView,
    PaymentCreateView,
    LoanConfigDetailView,
    LoanApprovalUpdateView,
    LoanFundApprovalUpdateView,
    PaymentScheduleView,
)

urlpatterns = [
    path('sample/', sample_view, name='sample'),
    path('loanfunds/', LoanFundListView.as_view(), name='loanfund-list'),
    path('loans/', LoanListView.as_view(), name='loan-list'),
    path('payments/', PaymentCreateView.as_view(), name='payment-create'),
    path('loanconfig/', LoanConfigDetailView.as_view(), name='loanconfig-detail'),
    path('loanapproval/<int:pk>/', LoanApprovalUpdateView.as_view(), name='loanapproval-detail'),
    path('loanfundapproval/<int:pk>/', LoanFundApprovalUpdateView.as_view(), name='loanfundapproval-detail'),
    path('paymentschedule/<int:loan_id>/', PaymentScheduleView.as_view(), name='paymentschedule'),

]

urlpatterns = format_suffix_patterns(urlpatterns)
