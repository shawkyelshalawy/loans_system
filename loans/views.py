from rest_framework import generics, status
import uuid
from rest_framework.exceptions import ValidationError

from django.db import transaction
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import api_view, permission_classes
from django.db.models import Sum
from .models import LoanFund, LoanConfig, Loan, Payment
from .serializers import (
    LoanFundSerializer,
    LoanConfigSerializer,
    LoanSerializer,
    PaymentSerializer,
    LoanApprovalSerializer,
    LoanFundApprovalSerializer,
)
from .permissions import IsLoanProvider, IsLoanCustomer, IsBankPersonnel
from rest_framework.views import APIView


@api_view(['GET'])
@permission_classes([AllowAny])
def sample_view(request):
    return Response({'message': 'Hello, DRF is working with custom models!'})


class LoanFundListView(generics.ListAPIView):
    serializer_class = LoanFundSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.role == 'LP':
            return LoanFund.objects.filter(provider=user)
        elif user.role == 'BP':
            return LoanFund.objects.all()
        return LoanFund.objects.none()


class LoanListView(generics.ListAPIView):
    serializer_class = LoanSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.role == 'LC':
            return Loan.objects.filter(customer=user)
        elif user.role == 'BP':
            return Loan.objects.all()
        return Loan.objects.none()


class PaymentCreateView(generics.CreateAPIView):
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated, IsLoanCustomer]

    def perform_create(self, serializer):
        with transaction.atomic():
            loan = serializer.validated_data['loan']
            amount = serializer.validated_data['amount']
            
            
            if loan.customer != self.request.user:
                raise ValidationError("You can only make payments for your own loans.")
            
           
            if amount > loan.remaining_amount:
                raise ValidationError("Payment exceeds remaining loan balance.")
            
            
            loan.remaining_amount = float(loan.remaining_amount) - float(amount)
            if loan.remaining_amount <= 0:
               
                loan.status = 'R'
            loan.save()
            
           
            ref = serializer.validated_data.get('reference_number', None)
            if not ref or ref.strip() == "":
                ref = f"PAY-{uuid.uuid4().hex[:8].upper()}"
            
            
            serializer.save(reference_number=ref)

    def create(self, request, *args, **kwargs):
        
        response = super().create(request, *args, **kwargs)
       
        loan_id = request.data.get('loan')
        try:
            loan = Loan.objects.get(id=loan_id)
            response.data['remaining_amount'] = loan.remaining_amount
        except Loan.DoesNotExist:
            response.data['remaining_amount'] = None
        return response

class LoanConfigDetailView(generics.RetrieveUpdateAPIView):
    queryset = LoanConfig.objects.all()
    serializer_class = LoanConfigSerializer
    permission_classes = [IsAuthenticated, IsBankPersonnel]

    
    def get_object(self):
        return LoanConfig.objects.first()


class LoanApprovalUpdateView(generics.UpdateAPIView):
    queryset = Loan.objects.all()
    serializer_class = LoanApprovalSerializer
    permission_classes = [IsAuthenticated, IsBankPersonnel]

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        new_status = request.data.get('status', None)
        
        if new_status == 'A':
            approved_funds_total = LoanFund.objects.filter(status='A').aggregate(total=Sum('amount'))['total'] or 0
            approved_loans_total = Loan.objects.filter(status='A').aggregate(total=Sum('amount'))['total'] or 0
            if (approved_loans_total + instance.amount) > approved_funds_total:
                return Response({'error': 'Approving this loan exceeds available funds.'}, status=status.HTTP_400_BAD_REQUEST)
        return super().update(request, *args, **kwargs)


class LoanFundApprovalUpdateView(generics.UpdateAPIView):
    queryset = LoanFund.objects.all()
    serializer_class = LoanFundApprovalSerializer
    permission_classes = [IsAuthenticated, IsBankPersonnel]

class PaymentScheduleView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, loan_id):
        try:
            loan = Loan.objects.get(id=loan_id)
            if request.user.role == 'LC' and loan.customer != request.user:
                return Response({'error': 'Not allowed.'}, status=status.HTTP_403_FORBIDDEN)
            schedule = loan.generate_payment_schedule()
            return Response({'schedule': schedule})
        except Loan.DoesNotExist:
            return Response({'error': 'Loan not found.'}, status=status.HTTP_404_NOT_FOUND)