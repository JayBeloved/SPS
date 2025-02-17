from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('employees/', views.employee_list, name='employee_list'),
    path('employees/add/', views.employee_add, name='employee_add'),
    path('employees/update/<int:pk>/', views.employee_update, name='employee_update'),
    path('employees/delete/<int:pk>/', views.employee_delete, name='employee_delete'),
    path('salaries/', views.salary_list, name='salary_list'),
    path('salaries/add/', views.salary_add, name='salary_add'),
    path('salaries/update/<int:pk>/', views.salary_update, name='salary_update'),
    path('salaries/delete/<int:pk>/', views.salary_delete, name='salary_delete'),
    path('salaries/<int:pk>/payslip', views.generate_payslip, name='generate_payslip'),
    path('payslips/', views.payslip_list, name='payslip_list'),
    path('payslip/view/<int:pk>/', views.view_payslip, name='view_payslip'),
    path('payslip/send/<int:pk>/', views.send_payslip_email, name='send_payslip_email'),
    path('test-email/', views.test_email, name='test_email'),
    path('upload-employees/', views.upload_employees, name='upload_employees'),
    path('export-template/', views.export_template, name='export_template'),
    path('import-payroll/', views.import_payroll, name='import_payroll'),
    path('bulk-send-payslips/', views.bulk_send_payslips, name='bulk_send_payslips'),
    path('export-employee-template/', views.export_employee_template, name='export_employee_template'),
     path('reports/monthly-payroll-summary/', views.monthly_payroll_summary, name='monthly_payroll_summary'),
    path('reports/employee-compensation/', views.employee_compensation_report, name='employee_compensation_report'),
    path('management-dashboard/', views.management_dashboard, name='management_dashboard'), 
    
]