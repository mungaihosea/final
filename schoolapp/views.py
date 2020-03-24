import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from io import BytesIO
import base64
import numpy as np
from zipfile import ZipFile

from django.shortcuts import render, get_object_or_404, redirect
from .models import Portal, Student, Subject, SubjectGradingSystem, Alumni, open_and_closing
from django.http import HttpResponse
from django.contrib.auth import authenticate,login as login_user, logout as logout_user
import json
from django.template.loader import get_template
from weasyprint import HTML
from django.db.models import Q
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from accounts.models import Feestructure
from django.contrib.auth.models import User

def average_remark(score):
    score = int(score)
    if 80 <= score <= 100:
        return "Excellent"
    if 70 <= score <= 79:
        return "Very Good"
    if 60 <= score <= 69:
        return "Good"
    if 50 <= score <= 59:
        return "Average"
    if 40 <= score <= 49:
        return "Put More Effort"
    if 0 <= score <= 39:
        return "Work Harder"

def average_remark_kiswahili(score):
    score = int(score)
    if 80 <= score <= 100:
        return "Hongera"
    if 70 <= score <= 79:
        return "Kazi Nzuri"
    if 60 <= score <= 69:
        return "Vyema"
    if 50 <= score <= 59:
        return "vizuri"
    if 40 <= score <= 49:
        return "umejaribu"
    if 0 <= score <= 39:
        return "Tia Bidii"


def average(first_exam, second_exam, third_exam):
    soln = (((int(first_exam) + int(third_exam))/2) * (30/100)) + (int(second_exam) * (70/100))
    return round(soln)

def case2average(second_exam, third_exam):
    soln = (int(second_exam )* (70/100)) + (int(third_exam) * (30/100))
    return round(soln)

def specialaverage(first_exam, third_exam):
    soln = (int(first_exam) + int(third_exam))/2
    return round(soln)

def logout(request):
    logout_user(request)
    return redirect("schoolapp:login")

def login(request):
    if request.method == "POST":
        if request.POST.get("pass") and request.POST.get("username"):
            username = request.POST.get("username")
            password = request.POST.get("pass")
            user = authenticate(request, username = username, password = password)
            if user is not None:
                login_user(request, user)
                return redirect("schoolapp:dash")

    context = {}
    return render(request, 'login.html', context)



def dash(request):
    if request.user.teacher.is_accountant:
        return redirect("accounts:accounts")
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
        "subject_queryset":Subject.objects.all(),
    }
    return render(request, "dashboard.html", context)

def portal(request):
    if request.GET.get('timestamp'):
        portal = Portal.objects.get()
        portal.term1bot = False
        portal.term2bot = False
        portal.term3bot = False
        portal.term1mot = False
        portal.term2mot = False
        portal.term3mot = False
        portal.term1eot = False
        portal.term2eot = False
        portal.term3eot = False
        setattr(portal, request.GET['timestamp'], True)
        portal.save()
        return redirect('schoolapp:dash')

        
    context = {
        "portal":Portal.objects.get()
    }
    return render(request, "portal.html", context)

def enter_scores(request):
    context = {
        "portal":Portal.objects.get()
    }
    return render(request, "enter_scores.html", context)
def enter_scores_timestamp(request, timestamp, form):
    
    context = {
        "timestamp":timestamp,
        "form":form,
        "teacher_subject_queryset":request.user.teacher.subjects.all()
    }
    return render(request, "enter_scores_subject.html", context)

def score_sheet(request):
    if request.method == "POST":
        key_list = []
        for x in request.POST.keys():
            key_list.append(x)
        key_list.remove("csrfmiddlewaretoken")
        for key in key_list:
            student = get_object_or_404(Student, id = key)
            exam_period = f"form{student.form}_{request.user.teacher.selected_timestamp}"
            if getattr(student, exam_period):
                result = json.loads(getattr(student, exam_period))
                result[get_object_or_404(Subject, id = int(request.GET['subject_id'])).subject_name] = int(request.POST[key])
                setattr(student,exam_period, json.dumps(result))
                student.save()
            else:
                setattr(student, exam_period, json.dumps({get_object_or_404(Subject, id = int(request.GET['subject_id'])).subject_name : request.POST[key]}))
                student.save()

        return redirect("schoolapp:dash")

    subject = get_object_or_404(Subject, id = int(request.GET['subject_id']))
    student_queryset = subject.student_set.filter(form = int(request.GET['form']))
    student_queryset = student_queryset.filter(stream = request.GET['stream'])
    for student in student_queryset:
        exam_period = f"form{student.form}_{request.GET['timestamp']}"
        scores = getattr(student, exam_period)
        if scores == "" or scores == None:
            student.score = ""
        else:
            try:
                student.score = json.loads(scores)[get_object_or_404(Subject, id = int(request.GET['subject_id'])).subject_name]
            except KeyError:
                student.score = ''

    request.user.teacher.selected_timestamp = request.GET['timestamp']
    request.user.teacher.selected_subject = subject.id
    request.user.teacher.save()
    context = {
        "subject":subject.subject_name,
        "stream":request.GET['stream'],
        "form":request.GET['form'],
        "student_queryset":student_queryset
    }
    return render(request, "score_sheet.html", context)


