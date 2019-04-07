import json
import requests
from django.contrib.auth import login, authenticate, logout
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, reverse, redirect
from django.views.decorators.csrf import csrf_exempt
from .models import *
from django.contrib.auth.models import User
from datetime import datetime

from django.db import connection

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

url =  'http://10.0.80.133:3000/oauth/getDetails'
#url = 'https://serene-wildwood-35121.herokuapp.com/oauth/changeUr/'
clientSecret = "445b354949599afbcc454441543297a9a827b477dd3eb78d1cdd478f1482b5da08f9b6c3496e650783927e03b20e716483d5b9085143467804a5c6d40933282f"

# Create your views here.
def index(request):
    if not request.user.is_authenticated:
        return render(request, 'homepage.html')
    else:
        return HttpResponseRedirect(reverse('Portal:home'))


@csrf_exempt
def check_username(request):
    data = json.loads(request.body.decode('utf-8'))
    username = data['username']
    try:
        user = User.objects.get(username=username)
        if user:
            return HttpResponse('<b>Username must be unique.</b>')
    except User.DoesNotExist:
        return HttpResponse('')


@csrf_exempt
def check_email(request):
    data = json.loads(request.body.decode('utf-8'))
    email = data['email']
    if email.endswith('@iiits.in'):
        return HttpResponse('<b>Login with iiits link.</b>')
    try:
        if User.objects.get(email=email):
            return HttpResponse('<b>Email must be unique.</b>')
    except User.DoesNotExist:
        return HttpResponse('')


@csrf_exempt
def open_close_project(request):
    data = json.loads(request.body.decode('utf-8'))
    tid = data["task_id"]
    current_state = data["current"]
    task = Task.objects.get(id=tid)
    task.isCompleted = not task.isCompleted
    task.save()
    return HttpResponse(str(task.isCompleted))

def send_simple_message(reciever,subject,text):
    print(">>",reciever)
    print(">>",subject)
    print(">>",text)
    fromaddr = "freelancingportaliiits@gmail.com"
    toaddr = reciever
    msg = MIMEMultipart()

    msg['From'] = fromaddr
    msg['To'] = toaddr
    msg['Subject'] = subject
    body = text
    msg.attach(MIMEText(body, 'plain'))
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(fromaddr, "freelancingportal")
    text = msg.as_string()
    x=server.sendmail(fromaddr, toaddr, text)
    print(x,"sent mail")
    server.quit()

def signup_user(request):
    context = dict()
    skill_list = Skill.objects.all()
    language_list = CommunicationLanguage.objects.all()
    context['skill_list'] = skill_list
    context['language_list'] = language_list
    if request.method == 'POST':
        username = request.POST['name']
        first_name = request.POST['fname']
        last_name = request.POST['lname']
        email = request.POST['email']
        if email.endswith('@iiits.in'):
            password1 = 'iamstudent'
        else:
            password1 = request.POST['passwd1']
        phone_number = request.POST['phno']
        bio = request.POST['bio']
        image = request.FILES['image']
        batchYear = request.POST['batch']
        gender = request.POST['gender']
        skills = request.POST.getlist('skills[]')
        languages = request.POST.getlist('languages[]')
        user = User.objects.create_user(username=username, first_name=first_name, last_name=last_name, email=email,
                                        password=password1)
        cuser = CustomUser(user=user, phone_number=phone_number, image=image, bio=bio, batchYear=batchYear,
                           gender=gender)
        user.save()
        cuser.save()
        for uskill in skills:
            skill = Skill.objects.get(skill_name=uskill)
            cuskill = UsersSkill()
            cuskill.skill = skill
            cuskill.user = cuser
            cuskill.level_of_proficiency = int(request.POST[skill.skill_name])
            cuskill.save()
        for ulanguage in languages:
            language = CommunicationLanguage.objects.get(
                language_name=ulanguage)
            culanguage = UsersCommunicationLanguage()
            culanguage.language = language
            culanguage.user = cuser
            culanguage.level_of_fluency = int(
                request.POST[language.language_name])
            culanguage.save()
        login(request, user)
        return HttpResponseRedirect(reverse("Portal:home"))
    return render(request, 'signup.html', context)


