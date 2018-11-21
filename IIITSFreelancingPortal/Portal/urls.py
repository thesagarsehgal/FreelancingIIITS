from django.urls import path
from . import views

app_name = 'Portal'
urlpatterns = [
    path('', views.index, name='index'),
    path('signup/', views.signup_user, name='signup'),
    path('check_username/', views.check_username, name='check_username'),
    path('check_email/', views.check_email, name='check_email'),
    path('auth/callback/<token>', views.auth_callback_token, name='login_iiits'),
    path('login/', views.login_user, name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('open_close_project/', views.open_close_project,name="open_close_project"),
    path('home/', views.home, name='home'),
    path('browse_jobs/', views.browse_jobs, name='browse_jobs'),
    path('jobs_update/', views.jobs_update, name='jobs_update'),
    path('form_state/', views.form_state, name='form_state'),
    path('post_project/', views.post_project, name='post_project'),
    path('project_description/<int:project_id>/', views.project_description, name='project_description'),
    path('<int:project_id>/add_task/', views.add_task, name='add_task'),
    path('<int:project_id>/task_description/<int:task_id>/', views.task_description, name='task_description'),
    path('<int:project_id>/task_edit/<int:task_id>/', views.task_editfunction, name='task_edit'),
    path('profile/<username>/', views.user_profile, name="profile"),
    path('myprojects/', views.myprojects, name="myprojects"),
    path('applicants/<int:task_id>/', views.applicants,name="applicants")
]
