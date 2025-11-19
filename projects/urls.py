from django.urls import path
from .views import project_list, project_detail, propose_project, my_projects

urlpatterns = [
    path('', project_list, name='project_list'),
    path('propose/', propose_project, name='propose_project'),
    path('my-projects/', my_projects, name='my_projects'),
    path('<slug:slug>/', project_detail, name='project_detail'),
]

