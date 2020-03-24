from django.contrib import admin

from .models import  Student, Teacher, Subject, Portal,SubjectGradingSystem, Alumni, HOD, open_and_closing

admin.site.register(Teacher)
admin.site.register(Student)
admin.site.register(Subject)
admin.site.register(Portal)
admin.site.register(SubjectGradingSystem)
admin.site.register(Alumni)
admin.site.register(HOD)
admin.site.register(open_and_closing)
# Register your models here.
