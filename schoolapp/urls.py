from django.urls import path
from .views import dash, portal, enter_scores, enter_scores_timestamp, score_sheet,generate_results, grading_system, edit_grading_system, add_grading_stuff, view_reports, generate_endterm_reports, add_student

namespace = "schoolapp"

urlpatterns = [
    path('',dash,name = "dash"),
    path('portal/', portal, name = "portal"),
    path('enter_scores/', enter_scores, name = "enter_scores"),
    path('enter_scores/<slug:timestamp>/<str:form>/', enter_scores_timestamp, name = "enter_scores_timestamp"),
    path('score_sheet/', score_sheet, name = "score_sheet"),
    path("grading_system/<int:form>/<int:subject_id>/", grading_system, name = "grading system"),
    path("edit_grading_system/", edit_grading_system, name = "edit_grading_system"),
    path('generate_results/', generate_results, name = "generate_results"),
    path("add_grading_stuff", add_grading_stuff, name="add_grading_stuff"),
    path("view_reports/<slug:timestamp>/", view_reports, name="view_reports"),
    path("generate_endterm_reports/", generate_endterm_reports, name = "generate_endterm_reports"),
    path("add_student/", add_student, name = "add_student")
]