def recommended_jobs(cuser):
    jobs_recommended = list()
    users_skill_obj_list = UsersSkill.objects.filter(user=cuser)
    skills_list = set([obj.skill for obj in users_skill_obj_list])
    users_languages_obj_list = UsersCommunicationLanguage.objects.filter(
        user=cuser)
    languages_list = set([obj.language for obj in users_languages_obj_list])
    jobs = applicable_jobs(cuser)
    if jobs:
        for job in jobs:
            taskskreq_obj_list = TaskSkillsRequired.objects.filter(task=job)
            job_req_skills = set([obj.skill for obj in taskskreq_obj_list])
            tasklgreq_obj_list = TaskLanguagesRequired.objects.filter(task=job)
            job_req_languages = set(
                [obj.language for obj in tasklgreq_obj_list])
            common_job_skill = skills_list.intersection(job_req_skills)
            common_job_language = languages_list.intersection(
                job_req_languages)
            if len(common_job_skill) > 0 and len(common_job_language) > 0:
                jobs_recommended.append(job)
    return jobs_recommended


def home(request):
    if not request.user.is_superuser and request.user.is_authenticated:
        context = dict()
        cuser = CustomUser.objects.get(user=request.user)
        jobs_recommended = recommended_jobs(cuser)
        posted_projects = Project.objects.filter(
            leader=cuser).order_by('-postedOn')
        if len(posted_projects) == 0:
            context['current_posted_project'] = None
            context['current_added_task'] = None
            context['percentCompleted'] = None
        else:
            current_posted_project = posted_projects[0]
            context['current_posted_project'] = current_posted_project
            total_tasks = float(
                len(Task.objects.filter(project=current_posted_project)))
            completed_tasks = float(len(Task.objects.filter(
                project=current_posted_project, isCompleted=True)))
            if total_tasks == 0 or completed_tasks == 0:
                percentCompleted = 0
            else:
                percentCompleted = int((completed_tasks / total_tasks) * 100)
                if percentCompleted != 100:
                    percentCompleted = int(round(percentCompleted / 10)) * 10
            current_posted_project_tasks = Task.objects.filter(
                project=current_posted_project).order_by('-addedOn')
            if len(current_posted_project_tasks) == 0:
                context['current_added_task'] = None
            else:
                current_added_task = current_posted_project_tasks[0]
                context['current_added_task'] = current_added_task
            context['percentCompleted'] = percentCompleted
        task_obj_list = Contributor.objects.filter(user=cuser)
        if len(task_obj_list) == 0:
            context['current_working_task'] = None
        else:
            working_task_list = [obj.task for obj in task_obj_list if obj.task.isCompleted is False]
            if working_task_list:
                current_working_task = sorted(working_task_list, key=lambda x: x.addedOn, reverse=True)[0]
                context['current_working_task'] = current_working_task
        context['jobs_recommended'] = jobs_recommended
        return render(request, 'dashboard.html', context)
    elif request.user.is_superuser:
        return HttpResponseRedirect(reverse('Portal:admin'))
    else:
        return HttpResponseRedirect(reverse('Portal:index'))


def auth_callback_token(request, token):
    payload = {
        'token': token,
        'secret': clientSecret
    }
    response = requests.post(url, payload)
    content = json.loads(response.content.decode('utf-8'))
    student = content['student'][0]
    email = student['Student_Email']
    try:
        user = User.objects.get(email=email)
        login(request, user)
        if request.COOKIES.get('post_project'):
            print(request.COOKIES.get('post_project'))
            return form_state(request, 2)
        return redirect('Portal:home')
    except User.DoesNotExist:
        context = dict()
        context['student'] = student
        skill_list = Skill.objects.all()
        language_list = CommunicationLanguage.objects.all()
        context['skill_list'] = skill_list
        context['language_list'] = language_list
    return render(request, 'signup.html', context)
    

def login_user(request):
    if request.method == 'POST':
        context = dict()
        username = request.POST['name']
        password = request.POST['passwd']
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            if request.COOKIES.get('post_project'):
                return form_state(request, id=2)
            else:
                return HttpResponseRedirect(reverse('Portal:home'))
        else:
            if request.COOKIES.get('post_project'):
                context['post_project'] = 'post_project'
            context['error_message'] = 'Username or password is incorrect'
            return render(request, 'login.html', context)
    return render(request, 'login.html')


def logout_user(request):
    logout(request)
    return HttpResponseRedirect(reverse('Portal:index'))


def applicable_jobs(cuser):
    '''
    Use this function when using sqlclient database
    '''
    if not cuser:
        projects = Project.objects.all()
    else:
        projects = Project.objects.exclude(leader=cuser)

    jobs = set()
    if projects:
        for project in projects:
            if not project.isCompleted:
                tasks = Task.objects.filter(
                        project=project, isCompleted=False)
                for task in tasks:
                    if task.contributor_set.count() == 0:
                        jobs.add(task)
    if jobs:
        print(jobs)
        sorted(jobs, key=lambda x: x.addedOn, reverse=True)
    return jobs


