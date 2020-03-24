from django.db import models
from django.contrib.auth.models import User


class Subject(models.Model):
    subject_name = models.CharField(max_length = 20)
    compulsory = models.BooleanField(default = False)
    def __str__(self):
        return self.subject_name

class Student(models.Model):
    student_name = models.CharField(null = True, max_length=30)
    date_of_birth = models.TextField(null = True, blank= True)
    adm_no = models.IntegerField(null = True, blank= True)
    gender = models.CharField(max_length = 1, null = True)
    kcpe = models.IntegerField(null = True, blank = True)
    student_photo = models.ImageField(null = True, blank= True)
    form = models.IntegerField()
    stream = models.CharField(max_length=1)
    subjects = models.ManyToManyField(Subject)
    phone_number = models.CharField(null = True, blank=True, max_length= 20)
    parent_phone_number = models.CharField(null = True, blank=True, max_length= 20)
    guardian_phone = models.CharField(null = True, blank=True, max_length= 20)
    parent_name = models.CharField(null = True, blank=True, max_length = 30)
    guardian_name = models.CharField(null = True, blank=True, max_length = 30)
    county = models.CharField(null = True, blank=True, max_length= 30)
    birth_cert = models.IntegerField(null = True, blank=True)
    adm_date = models.TextField(null = True, blank=True)
    upi_no = models.CharField(null = True, blank=True, max_length=40)
    kcpe_index = models.IntegerField(null = True, blank= True)
    
    form1_term1bot = models.TextField(null = True, blank=True)
    form1_term1mot = models.TextField(null = True, blank=True)
    form1_term1eot = models.TextField(null = True, blank=True)

    form1_term2bot = models.TextField(null = True, blank=True)
    form1_term2mot = models.TextField(null = True, blank=True)
    form1_term2eot = models.TextField(null = True, blank=True)

    form1_term3bot = models.TextField(null = True, blank=True)
    form1_term3mot = models.TextField(null = True, blank=True)
    form1_term3eot = models.TextField(null = True, blank=True)

    form2_term1bot = models.TextField(null = True, blank=True)
    form2_term1mot = models.TextField(null = True, blank=True)
    form2_term1eot = models.TextField(null = True, blank=True)
    
    form2_term2bot = models.TextField(null = True, blank=True)
    form2_term2mot = models.TextField(null = True, blank=True)
    form2_term2eot = models.TextField(null = True, blank=True)

    form2_term3bot = models.TextField(null = True, blank=True)
    form2_term3mot = models.TextField(null = True, blank=True)
    form2_term3eot = models.TextField(null = True, blank=True)

    form3_term1bot = models.TextField(null = True, blank=True)
    form3_term1mot = models.TextField(null = True, blank=True)
    form3_term1eot = models.TextField(null = True, blank=True)
    
    form3_term2bot = models.TextField(null = True, blank=True)
    form3_term2mot = models.TextField(null = True, blank=True)
    form3_term2eot = models.TextField(null = True, blank=True)

    form3_term3bot = models.TextField(null = True, blank=True)
    form3_term3mot = models.TextField(null = True, blank=True)
    form3_term3eot = models.TextField(null = True, blank=True)

    form4_term1bot = models.TextField(null = True, blank=True)
    form4_term1mot = models.TextField(null = True, blank=True)
    form4_term1eot = models.TextField(null = True, blank=True)

    form4_term2bot = models.TextField(null = True, blank=True)
    form4_term2mot = models.TextField(null = True, blank=True)
    form4_term2eot = models.TextField(null = True, blank=True)
    
    form4_term3bot = models.TextField(null = True, blank=True)
    form4_term3mot = models.TextField(null = True, blank=True)
    form4_term3eot = models.TextField(null = True, blank=True)

    form1term1_closing_balance = models.IntegerField(null = True, blank = True)
    form1term2_closing_balance = models.IntegerField(null = True, blank = True)
    form1term3_closing_balance = models.IntegerField(null = True, blank = True)

    form2term1_closing_balance = models.IntegerField(null = True, blank = True)
    form2term2_closing_balance = models.IntegerField(null = True, blank = True)
    form2term3_closing_balance = models.IntegerField(null = True, blank = True)
    
    form3term1_closing_balance = models.IntegerField(null = True, blank = True)
    form3term2_closing_balance = models.IntegerField(null = True, blank = True)
    form3term3_closing_balance = models.IntegerField(null = True, blank = True)

    form4term1_closing_balance = models.IntegerField(null = True, blank = True)
    form4term2_closing_balance = models.IntegerField(null = True, blank = True)
    form4term3_closing_balance = models.IntegerField(null = True, blank = True)


    def __str__(self):
        return self.student_name

    class Meta:
        ordering = ('adm_no', "student_name")


