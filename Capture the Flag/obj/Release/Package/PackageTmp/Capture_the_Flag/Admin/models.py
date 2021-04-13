from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

# Create your models here.
class Team(models.Model):
    teamcode = models.CharField(max_length=255, primary_key=True)
    naam = models.CharField(max_length=255)
    score = models.IntegerField(default=0)
    kleur = models.CharField(max_length=50)

    def __str__(self):
        return self.naam

class Teamlid(models.Model):
    schermnaam = models.CharField(max_length=255, primary_key=True)
    teamcode = models.ForeignKey(Team, on_delete=models.CASCADE)
    studentnummer = models.CharField(max_length=8)

    def __str__(self):
        return self.schermnaam

class Toernooi(models.Model):
    toernooicode = models.CharField(max_length=255, primary_key=True)
    naam = models.CharField(max_length=255)
    omschrijving = models.CharField(max_length=255)
    TOURNAMENT_TYPE_CHOICES = [
        ('1', 'Casual'),
        ('2', 'Proffesioneel')
    ]
    type = models.CharField(max_length=255, choices=TOURNAMENT_TYPE_CHOICES)
    datum = models.DateField('datum')
    status = models.IntegerField(default=1)
    current_round = models.IntegerField(default=1)

    def __str__(self):
        return self.naam

class Gebruiker_Toernooi (models.Model):
    userID = models.ForeignKey(User, on_delete=models.CASCADE)
    toernooicode = models.ForeignKey(Toernooi, on_delete=models.CASCADE)
    rol = models.IntegerField(default=0)

class Team_Toernooi(models.Model):
    teamcode = models.ForeignKey(Team, on_delete=models.CASCADE)
    toernooicode = models.ForeignKey(Toernooi, on_delete=models.CASCADE)

class Vraag(models.Model):
    vraagID = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    TYPE_CHOICES = [
        ('T', 'Text'),
        ('I', 'Image'),
        ('M', 'Multiple Choice')
    ]
    type = models.CharField(max_length=255, choices=TYPE_CHOICES)
    omschrijving = models.CharField(max_length=255)
    juist_antwoord = models.CharField(max_length=255)
    downloadlink = models.CharField(max_length=255)
    punten = models.IntegerField(default=0)
    nakijken = models.IntegerField(default=0)

    def __int__(self):
        return self.vraagID

class Vraag_Antwoord(models.Model):
    vraagID = models.ForeignKey(Vraag, on_delete=models.CASCADE)
    keuzeEen = models.CharField(max_length=255)
    keuzeTwee = models.CharField(max_length=255)
    keuzeDrie = models.CharField(max_length=255)
    keuzeVier = models.CharField(max_length=255)
    correctAntwoord = models.IntegerField(max_length=4)

class Ronde(models.Model):
    toernooicode = models.ForeignKey(Toernooi, on_delete=models.CASCADE)
    rondenummer = models.IntegerField(default=1)
    duratie = models.IntegerField(default=0)

class Ronde_Vraag(models.Model):
    toernooicode = models.ForeignKey(Toernooi, on_delete=models.CASCADE)
    rondenummer = models.ForeignKey(Ronde, on_delete=models.CASCADE)
    vraagID = models.ForeignKey(Vraag, on_delete=models.CASCADE)
    disabled = models.IntegerField(default=0, null=True)

class Antwoord(models.Model):
    vraagID = models.ForeignKey(Vraag, on_delete=models.CASCADE)
    teamcode = models.ForeignKey(Team, on_delete=models.CASCADE)
    antwoord = models.CharField(max_length=255)
    tijd = models.TimeField(auto_now=True)
    correct = models.IntegerField(default=0)

class Timer(models.Model):
    toernooicode = models.OneToOneField(Toernooi, on_delete=models.CASCADE, primary_key=True)
    eindtijd = models.DateTimeField(null=True)
    current_timer_time = models.TimeField() # is only updated and relevant when active is set to 0
    start_time = models.DateTimeField(null=True) # for the progressbar
    active = models.IntegerField(default=0)
    set = models.IntegerField(default=0)

class Notification(models.Model):
    toernooicode = models.ForeignKey(Toernooi, on_delete=models.CASCADE)
    content = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now=True)