#this function generates results for an independent exam
def generate_results(request):
    if request.GET.get('timestamp'):
        timestamp = request.GET['timestamp']
        reports_list = []
        for student in Student.objects.all():
            exam_period = f"form{student.form}_{timestamp}"
            if getattr(student, exam_period):
                result = json.loads(getattr(student, exam_period))
                if result.get('english'):
                    result['english_points'] = award_grade(student.form, get_object_or_404(Subject, subject_name = "english"),int(result['english']))[0]
                    result['english_grade'] = award_grade(student.form, get_object_or_404(Subject, subject_name = "english"),int(result['english']))[1]
                else:
                    result['english'] = 0
                    result['english_points'] = award_grade(student.form, get_object_or_404(Subject, subject_name = "english"),int(result['english']))[0]
                    result['english_grade'] = award_grade(student.form, get_object_or_404(Subject, subject_name = "english"),int(result['english']))[1]

                if result.get('kiswahili'):
                    result['kiswahili_points'] = award_grade(student.form, get_object_or_404(Subject, subject_name = "kiswahili"),int(result['kiswahili']))[0]
                    result['kiswahili_grade'] = award_grade(student.form, get_object_or_404(Subject, subject_name = "kiswahili"),int(result['kiswahili']))[1]
                else: 
                    result['kiswahili'] = 0
                    result['kiswahili_points'] = award_grade(student.form, get_object_or_404(Subject, subject_name = "kiswahili"),int(result['kiswahili']))[0]
                    result['kiswahili_grade'] = award_grade(student.form, get_object_or_404(Subject, subject_name = "kiswahili"),int(result['kiswahili']))[1]

                if result.get('mathematics'): 
                    result['mathematics_points'] = award_grade(student.form, get_object_or_404(Subject, subject_name = "mathematics"),int(result['mathematics']))[0]
                    result['mathematics_grade']= award_grade(student.form, get_object_or_404(Subject, subject_name = "mathematics"),int(result['mathematics']))[1]
                else:
                    result['mathematics'] = 0
                    result['mathematics_points'] = award_grade(student.form, get_object_or_404(Subject, subject_name = "mathematics"),int(result['mathematics']))[0]
                    result['mathematics_grade']= award_grade(student.form, get_object_or_404(Subject, subject_name = "mathematics"),int(result['mathematics']))[1]

                if result.get('chemistry'):
                    result['chemistry_points'] = award_grade(student.form, get_object_or_404(Subject, subject_name = "chemistry"),int(result['chemistry']))[0]
                    result['chemistry_grade']= award_grade(student.form, get_object_or_404(Subject, subject_name = "chemistry"),int(result['chemistry']))[1]
                else:
                    result['chemistry'] = 0
                    result['chemistry_points'] = award_grade(student.form, get_object_or_404(Subject, subject_name = "chemistry"),int(result['chemistry']))[0]
                    result['chemistry_grade']= award_grade(student.form, get_object_or_404(Subject, subject_name = "chemistry"),int(result['chemistry']))[1]

                if result.get('physics'):
                    result['physics_points'] = award_grade(student.form, get_object_or_404(Subject, subject_name = "physics"),int(result['physics']))[0]
                    result['physics_grade']= award_grade(student.form, get_object_or_404(Subject, subject_name = "physics"),int(result['physics']))[1]
                else:
                    result['physics'] = 0
                    result['physics_points'] = award_grade(student.form, get_object_or_404(Subject, subject_name = "physics"),int(result['physics']))[0]
                    result['physics_grade']= award_grade(student.form, get_object_or_404(Subject, subject_name = "physics"),int(result['physics']))[1]

                if result.get('biology'):
                    result['biology_points'] = award_grade(student.form, get_object_or_404(Subject, subject_name = "biology"),int(result['biology']))[0]
                    result['biology_grade']= award_grade(student.form, get_object_or_404(Subject, subject_name = "biology"),int(result['biology']))[1]
                else:
                    result['biology'] = 0
                    result['biology_points'] = award_grade(student.form, get_object_or_404(Subject, subject_name = "biology"),int(result['biology']))[0]
                    result['biology_grade']= award_grade(student.form, get_object_or_404(Subject, subject_name = "biology"),int(result['biology']))[1]

                if result.get('cre'):
                    result['cre_points'] = award_grade(student.form, get_object_or_404(Subject, subject_name = "cre"),int(result['cre']))[0]
                    result['cre_grade']= award_grade(student.form, get_object_or_404(Subject, subject_name = "cre"),int(result['cre']))[1]
                else:
                    result['cre'] = 0
                    result['cre_points'] = award_grade(student.form, get_object_or_404(Subject, subject_name = "cre"),int(result['cre']))[0]
                    result['cre_grade']= award_grade(student.form, get_object_or_404(Subject, subject_name = "cre"),int(result['cre']))[1]

                if result.get('history'):
                    result['history_points'] = award_grade(student.form, get_object_or_404(Subject, subject_name = "history"),int(result['history']))[0]
                    result['history_grade']= award_grade(student.form, get_object_or_404(Subject, subject_name = "history"),int(result['history']))[1]
                else:
                    result['history'] = 0
                    result['history_points'] = award_grade(student.form, get_object_or_404(Subject, subject_name = "history"),int(result['history']))[0]
                    result['history_grade']= award_grade(student.form, get_object_or_404(Subject, subject_name = "history"),int(result['history']))[1]

                if result.get('geography'):
                    result['geography_points'] = award_grade(student.form, get_object_or_404(Subject, subject_name = "geography"),int(result['geography']))[0]
                    result['geography_grade']= award_grade(student.form, get_object_or_404(Subject, subject_name = "geography"),int(result['geography']))[1]
                else:
                    result['geography'] = 0
                    result['geography_points'] = award_grade(student.form, get_object_or_404(Subject, subject_name = "geography"),int(result['geography']))[0]
                    result['geography_grade']= award_grade(student.form, get_object_or_404(Subject, subject_name = "geography"),int(result['geography']))[1]

                if result.get('agriculture'):
                    result['agriculture_points'] = award_grade(student.form, get_object_or_404(Subject, subject_name = "agriculture"),int(result['agriculture']))[0]
                    result['agriculture_grade']= award_grade(student.form, get_object_or_404(Subject, subject_name = "agriculture"),int(result['agriculture']))[1]    
                else:
                    result['agriculture'] = 0
                    result['agriculture_points'] = award_grade(student.form, get_object_or_404(Subject, subject_name = "agriculture"),int(result['agriculture']))[0]
                    result['agriculture_grade']= award_grade(student.form, get_object_or_404(Subject, subject_name = "agriculture"),int(result['agriculture']))[1]    

                if result.get('bussiness'):
                    result['bussiness_points'] = award_grade(student.form, get_object_or_404(Subject, subject_name = "bussiness"),int(result['bussiness']))[0]
                    result['bussiness_grade']= award_grade(student.form, get_object_or_404(Subject, subject_name = "bussiness"),int(result['bussiness']))[1]
                else:
                    result['bussiness'] = 0
                    result['bussiness_points'] = award_grade(student.form, get_object_or_404(Subject, subject_name = "bussiness"),int(result['bussiness']))[0]
                    result['bussiness_grade']= award_grade(student.form, get_object_or_404(Subject, subject_name = "bussiness"),int(result['bussiness']))[1]    

                result['total_points'] = int(result['mathematics_points']) + int(result['english_points']) + int(result['kiswahili_points']) + int(result['chemistry_points']) + int(result['physics_points']) + int(result['biology_points']) + int(result['cre_points']) + int(result['history_points']) + int(result['geography_points']) + int(result['agriculture_points']) + int(result['bussiness_points'])
                result['form'] = student.form
                result['stream'] = student.stream
                result['student_id'] = student.id
                result['student_name'] = student.student_name
                result['adm_no'] = student.adm_no
                result['exam_period'] = exam_period
                reports_list.append(result)
                setattr(student, exam_period, json.dumps(result))
                student.save()

        #getting the class rank and stream rank
        for form in [1, 2, 3, 4]:
            reports = []
            for x in reports_list:
                if int(x['form']) == int(form):
                    reports.append(x)
            reports = sorted(reports, key = lambda i: i['total_points'], reverse = True)
            for report in reports:
                report['class_rank'] = reports.index(report) + 1
            for y in reports:
                for z in reports:
                    if y['total_points'] == z['total_points']:
                        if int(y['class_rank']) > int(z['class_rank']):
                            y['class_rank'] = z['class_rank']
                        if int(y['class_rank']) < int(z['class_rank']):
                            z['class_rank'] = y['class_rank']

            for stream in ['a','b','c']:
                stream_reports = []
                for report in reports:
                    if report['stream'] == stream:
                        stream_reports.append(report) 
                stream_reports = sorted(stream_reports, key = lambda i: i['total_points'], reverse = True)
                for report in stream_reports:
                    report['stream_rank'] = stream_reports.index(report) + 1
                for y in stream_reports:
                    for z in stream_reports:
                        if y['total_points'] == z['total_points']:
                            if int(y['stream_rank']) > int(z['stream_rank']):
                                y['stream_rank'] = z['stream_rank']
                            if int(y['stream_rank']) < int(z['stream_rank']):
                                z['stream_rank'] = y['stream_rank']
                for report in stream_reports:
                    for student in Student.objects.all():
                        if student.id == int(report["student_id"]):
                            result = json.loads(getattr(student, report['exam_period']))
                            result['class_rank'] = report['class_rank']
                            result['stream_rank'] = report['stream_rank']
                            setattr(student, report['exam_period'], json.dumps(result))
                            student.save()
        return redirect(f"/view_reports/{request.GET['timestamp']}/")
    context = {
        "portal":Portal.objects.get(),
    }
    return render(request, "generate_results.html", context)