class Teacher(models.Model):
    user = models.OneToOneField(User, on_delete = models.CASCADE)
    subjects = models.ManyToManyField(Subject)
    selected_timestamp = models.CharField(null = True, blank = True, max_length= 30)
    selected_subject = models.IntegerField(null = True, blank=True)  #holds the subject_id
    initials = models.TextField(max_length=6, null = True, blank = True)
    is_teacher = models.BooleanField(default=True)
    is_dean = models.BooleanField(default = False)
    is_accountant = models.BooleanField(default= False)
    is_secretary = models.BooleanField(default=False)
    is_principal = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username
        
class Portal(models.Model):
    term1bot =models.BooleanField()
    term2bot = models.BooleanField()
    term3bot = models.BooleanField()
    term1mot =models.BooleanField()
    term2mot = models.BooleanField()
    term3mot = models.BooleanField()
    term1eot =models.BooleanField()
    term2eot = models.BooleanField()
    term3eot = models.BooleanField()



#grading system model goes here
class SubjectGradingSystem(models.Model):
    form = models.IntegerField(null = True, blank= True)
    subject = models.ForeignKey(Subject, on_delete = models.CASCADE)
    Aplain_upper = models.IntegerField()
    Aplain_lower = models.IntegerField()
    Aplain_points =models.IntegerField()
    Aminus_upper = models.IntegerField()
    Aminus_lower = models.IntegerField()
    Aminus_points =models.IntegerField()
    Bplus_upper = models.IntegerField()
    Bplus_lower = models.IntegerField()
    Bplus_points =models.IntegerField()
    Bplain_upper = models.IntegerField()
    Bplain_lower = models.IntegerField()
    Bplain_points =models.IntegerField()
    Bminus_upper = models.IntegerField()
    Bminus_lower = models.IntegerField()
    Bminus_points =models.IntegerField()
    Cplus_upper = models.IntegerField()
    Cplus_lower = models.IntegerField()
    Cplus_points =models.IntegerField()
    Cplain_upper = models.IntegerField()
    Cplain_lower = models.IntegerField()
    Cplain_points =models.IntegerField()
    Cminus_upper = models.IntegerField()
    Cminus_lower = models.IntegerField()
    Cminus_points =models.IntegerField()
    Dplus_upper = models.IntegerField()
    Dplus_lower = models.IntegerField()
    Dplus_points =models.IntegerField()
    Dplain_upper = models.IntegerField()
    Dplain_lower = models.IntegerField()
    Dplain_points =models.IntegerField()
    Dminus_upper = models.IntegerField()
    Dminus_lower = models.IntegerField()
    Dminus_points =models.IntegerField()
    Eplain_upper = models.IntegerField()
    Eplain_lower = models.IntegerField()
    Eplain_points = models.IntegerField()
    Fplain_upper = models.IntegerField(null = True)
    Fplain_lower = models.IntegerField(null = True)
    Fplain_points = models.IntegerField(null = True)
    
    def __str__(self):
        return f"{self.form} {self.subject}"


