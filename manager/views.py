from django.shortcuts import render

# Create your views here.

def manager_dashboard(request):
    return render(request,'manager/manager_dashboard.html')