# def applicable_jobs(cuser):
#     '''
#     Use this function when using MySQL as a database
#     '''
#     cur = connection.cursor()
#     if not cuser:
#         id=0
#     else:
#         id=cuser.id
#     cur.callproc('applicable_jobs', [id])
#     results = cur.fetchall()
#     cur.close()
#     jobs = [Task(*row) for row in results]
#     if jobs:
#         jobs = [Task.objects.get(id=job.id) for job in jobs]
#         sorted(jobs, key=lambda x: x.addedOn, reverse=True)
#     return jobs


@csrf_exempt
def jobs_update(request):
    data = json.loads(request.body.decode('utf-8'))
    skills = data['skills']
    languages = data['languages']
    credits = data['credits']
    context = dict()
    cuser = None
    if request.user.is_authenticated:
        cuser = CustomUser.objects.get(user=request.user)
    jobs = applicable_jobs(cuser)
    # else:
    #     jobs = Task.objects.filter(isCompleted=False).order_by('-addedOn')
    filtered_tasks = set()
    filtered_tasks_skills = set()
    filtered_tasks_languages = set()
    filtered_tasks_credits = set()
    skills_len = len(skills)
    languages_len = len(languages)
    if len(skills) == 0 and len(languages) == 0:
        if not credits == "Both":
            filtered_tasks = [job for job in jobs if job.credits == credits]
            jobs = filtered_tasks
    else:
        for task in jobs:
            if skills_len > 0:
                taskskreq = TaskSkillsRequired.objects.filter(task=task)
                skill_list = [Skill.objects.get(
                    id=obj.skill.id) for obj in taskskreq]
                skill_list = [obj.skill_name for obj in skill_list]
                flag_skills = sum([skill in skills for skill in skill_list])
                if flag_skills > 0:
                    filtered_tasks_skills.add(task)
            if languages_len > 0:
                tasklgreq = TaskLanguagesRequired.objects.filter(task=task)
                language_list = [CommunicationLanguage.objects.get(
                    id=obj.language.id) for obj in tasklgreq]
                language_list = [obj.language_name for obj in language_list]
                flag_languages = sum(
                    [language in languages for language in language_list])
                if flag_languages > 0:
                    filtered_tasks_languages.add(task)
            if task.credits == credits:
                filtered_tasks_credits.add(task)

        if credits == "Both":
            if skills_len > 0 and languages_len > 0:
                filtered_tasks = filtered_tasks_skills.intersection(
                    filtered_tasks_languages)
            elif skills_len > 0:
                filtered_tasks = filtered_tasks_skills
            else:
                filtered_tasks = filtered_tasks_languages
        else:
            if skills_len > 0 and languages_len > 0:
                filtered_tasks = filtered_tasks_skills.intersection(
                    filtered_tasks_languages, filtered_tasks_credits)
            elif skills_len > 0:
                filtered_tasks = filtered_tasks_skills.intersection(filtered_tasks_credits)
            else:
                filtered_tasks = filtered_tasks_languages.intersection(filtered_tasks_credits)
        jobs = filtered_tasks
    print(filtered_tasks_skills, filtered_tasks_languages, filtered_tasks_credits)
    context['jobs'] = jobs
    print(jobs)
    return render(request, 'jobs.html', context)


def browse_jobs(request):
    context = dict()
    cuser = None
    if request.user.is_authenticated:
        cuser = CustomUser.objects.get(user=request.user)
    context['jobs'] = applicable_jobs(cuser)
    skill_list = Skill.objects.all()
    language_list = CommunicationLanguage.objects.all()
    context['skill_list'] = skill_list
    context['language_list'] = language_list
    if(request.method=='GET'):
        context['skill_check']=request.GET.get('skill',None)
        context['language_check']=request.GET.get('language',None)
    return render(request, 'browsejobs.html', context)


def form_state(request, id=1):
    context = dict()
    if id == 1:
        project_name = request.POST['name']
        description = request.POST['desc']
        deadline = request.POST['deadline']
        context['post_project'] = 'post_project'
        response = render(request, 'login.html', context)
        response.set_cookie('post_project', 'post_project')
        response.set_cookie('name', str(project_name))
        response.set_cookie('desc', str(description))
        response.set_cookie('deadline', str(deadline))
        return response
    else:
        context['name'] = request.COOKIES.get('name')
        context['desc'] = request.COOKIES.get('desc')
        context['deadline'] = request.COOKIES.get('deadline')
        context['post_project'] = 'post_project'
        response = render(request, 'postproject.html', context)
        response.delete_cookie('post_project')
        response.delete_cookie('name')
        response.delete_cookie('desc')
        response.delete_cookie('deadline')
        return response


