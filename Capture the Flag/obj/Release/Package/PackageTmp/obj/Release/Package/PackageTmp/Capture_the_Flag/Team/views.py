import hashlib
from django.core import serializers
from django.http import HttpResponse, HttpResponseRedirect, Http404, JsonResponse
from django.template import loader
from Capture_the_Flag.Admin.models import Team, Team_Toernooi, Vraag, Teamlid
from django.db import models
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404, render
from .forms import *

def dashboard(request, id):
    teams = Team.objects.filter(team_toernooi__toernooicode=id)
    current_teamcode = request.COOKIES.get('team_teamcode')
    current_team = teams.filter(teamcode=current_teamcode)[0]
    vraag = Vraag.objects.all()
    team_has_name = False
    teamname_form = TeamNameForm()

    if request.method == 'POST':
        form = TeamNameForm(request.POST, instance=current_team)
        if form.is_valid():
            if form.cleaned_data['naam'] != "":
                form.save()

    # Check if team has team name
    if current_team.naam != "":
        team_has_name = True

    antwoord = Antwoord.objects.filter(teamcode=request.COOKIES.get("team_teamcode"))
    print(antwoord)
    context = { 
        'teams': teams,
        'current_team': current_team,
        'vragen' : vraag,
        'id' : id,
        'antwoorden': antwoord,
        'team_has_name' : team_has_name,
        'form': teamname_form
    }

    template = loader.get_template('dashboard.html')
    return HttpResponse(template.render(context, request))

def vraag(request, vraagid):
    template = loader.get_template('vraag.html')
    vraag = Vraag.objects.get(vraagID= vraagid)
    teams = Team.objects.all()
    teamcode = request.COOKIES.get('team_teamcode')
    tournamentCode = request.COOKIES.get('team_tournamentCode')
    team = Team.objects.get(teamcode=teamcode)
    print(teamcode)

    if(vraag.type == 'T'):
        form = SubmitAnswerForm()
        context = {
            'vraag' : vraag, 
            'teams' : teams,
            'teamcode' : teamcode,
            'form' : form
        }
    elif(vraag.type == 'I'):
        form = SubmitImageAnswerForm()
        context = {
            'vraag' : vraag, 
            'teams' : teams,
            'teamcode' : teamcode,
            'form' : form
        }
    elif vraag.type == 'M':
        form = SubmitAnswerForm()
        keuzes = Vraag_Antwoord.objects.get(vraagID=vraagid)
        context = {
            'vraag' : vraag, 
            'teams' : teams,
            'teamcode' : teamcode,
            'form' : form,
            'keuzes': keuzes
        }

    if request.method == 'POST':
        if(vraag.type == 'T'):
            form = SubmitAnswerForm(request.POST)
        elif(vraag.type == 'I'):
            form = SubmitImageAnswerForm(request.POST, request.FILES)
        elif vraag.type == 'M':
            form = SubmitAnswerForm(request.POST)
            temp_form = request.POST.copy()
            temp_form.update({'antwoord': temp_form['gekozen']})
            form = SubmitAnswerForm(data=temp_form)

        if form.is_valid():

            if(vraag.type == 'I'):
                image = request.FILES.get('antwoord')
                hash = 0
                form = SubmitAnswerForm()

                md5 = hashlib.md5()
                for chunk in image.chunks():
                    md5.update(chunk)
                    hash = md5.hexdigest()
                form.antwoord = hash

            #stop from immediately posting.  Allows for changes to be made
            post = form.save(commit=False)
            post.teamcode = team
            post.vraagID = vraag

            if(vraag.type == 'T') or (vraag.type == 'M'):
                if vraag.type == 'M':
                     antwoord = request.POST.get('gekozen')
                else:
                    antwoord = request.POST.get('antwoord')
                #Removes all punctuation from the string.
                punctuation = "!@#$%^&*()_+<>?:.,;"
                upperantwoord = antwoord.upper()
                for s in upperantwoord:
                   if s in punctuation:
                       upperantwoord = upperantwoord.replace(s, "")
                   #checks whether the given answer is the same as the answer
                   #from VRAAG.juist_antwoord
                   print(upperantwoord)
                   print(vraag.juist_antwoord)
                if upperantwoord == vraag.juist_antwoord:
                    #if correct, VRAAG.correct is 1 (correct)
                    post.correct = 1
                else:
                    post.correct = 2
                #change the input answer the non-punctuated answer.  Turns it
                #into all uppercase
                post.antwoord = upperantwoord

            elif(vraag.type == 'I'):
                post.antwoord = form.antwoord
                if post.antwoord == vraag.juist_antwoord:
                    post.correct = 1
                else:
                    post.correct = 2

            print(post.correct) # dit werkt
            print(vraag.punten)
            print(team.score)

            if(post.correct == 1):
                team.score += vraag.punten
                team.save()
            print(team.score)
            post.save()
            response = HttpResponseRedirect('/dashboard/' + tournamentCode)
            return response
        else:
            if(vraag.type == 'T'):
                form = SubmitAnswerForm(request.POST)
            elif(vraag.type == 'I'):
                form = SubmitImageAnswerForm(request.POST)
            #response = HttpResponseRedirect('/dashboard/')
            #return response
    else: 

        return render(request, 'dashboard/vraag.html', context)

