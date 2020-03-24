from django.shortcuts import render, redirect
from schoolapp.models import Student, Portal
from .models import Feestructure


def accounts(request):
    form1f =Student.objects.filter(form = 1, gender = 'f').count()
    form1m =Student.objects.filter(form = 1 ,gender = 'm').count()
    form1 = form1f + form1m
    form2f =Student.objects.filter(form = 2, gender = 'f').count()
    form2m =Student.objects.filter(form = 2, gender = 'm').count()
    form2 = form2f + form2m
    form3f = Student.objects.filter(form = 3, gender = 'f').count()
    form3m = Student.objects.filter(form = 3, gender = 'm').count()
    form3 =form3f + form3m
    form4f = Student.objects.filter(form = 4, gender = 'f').count()
    form4m = Student.objects.filter(form = 4, gender = 'm').count()
    form4 = form4f + form4m
    girls_total = form1f + form2f + form3f + form4f
    boys_total = form1m + form2m + form3m + form4m
    school_total = girls_total + boys_total
    
    context = {
        "school_total":school_total,
        'girls_total':girls_total,
        'boys_total':boys_total,
        'form1f':form1f,
        'form1m':form1m,
        'form1':form1,
        'form2f':form2f,
        'form2m':form2m,
        'form2':form2,
        'form3f':form3f,
        'form3m':form3m,
        'form3':form3,
        'form4f':form4f,
        'form4m':form4m,
        'form4':form4,    
    }
    return render(request, 'accounts_front.html', context)

def enter_closing_balance(request):
    context = {}
    return render(request, "enter_closing_balance.html", context)

def enter_closing_balance_class(request, form, stream):
    portal = Portal.objects.get()
    if portal.term1bot == True:
        term = "term1"
    if portal.term2bot == True:
        term = "term2"
    if portal.term3bot == True:
        term = "term3"
    if portal.term1mot == True:
        term = "term1"
    if portal.term2mot == True:
        term = "term2"
    if portal.term3mot == True:
        term = "term3"
    if portal.term1eot == True:
        term = "term1"
    if portal.term2eot == True:
        term = "term2"
    if portal.term3eot == True:
        term = "term3"
    
    student_queryset = Student.objects.filter(form = form, stream = stream)
    for student in student_queryset:
        term_period = f"form{student.form}{term}_closing_balance"
        if getattr(student, term_period):
            student.balance = getattr(student, term_period)
    if request.method == "POST":
        print(request.POST)
        for student in Student.objects.all():
            if request.POST.get(str(student.id)):
                term_period = f"form{student.form}{term}_closing_balance"
                setattr(student, term_period, request.POST[str(student.id)])
                student.save()
        return redirect("accounts:accounts")
        
    context = {
        "term":term,
        "fee_structure":Feestructure.objects.get(),
        "student_queryset" :student_queryset,
    }
    return render(request, "enter_closing_balance_class.html", context)

def edit_fee_structure(request):
    if request.method == "POST":
        fee_structure = Feestructure.objects.get()
        fee_structure.term1 = request.POST['term1']
        fee_structure.term2 = request.POST['term2']
        fee_structure.term3 = request.POST['term3']
        fee_structure.save()
        return redirect("accounts:accounts")
    context = {
        "fee_structure" :Feestructure.objects.get()
    }
    return render(request, "edit_fee_structure.html", context)