#this function reads and awards grade and points to marks
def award_grade(form, subject, score):
    grading_system = get_object_or_404(SubjectGradingSystem, form = form, subject = subject)
    if grading_system.Aplain_upper >= score >= grading_system.Aplain_lower:
        return (grading_system.Aplain_points, "A")
    if grading_system.Aminus_upper >= score >= grading_system.Aminus_lower:
        return [grading_system.Aminus_points, "A-"]
    if grading_system.Bplus_upper >= score >= grading_system.Bplus_lower:
        return (grading_system.Bplus_points, "B+")
    if grading_system.Bplain_upper >= score >= grading_system.Bplain_lower:
        return (grading_system.Bplain_points, "B")
    if grading_system.Bminus_upper >= score >= grading_system.Bminus_lower:
        return (grading_system.Bminus_points, "B-")
    if grading_system.Cplus_upper >= score >= grading_system.Cplus_lower:
        return (grading_system.Cplus_points, "C+")
    if grading_system.Cplain_upper >= score >= grading_system.Cplain_lower:
        return (grading_system.Cplain_points, "C")
    if grading_system.Cminus_upper >= score >= grading_system.Cminus_lower:
        return (grading_system.Cminus_points, "C-")
    if grading_system.Dplus_upper >= score >= grading_system.Dplus_lower:
        return (grading_system.Dplus_points, "D+")
    if grading_system.Dplain_upper >= score >= grading_system.Dplain_lower:
        return (grading_system.Dplain_points, "D")
    if grading_system.Dminus_upper >= score >= grading_system.Dminus_lower:
        return (grading_system.Dminus_points, "D-")
    if grading_system.Eplain_upper>= score >= grading_system.Eplain_lower:
        return (grading_system.Eplain_points, "E")
    if grading_system.Fplain_upper>= score >= grading_system.Fplain_lower:
        return (grading_system.Fplain_points, "F")

def grading_system(request,form,subject_id):
    form = form
    subject = get_object_or_404(Subject, id = subject_id)
    current_grading_system = SubjectGradingSystem.objects.get(form = form, subject = subject)
    if request.method == 'POST':
        current_grading_system = SubjectGradingSystem.objects.get(form = form, subject = subject)
        # print(current_grading_system)
        current_grading_system.Aplain_upper = int(request.POST["Aplain_upper"])
        current_grading_system.Aplain_lower = int(request.POST["Aplain_lower"])
        current_grading_system.Aplain_points = int(request.POST["Aplain_points"])
        current_grading_system.Aminus_upper = int(request.POST["Aminus_upper"])
        current_grading_system.Aminus_lower = int(request.POST["Aminus_lower"])
        current_grading_system.Aminus_points = int(request.POST["Aminus_points"])
        current_grading_system.Bplus_upper = int(request.POST["Bplus_upper"])
        current_grading_system.Bplus_lower = int(request.POST["Bplus_lower"])
        current_grading_system.Bplus_points = int(request.POST["Bplus_points"])
        current_grading_system.Bplain_upper = int(request.POST["Bplain_upper"])
        current_grading_system.Bplain_lower = int(request.POST["Bplain_lower"])
        current_grading_system.Bplain_points = int(request.POST["Bplain_points"])
        current_grading_system.Bminus_upper = int(request.POST["Bminus_upper"])
        current_grading_system.Bminus_lower = int(request.POST["Bminus_lower"])
        current_grading_system.Bminus_points = int(request.POST["Bminus_points"])
        current_grading_system.Cplus_upper = int(request.POST["Cplus_upper"])
        current_grading_system.Cplus_lower = int(request.POST["Cplus_lower"])
        current_grading_system.Cplus_points = int(request.POST["Cplus_points"])
        current_grading_system.Cplain_upper = int(request.POST["Cplain_upper"])
        current_grading_system.Cplain_lower = int(request.POST["Cplain_lower"])
        current_grading_system.Cplain_points = int(request.POST["Cplain_points"])
        current_grading_system.Cminus_upper = int(request.POST["Cminus_upper"])
        current_grading_system.Cminus_lower = int(request.POST["Cminus_lower"])
        current_grading_system.Cminus_points = int(request.POST["Cminus_points"])
        current_grading_system.Dplus_upper = int(request.POST["Dplus_upper"])
        current_grading_system.Dplus_lower = int(request.POST["Dplus_lower"])
        current_grading_system.Dplus_points = int(request.POST["Dplus_points"])
        current_grading_system.Dplain_upper = int(request.POST["Dplain_upper"])
        current_grading_system.Dplain_lower = int(request.POST["Dplain_lower"])
        current_grading_system.Dplain_points = int(request.POST["Dplain_points"])
        current_grading_system.Dminus_upper = int(request.POST["Dminus_upper"])
        current_grading_system.Dminus_lower = int(request.POST["Dminus_lower"])
        current_grading_system.Dminus_points = int(request.POST["Dminus_points"])
        current_grading_system.Eplain_upper = int(request.POST["Eplain_upper"])
        current_grading_system.Eplain_lower = int(request.POST["Eplain_lower"])
        current_grading_system.Eplain_points = int(request.POST["Eplain_points"])
        current_grading_system.save()

    context = {
    "current_grading_system":current_grading_system,
    "form":form,
    "subject":subject,
    }
    return render(request, 'grading_system.html', context)

def edit_grading_system(request):
    form_queryset = [1, 2, 3, 4]
    subject_queryset = Subject.objects.all()
    context = {
        "form_queryset": form_queryset,
        "subject_queryset": subject_queryset
    }
    return render(request, "edit_grading_system.html", context)

