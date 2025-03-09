from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, LoanFund, LoanConfig, Loan, Payment

class CustomUserAdmin(UserAdmin):
    
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('role',)}),
    )
  
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'role', 'password1', 'password2'),
        }),
    )

admin.site.register(User, CustomUserAdmin)
admin.site.register(LoanFund)
admin.site.register(LoanConfig)
admin.site.register(Loan)
admin.site.register(Payment)
