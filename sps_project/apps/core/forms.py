import datetime
from django import forms
from .models import Employee, Salary

class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = '__all__'
        exclude = ['employee_code']  # Exclude the employee_id field
        widgets = {
            'employee_id': forms.TextInput(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'staff_type': forms.Select(attrs={'class': 'form-control form-select'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'designation': forms.TextInput(attrs={'class': 'form-control'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'grade_level': forms.TextInput(attrs={'class': 'form-control'}),
            'account_number': forms.TextInput(attrs={'class': 'form-control'}),
            'bank_name': forms.TextInput(attrs={'class': 'form-control'}),
            'account_name': forms.TextInput(attrs={'class': 'form-control'}),
        }

class SalaryForm(forms.ModelForm):
    class Meta:
        model = Salary
        fields = '__all__'
        widgets = {
            'employee': forms.Select(attrs={'class': 'form-control form-select'}),
            'salary_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'basic_pay': forms.NumberInput(attrs={'class': 'form-control'}),
            'no_of_days': forms.NumberInput(attrs={'class': 'form-control'}),
            'actual_attendance': forms.NumberInput(attrs={'class': 'form-control'}),
            'rent_allowance': forms.NumberInput(attrs={'class': 'form-control'}),
            'transport_allowance': forms.NumberInput(attrs={'class': 'form-control'}),
            'meal_allowance': forms.NumberInput(attrs={'class': 'form-control'}),
            'utility_allowance': forms.NumberInput(attrs={'class': 'form-control'}),
            'other_allowances': forms.NumberInput(attrs={'class': 'form-control'}),
            'overtime': forms.NumberInput(attrs={'class': 'form-control'}),
            'arrears': forms.NumberInput(attrs={'class': 'form-control'}),
            'staff_loan_deduction': forms.NumberInput(attrs={'class': 'form-control'}),
            'rent_deduction': forms.NumberInput(attrs={'class': 'form-control'}),
            'medical_deduction': forms.NumberInput(attrs={'class': 'form-control'}),
            'pension_contribution': forms.NumberInput(attrs={'class': 'form-control'}),
            'shortage_deduction': forms.NumberInput(attrs={'class': 'form-control'}),
            'development_levy': forms.NumberInput(attrs={'class': 'form-control'}),
            'personal_income_tax': forms.NumberInput(attrs={'class': 'form-control'}),
        }


class EmployeeUploadForm(forms.Form):
    file = forms.FileField()
    widget = {
        'file': forms.FileInput(attrs={'class': 'form-control form-control-file'})
    }


class PayrollUploadForm(forms.Form):
    file = forms.FileField()
    widget = {
        'file': forms.FileInput(attrs={'class': 'form-control form-control-file'})
    }


class MonthlyPayrollSummaryForm(forms.Form):
    month = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        label="Select Month"
    )
    staff_type = forms.ChoiceField(
        choices=Employee.STAFF_TYPE_CHOICES,
        required=False,
        label="Select Staff Type",
        widget=forms.Select(attrs={'class': 'form-control form-select'})
    )
    location = forms.CharField(
        max_length=100,
        required=False,
        label="Select Location",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    # def clean_month(self):
    #     month_str = self.cleaned_data['month']
    #     try:
    #         return datetime.datetime.strptime(month_str, '%Y-%m').date()
    #     except ValueError:
    #         raise forms.ValidationError("Enter a valid date in YYYY-MM format.")

class EmployeeCompensationReportForm(forms.Form):
    start_date = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        label="Start Date"
    )
    end_date = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        label="End Date"
    )
    employees = forms.ModelMultipleChoiceField(
        queryset=Employee.objects.all(),
        required=False,
        label="Select Employees",
        widget=forms.SelectMultiple(attrs={'class': 'form-control form-select'})
    )
    staff_type = forms.ChoiceField(
        choices=Employee.STAFF_TYPE_CHOICES,
        required=False,
        label="Select Staff Type",
        widget=forms.Select(attrs={'class': 'form-control form-select'})
    )
    location = forms.CharField(
        max_length=100,
        required=False,
        label="Select Location",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )