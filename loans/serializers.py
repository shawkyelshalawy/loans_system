from rest_framework import serializers
from .models import LoanFund, LoanConfig, Loan, Payment

class LoanFundSerializer(serializers.ModelSerializer):
    class Meta:
        model = LoanFund
        fields = '__all__'

class LoanConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = LoanConfig
        fields = '__all__'

class LoanSerializer(serializers.ModelSerializer):
    emi = serializers.SerializerMethodField()

    class Meta:
        model = Loan
        fields = '__all__'

    def get_emi(self, obj):
        try:
            return obj.calculate_sophisticated_emi()
        except Exception as e:
            return str(e)


class PaymentSerializer(serializers.ModelSerializer):
    reference_number = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = Payment
        fields = ['loan', 'amount', 'payment_date', 'reference_number']

class LoanApprovalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Loan
        fields = ('id', 'status')

class LoanFundApprovalSerializer(serializers.ModelSerializer):
    class Meta:
        model = LoanFund
        fields = ('id', 'status')