class Alumni(models.Model):
    student_name = models.CharField(null = True, max_length=30)
    date_of_birth = models.TextField(null = True, blank= True)
    adm_no = models.IntegerField(null = True, blank= True)
    gender = models.CharField(max_length = 1, null = True)
    kcpe = models.IntegerField(null = True, blank = True)
    student_photo = models.ImageField(null = True, blank= True)
    form = models.IntegerField()
    stream = models.CharField(max_length=1)
    subjects = models.ManyToManyField(Subject)
    phone_number = models.CharField(null = True, blank=True, max_length= 20)
    parent_phone_number = models.CharField(null = True, blank=True, max_length= 20)
    guardian_phone = models.CharField(null = True, blank=True, max_length= 20)
    parent_name = models.CharField(null = True, blank=True, max_length = 30)
    guardian_name = models.CharField(null = True, blank=True, max_length = 30)
    county = models.CharField(null = True, blank=True, max_length= 30)
    birth_cert = models.IntegerField(null = True, blank=True)
    adm_date = models.TextField(null = True, blank=True)
    upi_no = models.CharField(null = True, blank=True, max_length=40)
    kcpe_index = models.IntegerField(null = True, blank= True)
    
    form1_term1bot = models.TextField(null = True, blank=True)
    form1_term1mot = models.TextField(null = True, blank=True)
    form1_term1eot = models.TextField(null = True, blank=True)

    form1_term2bot = models.TextField(null = True, blank=True)
    form1_term2mot = models.TextField(null = True, blank=True)
    form1_term2eot = models.TextField(null = True, blank=True)

    form1_term3bot = models.TextField(null = True, blank=True)
    form1_term3mot = models.TextField(null = True, blank=True)
    form1_term3eot = models.TextField(null = True, blank=True)

    form2_term1bot = models.TextField(null = True, blank=True)
    form2_term1mot = models.TextField(null = True, blank=True)
    form2_term1eot = models.TextField(null = True, blank=True)
    
    form2_term2bot = models.TextField(null = True, blank=True)
    form2_term2mot = models.TextField(null = True, blank=True)
    form2_term2eot = models.TextField(null = True, blank=True)

    form2_term3bot = models.TextField(null = True, blank=True)
    form2_term3mot = models.TextField(null = True, blank=True)
    form2_term3eot = models.TextField(null = True, blank=True)

    form3_term1bot = models.TextField(null = True, blank=True)
    form3_term1mot = models.TextField(null = True, blank=True)
    form3_term1eot = models.TextField(null = True, blank=True)
    
    form3_term2bot = models.TextField(null = True, blank=True)
    form3_term2mot = models.TextField(null = True, blank=True)
    form3_term2eot = models.TextField(null = True, blank=True)

    form3_term3bot = models.TextField(null = True, blank=True)
    form3_term3mot = models.TextField(null = True, blank=True)
    form3_term3eot = models.TextField(null = True, blank=True)

    form4_term1bot = models.TextField(null = True, blank=True)
    form4_term1mot = models.TextField(null = True, blank=True)
    form4_term1eot = models.TextField(null = True, blank=True)

    form4_term2bot = models.TextField(null = True, blank=True)
    form4_term2mot = models.TextField(null = True, blank=True)
    form4_term2eot = models.TextField(null = True, blank=True)
    
    form4_term3bot = models.TextField(null = True, blank=True)
    form4_term3mot = models.TextField(null = True, blank=True)
    form4_term3eot = models.TextField(null = True, blank=True)

    def __str__(self):
        return self.student_name

class HOD(models.Model):
    subject = models.OneToOneField(Subject, on_delete = models.CASCADE)
    teacher = models.ForeignKey(Teacher, on_delete = models.CASCADE)
    def __str__(self):
        return f"{self.subject.subject_name} {self.teacher.user.username}"

class open_and_closing(models.Model):
    closing_date = models.TextField()
    opening_date = models.TextField()