def login(request):
    message = ''
    template = loader.get_template('login.html')

    if request.method == 'POST':
        form = TeamLoginForm(request.POST)

        if form.is_valid():
            data = request.POST.copy()
            tournamentCode = data.get('tournamentCode')
            teamCode = data.get('teamCode')
            

            # Check if toernooicode en teamcode is a combo
            foundTeamInTournament = Team_Toernooi.objects.filter(toernooicode_id=tournamentCode). filter(teamcode_id=teamCode)
            
            # Check if tournament exists
            if foundTeamInTournament:
                response = HttpResponseRedirect('../dashboard/' + tournamentCode)
                response.set_cookie('team_tournamentCode', tournamentCode)
                response.set_cookie('team_teamcode', teamCode)
                return response
            else:

                message = "Login failed. Combination not found"
                # TODO: add error messages if login failed
                return HttpResponse(template.render({'form': form, 'message': message}, request))
           
    else:
        form = TeamLoginForm()
    return HttpResponse(template.render({'form': form, 'message': message}, request))

#def vragenlijst(request):
#    vraag = Vraag.objects.all()
#    context = {
#        'vragen' : vraag
#        }
#    return render(request, 'Vragenlijst/vragenlijst.html', context)
def teamProfile(request, team_code):    
    #Get team using teamcode
    team = get_object_or_404(Team, pk=team_code)
    #Get 1 team_toernooi using teamcode
    team_toernooi = Team_Toernooi.objects.get(teamcode = team_code)
    #Get teamleden using teamcode
    teamleden = Teamlid.objects.filter(teamcode = team_code)

    #Load page
    template = loader.get_template('teamProfile.html')

    if request.method == 'POST':

        if request.POST.get("add_student"):
            #Add saving teammembers
        
            model_with_code = Teamlid(teamcode=team)
        
            form = TeamMemberForm(request.POST, instance=model_with_code)

            if form.is_valid():
                form.save()
        else:
            student_name = request.POST['delete_student']
            Teamlid.objects.filter(teamcode = team_code, schermnaam = student_name).delete()
            


    form = TeamMemberForm()

    context = { 
        'team': team,
        'team_toernooi': team_toernooi,
        'teamleden': teamleden,
        'form': form
    }

    return HttpResponse(template.render(context, request))


def ajaxGetTimer(request, tournament_code):
    timer = get_object_or_404(Timer, pk=tournament_code)
    tournament = get_object_or_404(Toernooi, pk=tournament_code)
    total_rounds = Ronde.objects.filter(toernooicode=tournament_code).count()
    round = 0

    if tournament.current_round > total_rounds:
        round = -1
    else:
        round = tournament.current_round

    data = {
        'active': timer.active,
        'set': timer.set,
        'current_timer_time': timer.current_timer_time,
        'start_time': timer.start_time,
        'endtime': timer.eindtijd,
        'round': round
    }

    return JsonResponse(data)


def ajaxGetNotifications(request, tournament_code):
    notifications = Notification.objects.filter(toernooicode=tournament_code)
    response = []

    for notif in notifications:
        temp = {
            'id': notif.id,
            'content': notif.content,
            'timestamp': notif.timestamp.strftime("%Y-%m-%dT%H:%M:%SZ")
        }
        response.append(temp)

    #serialized = serializers.serialize('json', notifications)

    return JsonResponse(response, safe=False)

def editTeamProfile(request, team_code):
    #Get team using teamcode
    team = get_object_or_404(Team, pk=team_code)

    template = loader.get_template('teamProfileEdit.html')

    form = TeamProfileForm(instance=team)

    context = {
        'team': team,
        'form': form}

    return HttpResponse(template.render(context, request))