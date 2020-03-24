from django.urls import path
from .views import dash, portal, enter_scores, enter_scores_timestamp, score_sheet,generate_results, grading_system, edit_grading_system, add_grading_stuff, view_reports, generate_endterm_reports, add_student, endterm_reports,login, class_list, promote_students, findstudent, edit_student, clearstuff, add_user, logout

namespace = "schoolapp"

urlpatterns = [
    path('dash/',dash,name = "dash"),
    path('', login, name= "login"),
    path('portal/', portal, name = "portal"),
    path('enter_scores/', enter_scores, name = "enter_scores"),
    path('enter_scores/<slug:timestamp>/<str:form>/', enter_scores_timestamp, name = "enter_scores_timestamp"),
    path('score_sheet/', score_sheet, name = "score_sheet"),
    path("grading_system/<int:form>/<int:subject_id>/", grading_system, name = "grading system"),
    path("edit_grading_system/", edit_grading_system, name = "edit_grading_system"),
    path('generate_results/', generate_results, name = "generate_results"),
    # path("add_grading_stuff", add_grading_stuff, name="add_grading_stuff"),
    path("view_reports/<slug:timestamp>/", view_reports, name="view_reports"),
    path("generate_endterm_reports/", generate_endterm_reports, name = "generate_endterm_reports"),
    path("generate_endterm_reports/<slug:timestamp>/", endterm_reports, name = "endterm_reports"),
    path("add_student/", add_student, name = "add_student"),
    path("class_list/<int:form>/", class_list, name = "class_list"),
    path("promote_students/", promote_students, name = "promote_students"),
    path("find_student/", findstudent, name = "find_student"),
    path("edit_student/<int:student_id>/", edit_student, name ="edit_student"),
    path("clear_stuff/", clearstuff, name="clear_stuff"),
    path("add_user", add_user, name ="add_user"),
    path('logout', logout, name ="logout")
]