def add_grading_stuff(request):
    subject_queryset = Subject.objects.filter(Q(subject_name = "english") | Q(subject_name = "kiswahili")| Q(subject_name = "geography") | Q(subject_name = "history") | Q(subject_name = "bussiness") |Q(subject_name = "agriculture") | Q(subject_name = "cre"))
    for form in [1, 2, 3, 4]:
        for subject in subject_queryset:
            SubjectGradingSystem.objects.create(
            form = form,
            subject = subject,
            Aplain_upper = 100,
            Aplain_lower = 80,
            Aplain_points = 12,
            Aminus_upper = 79,
            Aminus_lower = 75,
            Aminus_points = 11,
            Bplus_upper = 74,
            Bplus_lower = 70,
            Bplus_points = 10,
            Bplain_upper = 69,
            Bplain_lower = 65,
            Bplain_points = 9,
            Bminus_upper = 64,
            Bminus_lower = 60,
            Bminus_points = 8,
            Cplus_upper = 59,
            Cplus_lower = 55,
            Cplus_points = 7,
            Cplain_upper = 54,
            Cplain_lower = 50,
            Cplain_points = 6,
            Cminus_upper = 49,
            Cminus_lower = 45,
            Cminus_points = 5,
            Dplus_upper = 44,
            Dplus_lower = 40,
            Dplus_points = 4,
            Dplain_upper = 39,
            Dplain_lower = 35,
            Dplain_points = 3,
            Dminus_upper = 34,
            Dminus_lower = 30,
            Dminus_points = 2,
            Eplain_upper = 29,
            Eplain_lower = 1,
            Eplain_points = 1,
            Fplain_upper = 0,
            Fplain_lower = 0,
            Fplain_points = 0
            )
    return HttpResponse("added fake")


def view_reports(request, timestamp):    
    if request.GET.get("form"):
        student_queryset = Student.objects.filter(form = int(request.GET['form']))
        if request.GET.get('stream'):
            # print("yeah this is it")
            student_queryset = student_queryset.filter(stream = request.GET.get('stream'))
        result_queryset = []
        for student in student_queryset:
            exam_period = f"form{student.form}_{timestamp}"
            if getattr(student, exam_period):
                result_queryset.append(json.loads(getattr(student, exam_period)))
        context = {
            "form":request.GET.get("form"),
            "result_queryset":sorted(result_queryset, key = lambda i: i['total_points'], reverse = True),
        }
        template = get_template('results_sheet_template.html')
        html = template.render(context)
        results_sheet_pdf = HTML(string = html, base_url =  request.build_absolute_uri()).write_pdf()
        if request.method == "POST":
            return HttpResponse(results_sheet_pdf, content_type="application/pdf")
        return render(request, "results_sheet.html", context)
    context = {}
    return render(request, "view_reports.html",context)


def generate_endterm_reports(request):
    context = {
        "portal":Portal.objects.get(),
    }
    return render(request, "generate_endterm_reports.html", context)


def findstudent(request):
    try:
        if request.GET['key']:
            search_key = request.GET['key']
            search_queryset = Student.objects.filter(Q(student_name__contains = search_key)|Q(adm_no__contains = search_key)).distinct()
    except KeyError:
        search_queryset = []
    context = {
        "search_queryset":search_queryset,
    }
    return render(request, "find_student.html", context)

def edit_student(request, student_id):
    student = get_object_or_404(Student, id = student_id)
    if request.method == "POST":
        if request.FILES.get('photo'):
            myfile = request.FILES['photo']
            fs = FileSystemStorage()
            filename = fs.save(myfile.name, myfile)
            print("this is the filename",filename)
        else:
            filename = None
        if request.POST.get('date_of_birth'):
            date_of_birth = request.POST['date_of_birth']
        else:
            date_of_birth = None
        
        if request.POST.get("kcpe"):
            kcpe = request.POST['kcpe']
        else:
            kcpe = None
        if request.POST.get("upi_no"):
            upi_no = request.POST['upi_no']
        else:
            upi_no = None
        if request.POST.get("kcpe_index"):
            kcpe_index = request.POST['kcpe_index']
        else:
            kcpe_index = None
        if request.POST.get("birth_cert_no"):
            birth_cert_no = request.POST["birth_cert_no"]
        else:
            birth_cert_no = None
        if request.POST.get("adm_date"):
            adm_date = request.POST['adm_date']
        else:
            adm_date = None

        student.student_name = request.POST.get("student_name")
        student.date_of_birth = date_of_birth
        student.adm_no = request.POST.get('adm_no')
        student.kcpe = kcpe
        if filename is not None:
            student.student_photo = filename
        student.upi_no = upi_no
        student.kcpe_index = kcpe_index
        student.birth_cert = birth_cert_no
        student.adm_date = adm_date

        student.save()
        return redirect("schoolapp:find_student")

    context = {
        "student":student,
    }
    return render(request, "edit_student.html", context)


def add_student(request):

    if request.method == "POST":
        if request.FILES.get('photo'):
            myfile = request.FILES['photo']
            fs = FileSystemStorage()
            filename = fs.save(myfile.name, myfile)
        else:
            filename = None
        if request.POST.get('date_of_birth'):
            date_of_birth = request.POST['date_of_birth']
        else:
            date_of_birth = None
        
        if request.POST.get("kcpe"):
            kcpe = request.POST['kcpe']
        else:
            kcpe = None
        if request.POST.get("upi_no"):
            upi_no = request.POST['upi_no']
        else:
            upi_no = None
        if request.POST.get("kcpe_index"):
            kcpe_index = request.POST['kcpe_index']
        else:
            kcpe_index = None
        if request.POST.get("birth_cert_no"):
            birth_cert_no = request.POST["birth_cert_no"]
        else:
            birth_cert_no = None
        if request.POST.get("adm_date"):
            adm_date = request.POST['adm_date']
        else:
            adm_date = None

        student = Student.objects.create(
            student_name = request.POST.get("student_name"),
            date_of_birth = date_of_birth,
            adm_no = request.POST.get('adm_no'),
            gender = request.POST.get('gender'),
            kcpe = kcpe,
            student_photo = filename,
            stream = request.POST.get("stream"),
            form = request.POST.get("form"),
            phone_number = request.POST.get('student_phone'),
            parent_phone_number = request.POST.get('parent_phone'),
            guardian_phone = request.POST.get('guardian_phone'),
            parent_name = request.POST.get('parent_name'),
            guardian_name = request.POST.get('guardian_name'),
            county = request.POST.get('county'),
            upi_no = upi_no,
            kcpe_index = kcpe_index,
            birth_cert = birth_cert_no,
            adm_date = adm_date,
        )
        subject_queryset = Subject.objects.all()
        student.subjects.set(subject_queryset)
        student.save()
        return redirect("schoolapp:dash")

    # if request.method == "POST":
    #     student = Student.objects.create(
    #         student_name = request.POST.get("student_name"),
    #         # date_of_birth = request.POST.get('date_of_birth'),
    #         adm_no = request.POST.get('adm_no'),
    #         gender = request.POST.get('gender'),
    #         # kcpe = request.POST.get('kcpe'),
    #         student_photo = request.POST.get('photo'),
    #         stream = request.POST.get("stream"),
    #         form = request.POST.get("form"),
    #         phone_number = request.POST.get('student_phone'),
    #         parent_phone_number = request.POST.get('parent_phone'),
    #         guardian_phone = request.POST.get('guardian_phone'),
    #         parent_name = request.POST.get('parent_name'),
    #         guardian_name = request.POST.get('guardian_name'),
    #         county = request.POST.get('county'),
    #         upi_no = request.POST.get("upi_no"),
    #         # kcpe_index = request.POST[('kcpe_index'),
    #         # birth_cert = request.POST.get('birth_cert_no'),
    #         # adm_date = request.POST.get('adm_date'),
    #     )
        
        # return redirect("schoolapp:dash")

    context = {}
    return render(request, "add_student.html", context)