def post_project(request):
    if request.method == 'POST':
        project_name = request.POST['name']
        description = request.POST['desc']
        deadline = request.POST['deadline']
        if request.user.is_authenticated:
            project = Project()
            project.project_name = project_name
            project.description = description
            project.leader = CustomUser.objects.get(user=request.user.id)
            project.deadline = deadline
            project.postedOn=datetime.now()
            project.save()
            return redirect('Portal:project_description',project.id)
        else:
            return form_state(request)
    return render(request, "postproject.html")


def project_description(request, project_id):
    project = Project.objects.get(id=project_id)
    if not project.isCompleted:
        if project.deadline < datetime.now().date():
            project.isCompleted = True
            project.save()
    added_tasks = Task.objects.filter(project=project.id)
    context = dict()
    context['project'] = project
    context['added_tasks'] = added_tasks
    year = project.deadline.strftime("%Y")
    month = project.deadline.strftime("%m")
    date = project.deadline.strftime("%d")
    context['year'] = year
    context['month'] = month
    context['date'] = date
    if request.user.is_authenticated:
        context['is_leader'] = (project.leader.user == request.user)
    return render(request, 'projectdescription.html', context)


def add_task(request, project_id):
    context = {}
    if request.method == 'POST':
        if request.user.is_authenticated:
            task = Task()
            task.task_name = request.POST['name']
            task.task_description = request.POST['desc']
            task.credits = request.POST['credits']
            if(task.credits=="Other"):
                task.mention = request.POST['mention']
            elif(task.credits=="Paid"):
                task.amount = int(request.POST['amount'])
            task.deadline = request.POST['deadline']
            skills = request.POST.getlist('skills[]')
            languages = request.POST.getlist('languages[]')
            task.project = Project.objects.get(id=project_id)
            task.save()
            project = Project.objects.get(id=task.project.id)
            project.task_count += 1
            project.save()
            for rskill in skills:
                skill = Skill.objects.get(skill_name=rskill)
                task_skill_req = TaskSkillsRequired()
                task_skill_req.task = task
                task_skill_req.skill = skill
                task_skill_req.proficiency_level_required = int(
                    request.POST[skill.skill_name])
                task_skill_req.save()
            for rlanguage in languages:
                language = CommunicationLanguage.objects.get(
                    language_name=rlanguage)
                task_language_req = TaskLanguagesRequired()
                task_language_req.task = task
                task_language_req.language = language
                task_language_req.fluency_level_required = int(
                    request.POST[language.language_name])
                task_language_req.save()
            return redirect('Portal:task_description',project_id ,task.id)
        return render(request, 'login.html')
    project = Project.objects.get(id=project_id)
    year = project.deadline.strftime("%Y")
    month = project.deadline.strftime("%m")
    date = project.deadline.strftime("%d")
    context['year'] = year
    context['month'] = month
    context['date'] = date
    context['project_id'] = project_id
    skill_list = Skill.objects.all()
    language_list = CommunicationLanguage.objects.all()
    context['skill_list'] = skill_list
    context['language_list'] = language_list
    return render(request, "addtask.html", context)

def submit_task(request, task):
    submit_url = request.POST.get("work_link",None)
    if(submit_url!=None):
        if (not task.isCompleted):
            task.task_link = submit_url
            task.save()

def status_update(request, task):
    if request.POST["status_update"] == "open":
        task.isCompleted = False
    elif request.POST["status_update"] == "close":
        task.isCompleted = True
    else:
        print("some error in task_description")
    task.save()


def apply_for_task(request, task):
    applicant = Applicant()
    applicant.task = Task.objects.get(id=task.id)
    applicant.user = CustomUser.objects.get(user=request.user.id)
    applicant.save()


def submit_task_review(request, task):
    print("We will accept/reject the students work here")


def user_task_rating(request,task):
    task.rating=request.POST.get("rating",None)
    task.save()


