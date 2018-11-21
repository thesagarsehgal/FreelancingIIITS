# Generated by Django 2.1.1 on 2018-11-01 23:47

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Applicant',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('time_of_application', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='CommunicationLanguage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('language_name', models.CharField(max_length=30, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Contributor',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('isCreditVerified', models.BooleanField(default=False)),
                ('time_of_selection', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='CustomUser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('phone_number', models.IntegerField(default=None)),
                ('bio', models.TextField(default=None, max_length=500)),
                ('image', models.ImageField(upload_to='profiles/')),
                ('batchYear', models.CharField(choices=[('None', 'None'), ('UG-1', 'UG-1'), ('UG-2', 'UG-2'), ('UG-3', 'UG-3'), ('UG-4', 'UG-4'), ('MS', 'MS'), ('Ph.D', 'Ph.D')], default='None', max_length=4)),
                ('gender', models.CharField(choices=[('Male', 'Male'), ('Female', 'Female')], default='Male', max_length=10)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.CharField(default=None, max_length=300)),
                ('has_read', models.BooleanField(default=False)),
                ('sending_time', models.DateTimeField(auto_now_add=True)),
                ('recieving_time', models.DateTimeField(blank=True, default=None, null=True)),
                ('_from', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='msgfrom', to='Portal.CustomUser')),
                ('_to', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='msgto', to='Portal.CustomUser')),
            ],
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('project_name', models.CharField(max_length=100)),
                ('description', models.CharField(default=None, max_length=300)),
                ('postedOn', models.DateTimeField(auto_now_add=True)),
                ('isCompleted', models.BooleanField(default=False)),
                ('deadline', models.DateField()),
                ('task_count', models.IntegerField(default=0)),
                ('leader', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Portal.CustomUser')),
            ],
        ),
        migrations.CreateModel(
            name='Skill',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('skill_name', models.CharField(max_length=50, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('task_name', models.CharField(max_length=50)),
                ('addedOn', models.DateTimeField(auto_now_add=True)),
                ('credits', models.CharField(choices=[('Paid', 'Paid'), ('Other', 'Other')], default='Paid', max_length=20)),
                ('rating', models.DecimalField(decimal_places=1, default=-1, max_digits=2)),
                ('mention', models.CharField(default=None, max_length=200, null=True)),
                ('amount', models.IntegerField(default=0)),
                ('task_description', models.CharField(default=None, max_length=100)),
                ('task_link', models.URLField(blank=True, default=None, null=True)),
                ('latest_submission_time', models.DateTimeField(blank=True, null=True)),
                ('isCompleted', models.BooleanField(default=False)),
                ('deadline', models.DateField()),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Portal.Project')),
            ],
        ),
        migrations.CreateModel(
            name='TaskLanguagesRequired',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fluency_level_required', models.IntegerField(verbose_name=1)),
                ('language', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Portal.CommunicationLanguage')),
                ('task', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Portal.Task')),
            ],
        ),
        migrations.CreateModel(
            name='TaskSkillsRequired',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('proficiency_level_required', models.IntegerField(verbose_name=1)),
                ('skill', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Portal.Skill')),
                ('task', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Portal.Task')),
            ],
        ),
        migrations.CreateModel(
            name='UserRating',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('f_rating', models.DecimalField(decimal_places=1, default=0, max_digits=2)),
                ('e_rating', models.DecimalField(decimal_places=1, default=0, max_digits=2)),
                ('emp', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='rating_by', to='Portal.CustomUser')),
                ('fre', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='rating_to', to='Portal.CustomUser')),
                ('task', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='Portal.Task')),
            ],
        ),
        migrations.CreateModel(
            name='UsersCommunicationLanguage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('level_of_fluency', models.IntegerField(default=1)),
                ('language', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Portal.CommunicationLanguage')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Portal.CustomUser')),
            ],
        ),
        migrations.CreateModel(
            name='UsersSkill',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('level_of_proficiency', models.IntegerField(default=1)),
                ('skill', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Portal.Skill')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Portal.CustomUser')),
            ],
        ),
        migrations.AddField(
            model_name='contributor',
            name='task',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Portal.Task'),
        ),
        migrations.AddField(
            model_name='contributor',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Portal.CustomUser'),
        ),
        migrations.AddField(
            model_name='applicant',
            name='task',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Portal.Task'),
        ),
        migrations.AddField(
            model_name='applicant',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Portal.CustomUser'),
        ),
    ]