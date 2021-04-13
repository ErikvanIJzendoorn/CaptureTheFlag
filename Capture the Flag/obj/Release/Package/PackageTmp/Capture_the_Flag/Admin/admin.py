from django.contrib import admin
from .models import *
admin.site.register(Team)
admin.site.register(Teamlid)
admin.site.register(Toernooi)
admin.site.register(Gebruiker_Toernooi)
admin.site.register(Team_Toernooi)
admin.site.register(Vraag)
admin.site.register(Ronde)
admin.site.register(Ronde_Vraag)
admin.site.register(Antwoord)
admin.site.register(Timer)
admin.site.register(Notification)