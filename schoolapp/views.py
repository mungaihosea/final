from django.shortcuts import render, get_object_or_404, redirect
from .models import Portal, Student, Subject, SubjectGradingSystem
from django.http import HttpResponse
import json


def dash(request):
    context = {}
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
        return redirect('/')

        
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
                print("we chose the wrong option")
                result = json.loads(getattr(student, exam_period))
                result[get_object_or_404(Subject, id = int(request.GET['subject_id'])).subject_name] = request.POST[key]
                setattr(student,exam_period, json.dumps(result))
                student.save()
            else:
                setattr(student, exam_period, json.dumps({get_object_or_404(Subject, id = int(request.GET['subject_id'])).subject_name : request.POST[key]}))
                student.save()

        return HttpResponse("something")

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


def grading_system(request,form,subject_id):
    form = form
    subject = get_object_or_404(Subject, id = subject_id)
    current_grading_system = SubjectGradingSystem.objects.get(form = form, subject = subject)
    if request.method == 'POST':
        current_grading_system = SubjectGradingSystem.objects.get(form = form, subject = subject)
        print(current_grading_system)
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
    for form in [1, 2, 3, 4]:
        for subject in Subject.objects.all():
            SubjectGradingSystem.objects.create(
            form = form,
            subject = subject,
            Aplain_upper = 100,
            Aplain_lower = 90,
            Aplain_points = 12,
            Aminus_upper = 89,
            Aminus_lower = 80,
            Aminus_points = 11,
            Bplus_upper = 79,
            Bplus_lower = 70,
            Bplus_points = 10,
            Bplain_upper = 69,
            Bplain_lower = 60,
            Bplain_points = 9,
            Bminus_upper = 59,
            Bminus_lower = 50,
            Bminus_points = 8,
            Cplus_upper = 49,
            Cplus_lower = 40,
            Cplus_points = 7,
            Cplain_upper = 39,
            Cplain_lower = 30,
            Cplain_points = 6,
            Cminus_upper = 29,
            Cminus_lower = 20,
            Cminus_points = 5,
            Dplus_upper = 19,
            Dplus_lower = 10,
            Dplus_points = 4,
            Dplain_upper = 9,
            Dplain_lower = 5,
            Dplain_points = 3,
            Dminus_upper = 4,
            Dminus_lower = 3,
            Dminus_points = 2,
            Eplain_upper = 2,
            Eplain_lower = 0,
            Eplain_points = 1
            )
    return HttpResponse("added fake")


def view_reports(request, timestamp):    
    if request.GET.get("form"):
        student_queryset = Student.objects.filter(form = int(request.GET['form']))
        result_queryset = []
        for student in student_queryset:
            exam_period = f"form{student.form}_{timestamp}"
            result_queryset.append(json.loads(getattr(student, exam_period)))
        context = {
            "result_queryset":result_queryset,
        }
        return render(request, "results_sheet.html", context)
    context = {}
    return render(request, "view_reports.html",context)


def generate_endterm_reports(request):
    if request.GET.get('timestamp'):
        timestamp = request.GET['timestamp']
        context = {}
        return render(request, "generate_endterm_reports_form.html", context)
    context = {
        "portal":Portal.objects.get(),
    }
    return render(request, "generate_endterm_reports.html", context)


def add_student(request):
    
    if request.method == "POST":
        student = Student.objects.create(
            student_name = request.POST.get("student_name"),
            # date_of_birth = request.POST.get('date_of_birth'),
            adm_no = request.POST.get('adm_no'),
            gender = request.POST.get('gender'),
            kcpe = request.POST.get('kcpe'),
            student_photo = request.POST.get('photo'),
            stream = request.POST.get("stream"),
            form = request.POST.get("form"),
            phone_number = request.POST.get('student_phone'),
            parent_phone_number = request.POST.get('parent_phone'),
            guardian_phone = request.POST.get('guardian_phone'),
            parent_name = request.POST.get('parent_name'),
            guardian_name = request.POST.get('guardian_name'),
            county = request.POST.get('county'),
            upi_no = request.POST.get("upi_no"),
            # birth_cert = request.POST.get('birth_cert_no'),
            # adm_date = request.POST.get('adm_date'),
        )
        subject_queryset = Subject.objects.all()
        student.subjects.set(subject_queryset)
        student.save()
        return redirect("/")

    context = {}
    return render(request, "add_student.html", context)