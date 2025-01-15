from django.contrib import admin
from .models import Payslip, Employee, Salary

# Register your models here.

admin.site.register(Payslip)
admin.site.register(Employee)
admin.site.register(Salary)