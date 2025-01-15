import random
import string, os
from django.conf import settings
from django.utils import timezone
from django.core.paginator import Paginator
from django.db.models import Sum, Count
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.urls import reverse
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.core.mail import EmailMessage, send_mail
from weasyprint import HTML
from .models import Employee, Payslip, Salary
from .forms import EmployeeForm, SalaryForm


# Create your views here.
@login_required
def dashboard(request):
    total_employees = Employee.objects.count()
    total_salary_last_month = Payslip.objects.filter(date__month=timezone.now().month-1).aggregate(Sum('net_pay'))['net_pay__sum'] or 0
    payrolls_processed = Payslip.objects.count()

    # Total salary paid per month
    salary_per_month = Payslip.objects.values('date__month').annotate(total_salary=Sum('net_pay')).order_by('date__month')

    # Total payrolls processed per month
    payrolls_per_month = Payslip.objects.values('date__month').annotate(total_payrolls=Count('id')).order_by('date__month')

    # Fetch list of employees and payslips
    employees = Employee.objects.all()
    payslips = Payslip.objects.all()

    context = {
        'total_employees': total_employees,
        'total_salary_last_month': total_salary_last_month,
        'payrolls_processed': payrolls_processed,
        'salary_per_month': salary_per_month,
        'payrolls_per_month': payrolls_per_month,
        'employees': employees,
        'payslips': payslips,
    }

    return render(request, 'core/dashboard.html', context)

@login_required
def employee_list(request):
    employees = Employee.objects.all()
    paginator = Paginator(employees, 10)  # Show 10 employees per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    form = EmployeeForm()
    return render(request, 'core/employee_dashboard.html', {'page_obj': page_obj, 'form': form})

@login_required
def employee_add(request):
    if request.method == 'POST':
        form = EmployeeForm(request.POST)
        if form.is_valid():
            employee = form.save(commit=False)
            employee.employee_code = generate_reference_code(employee)
            employee.save()
            return redirect('core:employee_list')
    return redirect('core:employee_list')

@login_required
def employee_update(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    if request.method == 'POST':
        form = EmployeeForm(request.POST, instance=employee)
        if form.is_valid():
            form.save()
            return redirect('core:employee_list')
    else:
        form = EmployeeForm(instance=employee)
    return render(request, 'core/edit_employee.html', {'form': form, 'employee': employee})

@login_required
def employee_delete(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    if request.method == 'POST':
        employee.delete()
        return redirect('core:employee_list')
    return redirect('core:employee_list')

def generate_reference_code(employee):
    count = Employee.objects.filter(location=employee.location, staff_type=employee.staff_type).count() + 1
    random_code = ''.join(random.choices(string.ascii_letters + string.digits, k=3))
    return f"RUN/MP/{employee.staff_type}/{random_code}/{count}"

@login_required
def salary_list(request):
    salaries = Salary.objects.all()
    paginator = Paginator(salaries, 10)  # Show 10 salaries per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    form = SalaryForm()
    return render(request, 'core/salary_dashboard.html', {'page_obj': page_obj, 'form': form})

@login_required
def salary_add(request):
    if request.method == 'POST':
        form = SalaryForm(request.POST)
        if form.is_valid():
            salary = form.save()
            # Calculate gross pay, total deductions, and net pay
            gross_pay = (
                salary.basic_pay +
                salary.rent_allowance +
                salary.transport_allowance +
                salary.meal_allowance +
                salary.utility_allowance +
                salary.other_allowances +
                salary.overtime +
                salary.arrears
            )
            total_deductions = (
                salary.staff_loan_deduction +
                salary.rent_deduction +
                salary.medical_deduction +
                salary.pension_contribution +
                salary.shortage_deduction +
                salary.development_levy +
                salary.personal_income_tax
            )
            net_pay = gross_pay - total_deductions

            # Create a corresponding payslip record
            Payslip.objects.create(
                employee=salary.employee,
                salary=salary,
                date=salary.salary_date,
                gross_pay=gross_pay,
                total_deductions=total_deductions,
                net_pay=net_pay
            )
            return redirect('core:salary_list')
    return redirect('core:salary_list')
    

@login_required
def salary_update(request, pk):
    salary = get_object_or_404(Salary, pk=pk)
    if request.method == 'POST':
        form = SalaryForm(request.POST, instance=salary)
        if form.is_valid():
            form.save()
            return redirect('core:salary_list')
    else:
        form = SalaryForm(instance=salary)
    return render(request, 'core/edit_salary.html', {'form': form, 'salary': salary})

@login_required
def salary_delete(request, pk):
    salary = get_object_or_404(Salary, pk=pk)
    if request.method == 'POST':
        salary.delete()
        return redirect('core:salary_list')
    return redirect('core:salary_list')


def generate_payslip_pdf(payslip):
    salary = payslip.salary
    # Calculate gross pay, total deductions, and net pay
    gross_pay = (
        salary.basic_pay +
        salary.rent_allowance +
        salary.transport_allowance +
        salary.meal_allowance +
        salary.utility_allowance +
        salary.other_allowances +
        salary.overtime +
        salary.arrears
    )
    total_deductions = (
        salary.staff_loan_deduction +
        salary.rent_deduction +
        salary.medical_deduction +
        salary.pension_contribution +
        salary.shortage_deduction +
        salary.development_levy +
        salary.personal_income_tax
    )
    net_pay = gross_pay - total_deductions

    context = {
        'payslip': payslip,
        'salary': salary,
        'employee': payslip.employee,
        'company_name': 'Manna Palace',
        'company_logo': os.path.join(settings.STATIC_ROOT, 'assets/img/brand/logo.png'),
        'gross_pay': gross_pay,
        'total_deductions': total_deductions,
        'net_pay': net_pay
    }
    html_string = render_to_string('core/payslip.html', context)
    html = HTML(string=html_string, base_url=settings.BASE_DIR)
    return html


@login_required
def generate_payslip(request, pk):
    payslip = get_object_or_404(Payslip, pk=pk)
    html = generate_payslip_pdf(payslip)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename=payslip_{payslip.employee.name}_{payslip.date}.pdf'
    html.write_pdf(response)
    return response


@login_required
def payslip_list(request):
    payslips = Payslip.objects.all()
    paginator = Paginator(payslips, 10)  # Show 10 payslips per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'core/payslip_dashboard.html', {'page_obj': page_obj})

@login_required
def view_payslip(request, pk):
    payslip = get_object_or_404(Payslip, pk=pk)
    html = generate_payslip_pdf(payslip)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename=payslip_{payslip.employee.name}_{payslip.date}.pdf'
    html.write_pdf(response)
    return response



@login_required
def send_payslip_email(request, pk):
    payslip = get_object_or_404(Payslip, pk=pk)
    html = generate_payslip_pdf(payslip)
    pdf = html.write_pdf()

    email = EmailMessage(
        subject=f'Payslip for {payslip.employee.name}',
        body=f"Dear {payslip.employee.name},\nPlease find attached your payslip for the month of {payslip.date.strftime('%B')}.",
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[payslip.employee.email],
    )
    email.attach(f'payslip_{payslip.employee.employee_code}_{payslip.date}.pdf', pdf, 'application/pdf')
    email.send()

    return redirect('core:payslip_list')


def test_email(request):
    subject = 'Test Email'
    message = 'This is a test email.'
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = ['info.jaybeloved@gmail.com']  # Replace with your email address

    try:
        send_mail(subject, message, from_email, recipient_list)
        return HttpResponse('Email sent successfully.')
    except Exception as e:
        return HttpResponse(f'Error sending email: {e}')