def endterm_reports(request, timestamp):
    if request.method == "POST":
        dates = open_and_closing.objects.get()
        dates.closing_date = request.POST['closing_date']
        dates.opening_date = request.POST['opening_date']
        dates.save()

    if request.GET.get('form'):
        form = request.GET.get('form')
        student_queryset = Student.objects.filter(form = form)
        portal = Portal.objects.get()
        #getting which term it is
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
        #getting the next term
        if term == "term1":
            next_term = "term2"
        if term == "term2":
            next_term = "term3"
        if term == "term3":
            next_term = "term1"
        #creating a responce and zip file for the report cards
        response = HttpResponse(content_type= 'application/zip')
        zf = ZipFile(response , 'w')
        for student in student_queryset:
            context = {}
            #bot first exam
            term_period = f"form{student.form}{term}_closing_balance"
            exam_period = f"form{student.form}_{timestamp}bot"
            if getattr(student, exam_period):
                # print(getattr(student, term_period))
                result = json.loads(getattr(student, exam_period))
                context['student']= {
                    "closing_balance":getattr(student, term_period),
                    "next_term_balance":getattr(Feestructure.objects.get(), next_term),
                    "name": student.student_name,
                    "form": student.form,
                    "adm_no":student.adm_no,
                    "stream":student.stream
                }
                if context['student']['closing_balance'] and context['student']['next_term_balance']:
                    context['student']['next_term_payable'] = context['student']['closing_balance'] + context['student']['next_term_balance']

                context['first_exam']={
                    "total_points":result['total_points'],
                    "class_position":result['class_rank'],
                    "stream_position":result['stream_rank'],
                    "mathematics":result['mathematics'],
                    "mathematics_grade":result['mathematics_grade'],
                    "english":result['english'],
                    "english_grade":result['english_grade'],
                    "kiswahili":result['kiswahili'],
                    "kiswahili_grade":result['kiswahili_grade'],
                    "chemistry":result['chemistry'],
                    "chemistry_grade":result['chemistry_grade'],
                    "biology":result['biology'],
                    "biology_grade":result['biology_grade'],
                    "physics":result['physics'],
                    "physics_grade":result['physics_grade'],
                    "cre":result['cre'],
                    "cre_grade":result['cre_grade'],
                    "history":result['history'],
                    "history_grade":result['history_grade'],
                    "geography":result['geography'],
                    "geography_grade":result['geography_grade'],
                    "bussiness":result['bussiness'],
                    "bussiness_grade":result['bussiness_grade'],
                    "agriculture":result['agriculture'],
                    "agriculture_grade":result['agriculture_grade'],
                }
                # print(context)
            #mot second exam
            term_period = f"form{student.form}{term}_closing_balance"
            exam_period = f"form{student.form}_{timestamp}mot"
            if getattr(student, exam_period):
                result = json.loads(getattr(student, exam_period))
                context['student']= {
                    "closing_balance":getattr(student, term_period),
                    "next_term_balance":getattr(Feestructure.objects.get(), next_term),
                    "name": student.student_name,
                    "form": student.form,
                    "adm_no":student.adm_no,
                    "stream":student.stream
                }
                if context['student']['closing_balance'] and context['student']['next_term_balance']:
                    context['student']['next_term_payable'] = context['student']['closing_balance'] + context['student']['next_term_balance']
                    
                context['second_exam'] = {
                    "total_points":result['total_points'],
                    "class_position":result['class_rank'],
                    "stream_position":result['stream_rank'],
                    "mathematics":result['mathematics'],
                    "mathematics_grade":result['mathematics_grade'],
                    "english":result['english'],
                    "english_grade":result['english_grade'],
                    "kiswahili":result['kiswahili'],
                    "kiswahili_grade":result['kiswahili_grade'],
                    "chemistry":result['chemistry'],
                    "chemistry_grade":result['chemistry_grade'],
                    "biology":result['biology'],
                    "biology_grade":result['biology_grade'],
                    "physics":result['physics'],
                    "physics_grade":result['physics_grade'],
                    "cre":result['cre'],
                    "cre_grade":result['cre_grade'],
                    "history":result['history'],
                    "history_grade":result['history_grade'],
                    "geography":result['geography'],
                    "geography_grade":result['geography_grade'],
                    "bussiness":result['bussiness'],
                    "bussiness_grade":result['bussiness_grade'],
                    "agriculture":result['agriculture'],
                    "agriculture_grade":result['agriculture_grade'],
                }
                # print(context)
            #eot third exam
            term_period = f"form{student.form}{term}_closing_balance"
            exam_period = f"form{student.form}_{timestamp}eot"
            if getattr(student, exam_period):
                result = json.loads(getattr(student, exam_period))
                context['student']= {
                    "closing_balance":getattr(student, term_period),
                    "next_term_balance":getattr(Feestructure.objects.get(), next_term),
                    "name": student.student_name,
                    "form": student.form,
                    "adm_no":student.adm_no,
                    "stream":student.stream
                }
                if context['student']['closing_balance'] and context['student']['next_term_balance']:
                    context['student']['next_term_payable'] = context['student']['closing_balance'] + context['student']['next_term_balance']
                    
                context['third_exam'] = {
                    "total_points":result['total_points'],
                    "class_position":result['class_rank'],
                    "stream_position":result['stream_rank'],
                    "mathematics":result['mathematics'],
                    "mathematics_grade":result['mathematics_grade'],
                    "english":result['english'],
                    "english_grade":result['english_grade'],
                    "kiswahili":result['kiswahili'],
                    "kiswahili_grade":result['kiswahili_grade'],
                    "chemistry":result['chemistry'],
                    "chemistry_grade":result['chemistry_grade'],
                    "biology":result['biology'],
                    "biology_grade":result['biology_grade'],
                    "physics":result['physics'],
                    "physics_grade":result['physics_grade'],
                    "cre":result['cre'],
                    "cre_grade":result['cre_grade'],
                    "history":result['history'],
                    "history_grade":result['history_grade'],
                    "geography":result['geography'],
                    "geography_grade":result['geography_grade'],
                    "bussiness":result['bussiness'],
                    "bussiness_grade":result['bussiness_grade'],
                    "agriculture":result['agriculture'],
                    "agriculture_grade":result['agriculture_grade'],
                }
            
            if context.get('first_exam') and context.get('second_exam') and context.get('third_exam'):
                context['avg'] = {
                    "mathematics":average(context['first_exam']['mathematics'], context['second_exam']['mathematics'],context['third_exam']['mathematics']),
                    "english":average(context['first_exam']['english'], context['second_exam']['english'],context['third_exam']['english']),
                    "kiswahili":average(context['first_exam']['kiswahili'], context['second_exam']['kiswahili'],context['third_exam']['kiswahili']),
                    "chemistry":average(context['first_exam']['chemistry'], context['second_exam']['chemistry'],context['third_exam']['chemistry']),
                    "physics":average(context['first_exam']['physics'], context['second_exam']['physics'],context['third_exam']['physics']),
                    "biology":average(context['first_exam']['biology'], context['second_exam']['biology'],context['third_exam']['biology']),
                    "history":average(context['first_exam']['history'], context['second_exam']['history'],context['third_exam']['history']),
                    "geography":average(context['first_exam']['geography'], context['second_exam']['geography'],context['third_exam']['geography']),
                    "cre":average(context['first_exam']['cre'], context['second_exam']['cre'],context['third_exam']['cre']),
                    "bussiness":average(context['first_exam']['bussiness'], context['second_exam']['bussiness'],context['third_exam']['bussiness']),
                    "agriculture":average(context['first_exam']['agriculture'], context['second_exam']['agriculture'],context['third_exam']['agriculture'])
                }
            if context.get('first_exam') is None and context.get('second_exam') and context.get('third_exam'):
                context['avg'] = {
                    "mathematics":case2average(context['second_exam']['mathematics'],context['third_exam']['mathematics']),
                    "english":case2average(context['second_exam']['english'],context['third_exam']['english']),
                    "kiswahili":case2average(context['second_exam']['kiswahili'],context['third_exam']['kiswahili']),
                    "chemistry":case2average(context['second_exam']['chemistry'],context['third_exam']['chemistry']),
                    "biology":case2average(context['second_exam']['biology'],context['third_exam']['biology']),
                    "physics":case2average(context['second_exam']['physics'],context['third_exam']['physics']),
                    "cre":case2average(context['second_exam']['cre'],context['third_exam']['cre']),
                    "history":case2average(context['second_exam']['history'],context['third_exam']['history']),
                    "geography":case2average(context['second_exam']['geography'],context['third_exam']['geography']),
                    "bussiness":case2average(context['second_exam']['bussiness'],context['third_exam']['bussiness']),
                    "agriculture":case2average(context['second_exam']['agriculture'],context['third_exam']['agriculture']),
                }
            if context.get('first_exam') and context.get('second_exam') and context.get('third_exam') is None:
                context['avg'] = {
                    "mathematics":case2average(context['first_exam']['mathematics'],context['second_exam']['mathematics']),
                    "english":case2average(context['first_exam']['english'],context['second_exam']['english']),
                    "kiswahili":case2average(context['first_exam']['kiswahili'],context['second_exam']['kiswahili']),
                    "chemistry":case2average(context['first_exam']['chemistry'],context['second_exam']['chemistry']),
                    "biology":case2average(context['first_exam']['biology'],context['second_exam']['biology']),
                    "physics":case2average(context['first_exam']['physics'],context['second_exam']['physics']),
                    "cre":case2average(context['first_exam']['cre'],context['second_exam']['cre']),
                    "history":case2average(context['first_exam']['history'],context['second_exam']['history']),
                    "geography":case2average(context['first_exam']['geography'],context['second_exam']['geography']),
                    "bussiness":case2average(context['first_exam']['bussiness'],context['second_exam']['bussiness']),
                    "agriculture":case2average(context['first_exam']['agriculture'],context['second_exam']['agriculture']),
                }
            if context.get("first_exam") and context.get('second_exam') is None and context.get('third_exam'):
                context['avg'] = {
                    "mathematics":specialaverage(context['first_exam']['mathematics'], context['third_exam']['mathematics']),
                    "english":specialaverage(context['first_exam']['english'], context['third_exam']['english']),
                    "kiswahili":specialaverage(context['first_exam']['kiswahili'], context['third_exam']['kiswahili']),
                    "chemistry":specialaverage(context['first_exam']['chemistry'], context['third_exam']['chemistry']),
                    "physics":specialaverage(context['first_exam']['physics'], context['third_exam']['physics']),
                    "biology":specialaverage(context['first_exam']['biology'], context['third_exam']['biology']),
                    "cre":specialaverage(context['first_exam']['cre'], context['third_exam']['cre']),
                    "history":specialaverage(context['first_exam']['history'], context['third_exam']['history']),
                    "geography":specialaverage(context['first_exam']['geography'], context['third_exam']['geography']),
                    "bussiness":specialaverage(context['first_exam']['bussiness'], context['third_exam']['bussiness']),
                    "agriculture":specialaverage(context['first_exam']['agriculture'], context['third_exam']['agriculture']),
                }
            if context.get('first_exam') and context.get('second_exam') is None and context.get('third_exam') is None:
                context['avg'] = {
                    "mathematics":context['first_exam']['mathematics'],
                    "kiswahili":context['first_exam']['kiswahili'],
                    "english":context['first_exam']['english'],
                    "biology":context['first_exam']['biology'],
                    "history":context['first_exam']['history'],
                    "physics":context['first_exam']['physics'],
                    "chemistry":context['first_exam']['chemistry'],
                    "cre":context['first_exam']['cre'],
                    "geography":context['first_exam']['geography'],
                    "bussiness":context['first_exam']['bussiness'],
                    "agriculture":context['first_exam']['agriculture'],
                }
            if context.get('first_exam') is None and context.get('second_exam') and context.get('third_exam') is None:
                context['avg'] = {
                    "mathematics":context['second_exam']['mathematics'],
                    "kiswahili":context['second_exam']['kiswahili'],
                    "english":context['second_exam']['english'],
                    "biology":context['second_exam']['biology'],
                    "history":context['second_exam']['history'],
                    "physics":context['second_exam']['physics'],
                    "chemistry":context['second_exam']['chemistry'],
                    "cre":context['second_exam']['cre'],
                    "geography":context['second_exam']['geography'],
                    "bussiness":context['second_exam']['bussiness'],
                    "agriculture":context['second_exam']['agriculture'],
                }
            if context.get('first_exam') is None and context.get('second_exam') is None and context.get('third_exam'):
                context['avg'] = {
                    "mathematics":context['third_exam']['mathematics'],
                    "kiswahili":context['third_exam']['kiswahili'],
                    "english":context['third_exam']['english'],
                    "biology":context['third_exam']['biology'],
                    "history":context['third_exam']['history'],
                    "physics":context['third_exam']['physics'],
                    "chemistry":context['third_exam']['chemistry'],
                    "cre":context['third_exam']['cre'],
                    "geography":context['third_exam']['geography'],
                    "bussiness":context['third_exam']['bussiness'],
                    "agriculture":context['third_exam']['agriculture'],
                }
            if context.get('first_exam') is None and context.get('second_exam') is None and context.get('third_exam') is None:
                context['avg'] = {
                    "mathematics":int(0),
                    "kiswahili":int(0),
                    "english":int(0),
                    "biology":int(0),
                    "history":int(0),
                    "physics":int(0),
                    "chemistry":int(0),
                    "cre":int(0),
                    "geography":int(0),
                    "bussiness":int(0),
                    "agriculture":int(0)
                }
            
            context['remark'] = {
                "mathematics":average_remark(context['avg']['mathematics']),
                "english":average_remark(context['avg']['english']),
                "kiswahili":average_remark_kiswahili(context['avg']['kiswahili']),
                "chemistry":average_remark(context['avg']['chemistry']),
                "biology":average_remark(context['avg']['biology']),
                "physics":average_remark(context['avg']['physics']),
                "geography":average_remark(context['avg']['geography']),
                "history":average_remark(context['avg']['history']),
                "cre":average_remark(context['avg']['cre']),
                "bussiness":average_remark(context['avg']['bussiness']),
                "agriculture":average_remark(context['avg']['agriculture']),
            }
            
            context['avg']["mathematics_points"] = award_grade(student.form, Subject.objects.get(subject_name = 'mathematics'), int(context['avg']['mathematics']))[0]
            context['avg']["mathematics_grade"] = award_grade(student.form, Subject.objects.get(subject_name = 'mathematics'), int(context['avg']['mathematics']))[1]
            context['avg']["english_points"] = award_grade(student.form, Subject.objects.get(subject_name = 'english'), int(context['avg']['english']))[0]
            context['avg']["english_grade"] = award_grade(student.form, Subject.objects.get(subject_name = 'english'), int(context['avg']['english']))[1]
            context['avg']["kiswahili_points"] = award_grade(student.form, Subject.objects.get(subject_name = 'kiswahili'), int(context['avg']['kiswahili']))[0]
            context['avg']["kiswahili_grade"] = award_grade(student.form, Subject.objects.get(subject_name = 'kiswahili'), int(context['avg']['kiswahili']))[1]
            context['avg']["chemistry_points"] = award_grade(student.form, Subject.objects.get(subject_name = 'chemistry'), int(context['avg']['chemistry']))[0]
            context['avg']["chemistry_grade"] = award_grade(student.form, Subject.objects.get(subject_name = 'chemistry'), int(context['avg']['chemistry']))[1]
            context['avg']["physics_points"] = award_grade(student.form, Subject.objects.get(subject_name = 'physics'), int(context['avg']['physics']))[0]
            context['avg']["physics_grade"] = award_grade(student.form, Subject.objects.get(subject_name = 'physics'), int(context['avg']['physics']))[1]
            context['avg']["biology_points"] = award_grade(student.form, Subject.objects.get(subject_name = 'biology'), int(context['avg']['biology']))[0]
            context['avg']["biology_grade"] = award_grade(student.form, Subject.objects.get(subject_name = 'biology'), int(context['avg']['biology']))[1]
            context['avg']["cre_points"] = award_grade(student.form, Subject.objects.get(subject_name = 'cre'), int(context['avg']['cre']))[0]
            context['avg']["cre_grade"] = award_grade(student.form, Subject.objects.get(subject_name = 'cre'), int(context['avg']['cre']))[1]
            context['avg']["history_points"] = award_grade(student.form, Subject.objects.get(subject_name = 'history'), int(context['avg']['history']))[0]
            context['avg']["history_grade"] = award_grade(student.form, Subject.objects.get(subject_name = 'history'), int(context['avg']['history']))[1]
            context['avg']["geography_points"] = award_grade(student.form, Subject.objects.get(subject_name = 'geography'), int(context['avg']['geography']))[0]
            context['avg']["geography_grade"] = award_grade(student.form, Subject.objects.get(subject_name = 'geography'), int(context['avg']['geography']))[1]
            context['avg']["bussiness_points"] = award_grade(student.form, Subject.objects.get(subject_name = 'bussiness'), int(context['avg']['bussiness']))[0]
            context['avg']["bussiness_grade"] = award_grade(student.form, Subject.objects.get(subject_name = 'bussiness'), int(context['avg']['bussiness']))[1]
            context['avg']["agriculture_points"] = award_grade(student.form, Subject.objects.get(subject_name = 'agriculture'), int(context['avg']['agriculture']))[0]
            context['avg']["agriculture_grade"] = award_grade(student.form, Subject.objects.get(subject_name = 'agriculture'), int(context['avg']['agriculture']))[1]
            context['avg']['total_points'] = context['avg']['mathematics_points'] + context['avg']['english_points'] + context['avg']['kiswahili_points'] + context['avg']['chemistry_points'] + context['avg']['biology_points'] + context['avg']['physics_points'] + context['avg']['cre_points'] + context['avg']['history_points'] + context['avg']['geography_points'] + context['avg']['bussiness_points'] + context['avg']['agriculture_points']

            
            # term_period = f"form{student.form}{term}_closing_balance"
            
            # if getattr(Feestructure.objects.get(), next_term):
            #     balance = getattr(student, term_period)
            #     next_term_fee = getattr(Feestructure.objects.get(), next_term)
            #     next_term_balance =int(balance) - next_term_fee
            #     context['next_term_balance'] = next_term_balance

            term_period = f"form{student.form}{term}_closing_balance"
            if getattr(student, term_period):
                balance = getattr(student, term_period)
                context['balance'] = balance
                next_term_fee = getattr(Feestructure.objects.get(), next_term)
                context['next_term_fee'] = next_term_fee
                context['next_term_balance'] = balance + next_term_fee

            dates = open_and_closing.objects.get()
            context['opening_date'] = dates.opening_date
            context['closing_date'] = dates.closing_date

            ylist=[]
            xlist=[]
            if student.kcpe:
                xlist.append("kcpe")
                ylist.append(int(student.kcpe) *(120/500))
            if context.get('first_exam'):
                xlist.append("BOT")
                ylist.append(context['first_exam']['total_points'])

            if context.get('second_exam'):
                xlist.append("MOT")
                ylist.append(int(context['second_exam']['total_points']))

            if context.get('third_exam'):
                xlist.append("EOT")
                ylist.append(int(context['third_exam']['total_points']))
            xlist.append("AVG")
            ylist.append(int(context['avg']['total_points']))

            image_base64 = None
            index = np.arange(len(xlist))
            graph = plt.bar(index, ylist)
            graph[len(ylist) - 1].set_color("black")
            plt.xlabel('')
            plt.ylabel('total points')
            plt.xticks(index, xlist)
            plt.title(f"{student.student_name} termly performance trend")
            buf = BytesIO()
            plt.savefig(buf, format = 'png', dpi = 500)
            plt.clf()
            image_base64 = base64.b64encode(buf.getvalue()).decode('utf-8').replace('\n', '')
            buf.close()
            context['image_base64'] = image_base64
            context['stud'] = student
            context['term'] = term
            report_card_template = get_template('report_card.html')
            html = report_card_template.render(context)
            pdf_file = HTML(string = html, base_url = request.build_absolute_uri()).write_pdf()
            zf.writestr(f"{student.adm_no}.pdf", pdf_file)
        
        response['Content-Disposition'] = f"filename = {term} {form}.zip"
        return response
        
    context = {
        "dates":open_and_closing.objects.get()
    }
    return render(request, "generate_endterm_reports_form.html", context)




    #generating class lists 
