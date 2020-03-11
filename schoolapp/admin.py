from django.contrib import admin

from .models import  Student, Teacher, Subject, Portal,SubjectGradingSystem

admin.site.register(Teacher)
admin.site.register(Student)
admin.site.register(Subject)
admin.site.register(Portal)
admin.site.register(SubjectGradingSystem)
# Register your models here.
