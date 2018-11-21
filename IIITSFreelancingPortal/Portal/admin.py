from django.contrib import admin

# Register your models here.
from .models import *

admin.site.register([CustomUser,
                     Skill,
                     CommunicationLanguage,
                     UsersSkill,
                     UsersCommunicationLanguage,
                     Project,
                     Task,
                     TaskSkillsRequired,
                     TaskLanguagesRequired,
                     Applicant,
                     Contributor,
                     UserRating,
                     ])