def class_list(request, form):
    student_queryset = Student.objects.filter(form = form)
    filtered_class = f"{form} | entire class | Boys and Girls"
    filtered_class = {}
    filtered_class['form'] = form
    filtered_class['class'] = "entire"
    filtered_class['gender'] = "entire"
    if request.GET.get('gender') and request.GET.get("class"):
        if request.GET.get('gender') != 'entire' and request.GET.get('class') != 'entire':
            student_queryset = student_queryset.filter(gender = request.GET.get('gender'))
            stream = request.GET['class']
            student_queryset = student_queryset.filter(stream = stream)
            
            filtered_class['form'] = form
            filtered_class['class'] = request.GET.get('class')
            filtered_class['gender'] = request.GET.get('gender')

        if request.GET.get('gender') == 'entire' or request.GET.get("class") == 'entire':
            if request.GET.get('gender') == "entire" and request.GET.get('class') != 'entire':
                stream = request.GET.get("class")
                student_queryset = student_queryset.filter(stream = stream)
                
                filtered_class['form'] = form
                filtered_class['class'] = request.GET.get('class')
                filtered_class['gender'] = request.GET.get('entire')

            if request.GET.get('class') == "entire" and request.GET.get('gender') != 'entire':
                student_queryset = student_queryset.filter(gender = request.GET.get('gender'))
                # filtered_class = f"{form} | entire class | {request.GET.get('gender')}"
                filtered_class['form'] = form
                filtered_class['class'] = 'entire'
                filtered_class['gender'] = request.GET.get('gender')
            
    context = {
        "form_id":form,
        "filtered_class":filtered_class,
        "student_queryset":student_queryset,
    }   
    template = get_template('class_template.html')
    html = template.render(context)
    class_list_pdf = HTML(string = html, base_url =  request.build_absolute_uri()).write_pdf()
    if request.POST.get('print'):
        return HttpResponse(class_list_pdf ,content_type="application/pdf")
    return render(request, "class_list.html", context)