def user_user_rating(request,task,context):
    try:
        uurating=UserRating.objects.get(task=task)
    except:
        uurating=UserRating()
    uurating.task=task
    uurating.fre=Contributor.objects.get(task=task).user
    uurating.emp=task.project.leader
    if(context["is_contributor"]):
        uurating.e_rating=request.POST.get("rating",None)
    elif(context["is_leader"]):
        uurating.f_rating=request.POST.get("rating",None)
    uurating.save()


def select_user(request, task, context):
    user_id = request.POST["user_id"]
    is_applicant = False
    print(user_id)
    for i in context['applicants']:
        if i.user.user.id == int(user_id):
            is_applicant = True
    if is_applicant:
        if task.contributor_set.count() == 0:
            contributor = Contributor()
            contributor.user = CustomUser.objects.get(user=int(user_id))
            contributor.task = Task.objects.get(id=task.id)
            contributor.save()
            send_simple_message(str(contributor.user.user.email),"Selection for the Task"+str(),"You have been selected for the task "+str(contributor.task.task_name)+" of project "+str(contributor.task.project.project_name)+"\n\n -"+str(contributor.task.project.leader.user.username)) 
            for i in context['applicants']:
                if i.user!=contributor.user:
                    send_simple_message(str(i.user.user.email),"Non-Selection for the Task"+str(),"You have not been selected for the task "+str(contributor.task.task_name)+" of project "+str(contributor.task.project.project_name)+"\n\n -"+str(contributor.task.project.leader.user.username))
        else:
            print("we already have a contributor")
    else:
        print("Not an applicant")


def applicants(request, task_id):
    task = Task.objects.get(id=task_id)
    if (not request.user.is_authenticated or (request.user != task.project.leader.user)):
        return redirect("Portal:task_description", task.project.id, task_id)
    context = dict()
    context['task'] = task
    context['is_leader'] = (task.project.leader.user == request.user)
    context['applicants'] = task.applicant_set.all().order_by("-time_of_application")
    context['has_contributor'] = (task.contributor_set.count() > 0)
    if (context['has_contributor']):
        context['contributor'] = task.contributor_set.get()
    if request.method == 'POST':
        if request.user.is_authenticated and request.POST[
                "work"] == "select" and request.user == task.project.leader.user:
            select_user(request, task, context)
        return redirect("Portal:applicants", task_id)
    return render(request, "applicants.html", context)


def task_description(request, project_id, task_id):
    task = Task.objects.get(id=task_id, project=project_id)
    if not task.isCompleted:
        if task.deadline < datetime.now().date():
            task.isCompleted = True
            task.save()
    context = dict()
    year = task.deadline.strftime("%Y")
    month = task.deadline.strftime("%m")
    date = task.deadline.strftime("%d")
    context['year'] = year
    context['month'] = month
    context['date'] = date
    # if(request.user.is_authenticated):
    #     cuser=CustomUser.objects.get(user=request.user)
    #     if task.isCompleted:
    #         try:
    #             taskuserrating = UserRating.get(task=task)
    #             context["user_rating"]=taskuserrating
    #         except:
    #             taskuserrating = UserRating(task=task, emp=task.project.leader, fre=)
    #             context["user_rating"]= 
    context['task'] = task
    context['is_leader'] = (task.project.leader.user == request.user)
    context['applicants'] = task.applicant_set.all()
    context['is_contributor'] = False
    context['submit_link'] = task.task_link
    context['skills_required'] = task.taskskillsrequired_set.all()
    context['languages_required']=task.tasklanguagesrequired_set.all()
    context['task_rating'] = task.rating
    try:
        context['contributor'] = task.contributor_set.get()
        context['is_contributor'] = (context['contributor'].user.user == request.user)
    except Contributor.DoesNotExist:
        context['contributor'] = None
    context['has_applied'] = False
    for i in task.applicant_set.all():
        if i.user.user == request.user:
            context['has_applied'] = True
    if request.method == 'POST':
        if request.user.is_authenticated:
            if request.POST["work"] == "submit_task":
                submit_task(request, task)
            elif request.POST["work"] == "status_update":
                status_update(request, task)
            elif request.POST["work"] == "apply":
                if not context['has_applied']:
                    apply_for_task(request, task)
            elif request.POST["work"] == "user_task_rating":
                user_task_rating(request, task)
            elif request.POST["work"] == "user_user_rating":
                user_user_rating(request, task, context)
            elif request.POST["work"] == "start_working":
                start_end_working(request, task, )
        return redirect("Portal:task_description", project_id, task_id)
    return render(request, 'taskdescription.html', context)


