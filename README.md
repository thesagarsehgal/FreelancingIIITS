# Freelancing Portal

This group project was a part of Applied Software Engineering(ASE) course.

This project is a web portal built using Django to connect Freelancer to the
employers (people who want to get the work done). 
- Projects are added by the employer and then tasks are also added for each project. 
- For each task the sills required by the task and the deadline are also specified.
- Then according to the skill of a freelancer the tasks are shown to a freelancer in his feed and they can apply to these tasks.
- The employer can see the id of all the applicants.
- The employer can select a freelancer for each of the tasks.
- All of the applicants would be notified about their acceptance and rejection. 
- After this the freelancer and the employer can work on a project and can shre some of the links b/w each other. 
- Further, the freelancer and the employer can rate each other, thus leading to a total rating of a user.

A Django based fully responsive Web Portal for freelancers to work on projects according to their skills and earn money. Technology Stack used:- 
- MySQL (for hosting) (now shifted to MySqlClient) 
- Django
- Bootstart
- Ajax

To setup this posrtal in your system follow the following instructions:-
1. Clone the repository in your system
```
git clone https://github.com/sagar-sehgal/FreelancingIIITS
```

2. Make a `virtualenv`
```
virtualenv freelancing --python=python3
```

3. Activate the virtualenv using the following command
```
source freelancing/bin/activate
```

4. Install the dependencies 
```
cd FreelancingIIITS
pip install -r requirements.txt
```

5. To load all the static files
```
python manage.py collectstatic
```
6. Then run the django application
```
cd FreelancingIIITS/IIITSFreelancingPortal
python manage.py runserver
```





