import random
import string, os, csv
import openpyxl
from django.conf import settings
from django.utils import timezone
from django.core.paginator import Paginator
from django.db.models import Sum, Count
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.urls import reverse
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.core.mail import EmailMessage, send_mail
from weasyprint import HTML
from .models import Employee, Payslip, Salary
from .forms import EmployeeForm, SalaryForm, EmployeeUploadForm, PayrollUploadForm


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
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            phone_number = form.cleaned_data['phone_number']
            if not Employee.objects.filter(name=name, email=email, phone_number=phone_number).exists():
                employee = form.save(commit=False)
                employee.employee_code = generate_reference_code(employee)
                employee.save()
                messages.success(request, 'Employee added successfully.')
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


@login_required
def upload_employees(request):
    if request.method == 'POST':
        form = EmployeeUploadForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = request.FILES['file']
            decoded_file = csv_file.read().decode('utf-8').splitlines()
            reader = csv.DictReader(decoded_file)
            for row in reader:
                if not Employee.objects.filter(name=row['name'], email=row['email']).exists():
                    employee = Employee.objects.create(
                        name=row['name'],
                        email=row['email'],
                        location=row['location'],
                        staff_type=row['staff_type'],
                        designation=row['designation'],
                        grade_level=row['grade_level'],
                        account_number=row['account_number'],
                        bank_name=row['bank_name'],
                        account_name=row['account_name'],
                        phone_number=row['phone_number'],
                    )
                    employee.employee_code = generate_reference_code(employee)
                    employee.save()
            messages.success(request, 'Employees uploaded successfully.')
            return redirect('core:employee_list')
        else:
            messages.error(request, 'Failed to upload employees. Please check the file format.')
    else:
        form = EmployeeUploadForm()
    return render(request, 'core/upload_employees.html', {'form': form})
    
    
@login_required
def export_employee_template(request):
    # Define the headers for the CSV file
    headers = [
        'name', 'email', 'location', 'staff_type', 'designation', 
        'grade_level', 'account_number', 'bank_name', 'account_name'
    ]

    # Create a CSV response
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=employee_template.csv'

    writer = csv.writer(response)
    writer.writerow(headers)

    return response

@login_required
def export_template(request):
    employees = Employee.objects.all()
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.title = 'Payroll Template'

    # Add headers
    headers = [
        'Reference Number', 'Name', 'Basic Pay', 'Rent Allowance', 'Transport Allowance', 
        'Meal Allowance', 'Utility Allowance', 'Other Allowances', 'Overtime', 'Arrears', 
        'Staff Loan Deduction', 'Rent Deduction', 'Medical Deduction', 'Pension Contribution', 
        'Shortage Deduction', 'Development Levy', 'Personal Income Tax'
    ]
    sheet.append(headers)

    # Add employee data
    for employee in employees:
        sheet.append([
            employee.employee_code, employee.name, '', '', '', '', '', '', '', '', 
            '', '', '', '', '', '', ''
        ])

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=payroll_template.xlsx'
    workbook.save(response)
    return response


@login_required
def import_payroll(request):
    if request.method == 'POST':
        form = PayrollUploadForm(request.POST, request.FILES)
        if form.is_valid():
            excel_file = request.FILES['file']
            workbook = openpyxl.load_workbook(excel_file)
            sheet = workbook.active
            for row in sheet.iter_rows(min_row=2, values_only=True):
                reference_number, name, basic_pay, rent_allowance, transport_allowance, \
                meal_allowance, utility_allowance, other_allowances, overtime, arrears, \
                staff_loan_deduction, rent_deduction, medical_deduction, pension_contribution, \
                shortage_deduction, development_levy, personal_income_tax = row
                employee = Employee.objects.get(reference_number=reference_number)
                Salary.objects.create(
                    employee=employee,
                    basic_pay=basic_pay,
                    rent_allowance=rent_allowance,
                    transport_allowance=transport_allowance,
                    meal_allowance=meal_allowance,
                    utility_allowance=utility_allowance,
                    other_allowances=other_allowances,
                    overtime=overtime,
                    arrears=arrears,
                    staff_loan_deduction=staff_loan_deduction,
                    rent_deduction=rent_deduction,
                    medical_deduction=medical_deduction,
                    pension_contribution=pension_contribution,
                    shortage_deduction=shortage_deduction,
                    development_levy=development_levy,
                    personal_income_tax=personal_income_tax
                )
            messages.success(request, 'Payroll imported successfully.')
            return redirect('core:salary_list')
    else:
        form = PayrollUploadForm()
    return render(request, 'core/import_payroll.html', {'form': form})


@login_required
def bulk_send_payslips(request):
    if request.method == 'GET' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        month = request.GET.get('month')
        year, month = map(int, month.split('-'))
        salaries = Salary.objects.filter(salary_date__year=year, salary_date__month=month)
        count = salaries.count()
        return JsonResponse({'count': count})

    if request.method == 'POST':
        month = request.POST.get('month')
        year, month = map(int, month.split('-'))
        salaries = Salary.objects.filter(salary_date__year=year, salary_date__month=month)
        for salary in salaries:
            payslip = Payslip.objects.get(salary=salary)
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
        messages.success(request, f'{salaries.count()} payslips sent successfully.')
        return redirect('core:dashboard')
    return render(request, 'core/bulk_send_payslips.html')