def admin(request):
    if not request.user.is_authenticated:
        return render(request, 'login.html')
    else:
        context = dict()
        if request.user.is_superuser:
            no_of_users = len(User.objects.filter(is_superuser=False))
            tasks = Task.objects.filter(isCompleted=False)
            context['no_of_users'] = no_of_users
            context['no_of_jobs'] = no_of_jobs
            print(no_of_jobs)
            return render(request, 'admindashboard.html', context)
        return HttpResponse('<center><h1>You are not admin.</h1></center>')


def user_profile(request, username):
    context = dict()
    user = User.objects.get(username=username)
    cuser = CustomUser.objects.get(user=user)
    context['cuser'] = cuser
    if request.user.is_authenticated:
        if request.method == "POST":
            bio = request.POST['bio']
            cuser.bio = bio
            if request.FILES.get('image', None) is not None:
                image = request.FILES['image']
                cuser.image = image
            cuser.save()
            skills = request.POST.getlist('skills[]')
            languages = request.POST.getlist('languages[]')
            UsersSkill.objects.filter(user=cuser).all().delete()
            UsersCommunicationLanguage.objects.filter(
                user=cuser).all().delete()
            for skill in skills:
                skillreq = Skill.objects.get(skill_name=skill)
                uskill = UsersSkill(skill=skillreq, user=cuser,
                                    level_of_proficiency=int(request.POST[skill]))
                uskill.save()
            for language in languages:
                languagereq = CommunicationLanguage.objects.get(
                    language_name=language)
                ulanguage = UsersCommunicationLanguage(language=languagereq, user=cuser,
                                                       level_of_fluency=int(request.POST[language]))
                ulanguage.save()
            return HttpResponseRedirect(reverse('Portal:profile', args=(username,)))
    skills = UsersSkill.objects.filter(user=cuser)
    languages = UsersCommunicationLanguage.objects.filter(user=cuser)
    context['uskills'] = [obj.skill.skill_name for obj in skills]
    context['ulanguages'] = [
        obj.language.language_name for obj in languages]
    skill_list = Skill.objects.all()
    language_list = CommunicationLanguage.objects.all()
    context['skill_list'] = skill_list
    context['language_list'] = language_list
    context['erating'], context['frating'] = give_rating(cuser)
    return render(request, 'profile.html', context)


def give_rating(cuser):
    etasks = cuser.rating_by.all()
    ftasks = cuser.rating_to.all()
    elist = [task.e_rating for task in etasks]
    flist = [task.f_rating for task in ftasks]
    erating = None 
    frating = None
    if len(elist)>0:
        erating = int(round(sum(elist)/len(elist)))
        erating = [[1] * erating, [1] * (5 - erating)]
    if len(flist)>0:
        frating = int(round(sum(flist)/len(flist)))
        frating = [[1] * frating, [1] * (5 - frating)]
    return erating, frating

def myprojects(request):
    if request.user.is_authenticated:
        context={}
        cuser=CustomUser.objects.get(user=request.user)
        posted_tasks = [j for i in cuser.project_set.all() for j in i.task_set.all()]
        contributor_tasks=[i.task for i in cuser.contributor_set.all()]
        context['current_projects']=[i for i in cuser.project_set.all() if i.task_set.count()==0]
        context['completed']=[i for i in posted_tasks if i.isCompleted==True]+[i for i in contributor_tasks if i.isCompleted==True]
        context['active']=[i for i in posted_tasks if i.isCompleted==False]+[i for i in contributor_tasks if i.isCompleted==False]
        return render(request, 'myprojects.html',context)
    return render(request, 'login.html')

def task_editfunction(request, project_id, task_id):
    if request.user.is_authenticated:
        task = Task.objects.get(id=task_id, project=project_id)
        project = Project.objects.get(id=project_id)
        context = {}
        context['task'] = task
        context['project'] = project
        if request.method == 'POST':
            task.task_name = request.POST['name']
            task.task_description = request.POST['description']
            task.credits = request.POST['credits']
            if task.credits == 'Paid':
                task.amount = int(request.POST['amount'])
            else:    
                task.mention = request.POST['mention']
            task.deadline = request.POST['deadline']
            task.save()
            return redirect("Portal:task_description", project_id, task_id)
        project = Project.objects.get(id=project_id)
        year = project.deadline.strftime("%Y")
        month = project.deadline.strftime("%m")
        date = project.deadline.strftime("%d")
        context['year'] = year
        context['month'] = month
        context['date'] = date
        return render(request,'edittask.html',context)
    return redirect("Portal:task_description", project_id, task_id)