def promote_students(request):    
    if request.GET.get('promote'):
        if request.GET['promote'] == "true":
            student_queryset = Student.objects.all()
            for student in Student.objects.all():
                if student.form == 4:
                    Alumni.objects.create(
                        student_name = student.student_name,
                        date_of_birth = student.date_of_birth,
                        adm_no = student.adm_no,
                        gender = student.gender,
                        kcpe = student.kcpe,
                        student_photo = student.student_photo,
                        form = student.form,
                        stream = student.stream,
                        phone_number = student.phone_number,
                        parent_phone_number = student.parent_phone_number,
                        guardian_phone = student.guardian_phone,
                        parent_name = student.parent_name,
                        guardian_name = student.guardian_name,
                        county = student.county,
                        birth_cert = student.birth_cert,
                        adm_date = student.adm_date,
                        upi_no = student.upi_no,
                        kcpe_index = student.kcpe_index,
                        form1_term1bot = student.form1_term1bot,
                        form1_term1mot = student.form1_term1mot,
                        form1_term1eot = student.form1_term1eot,
                        form1_term2bot = student.form1_term2bot,
                        form1_term2mot = student.form1_term2mot,
                        form1_term2eot = student.form1_term2eot,
                        form1_term3bot = student.form1_term3bot,
                        form1_term3mot = student.form1_term3mot,
                        form1_term3eot = student.form1_term3eot,
                        form2_term1bot = student.form2_term1bot,
                        form2_term1mot = student.form2_term1mot,
                        form2_term1eot = student.form2_term1eot,
                        form2_term2bot = student.form2_term2bot,
                        form2_term2mot = student.form2_term2mot,
                        form2_term2eot = student.form2_term2eot,
                        form2_term3bot = student.form2_term3bot,
                        form2_term3mot = student.form2_term3mot,
                        form2_term3eot = student.form2_term3eot,
                        form3_term1bot = student.form3_term1bot,
                        form3_term1mot = student.form3_term1mot,
                        form3_term1eot = student.form3_term1eot,
                        form3_term2bot = student.form3_term2bot,
                        form3_term2mot = student.form3_term2mot,
                        form3_term2eot = student.form3_term2eot,
                        form3_term3bot = student.form3_term3bot,
                        form3_term3mot = student.form3_term3mot,
                        form3_term3eot = student.form3_term3eot,
                        form4_term1bot = student.form4_term1bot,
                        form4_term1mot = student.form4_term1mot,
                        form4_term1eot = student.form4_term1eot,
                        form4_term2bot = student.form4_term2bot,
                        form4_term2mot = student.form4_term2mot,
                        form4_term2eot = student.form4_term2eot,
                        form4_term3bot = student.form4_term3bot,
                        form4_term3mot = student.form4_term3mot,
                        form4_term3eot = student.form4_term3eot
                    )
                    student_queryset.delete()
                if student.form == 3:
                    student.form = 4
                    student.save()
                if student.form == 2:
                    student.form =3
                    student.save()
                if student.form == 1:
                    student.form = 2
                    student.save()
                
            return redirect('schoolapp:dash')
    context = {
        "student_queryset":Student.objects.all(),
    }
    return render(request, "promote_students.html", context)



