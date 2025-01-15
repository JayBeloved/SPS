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
]