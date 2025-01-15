from django.db import models

class Employee(models.Model):
    id = models.AutoField(primary_key=True)
    employee_code = models.CharField(max_length=25, unique=True)
    name = models.CharField(max_length=100)
    STAFF_TYPE_CHOICES = [
        ('SS', 'Senior Staff'),
        ('CoS', 'Contract Staff'),
        ('CaS', 'Casual Staff'),
    ]
    staff_type = models.CharField(max_length=3, choices=STAFF_TYPE_CHOICES)
    email = models.EmailField()
    designation = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    grade_level = models.CharField(max_length=10, null=True, blank=True)
    account_number = models.CharField(max_length=20, null=True, blank=True)
    bank_name = models.CharField(max_length=50, null=True, blank=True)
    account_name = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.name

class Salary(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    basic_pay = models.DecimalField(max_digits=10, decimal_places=2)
    no_of_days = models.IntegerField()
    actual_attendance = models.IntegerField()
    # Allowances
    rent_allowance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    transport_allowance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    meal_allowance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    utility_allowance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    other_allowances = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    overtime = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    arrears = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    # Deductions
    staff_loan_deduction = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    rent_deduction = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    medical_deduction = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    pension_contribution = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    shortage_deduction = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    development_levy = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    personal_income_tax = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    salary_date = models.DateField()

    def __str__(self):
        return f"{self.employee.name} - Salary for {self.salary_date}"

    class Meta:
        verbose_name = "Salary"
        verbose_name_plural = "Salaries"

class Payslip(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    salary = models.ForeignKey(Salary, on_delete=models.CASCADE, default=2)
    date = models.DateField()
    gross_pay = models.DecimalField(max_digits=10, decimal_places=2)
    total_deductions = models.DecimalField(max_digits=10, decimal_places=2)
    net_pay = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.employee.name} - Payslip for {self.date}"