def clearstuff(request):
    for student in Student.objects.all():
        student.form1_term1bot = None
        student.form1_term1mot = None
        student.form1_term1eot = None
        student.form1_term2bot = None
        student.form1_term2mot = None
        student.form1_term2eot = None
        student.form1_term3bot = None
        student.form1_term3mot = None
        student.form1_term3eot = None
        student.form2_term1bot = None
        student.form2_term1mot = None
        student.form2_term1eot = None
        student.form2_term2bot = None
        student.form2_term2mot = None
        student.form2_term2eot = None
        student.form2_term3bot = None
        student.form2_term3mot = None
        student.form2_term3eot = None
        student.form3_term1bot = None
        student.form3_term1mot = None
        student.form3_term1eot = None
        student.form3_term2bot = None
        student.form3_term2mot = None
        student.form3_term2eot = None
        student.form3_term3bot = None
        student.form3_term3mot = None
        student.form3_term3eot = None
        student.form4_term1bot = None
        student.form4_term1mot = None
        student.form4_term1eot = None
        student.form4_term2bot = None
        student.form4_term2mot = None
        student.form4_term2eot = None
        student.form4_term3bot = None
        student.form4_term3mot = None
        student.form4_term3eot = None

        student.form1term1_closing_balance = None
        student.form1term2_closing_balance = None
        student.form1term3_closing_balance = None
        student.form2term1_closing_balance = None
        student.form2term2_closing_balance = None
        student.form2term3_closing_balance = None
        student.form3term1_closing_balance = None
        student.form3term2_closing_balance = None
        student.form3term3_closing_balance = None
        student.form4term1_closing_balance = None
        student.form4term2_closing_balance = None
        student.form4term3_closing_balance = None

        student.save()

    return HttpResponse("junk has been cleared")

def add_user(request):
    if request.method == "POST":
        user = User.objects.create(
            username = request.POST['username']
        )
        user.set_password(request.POST['username'])
        user.save()
    context = {}
    return render(request, "add_user.html", context)