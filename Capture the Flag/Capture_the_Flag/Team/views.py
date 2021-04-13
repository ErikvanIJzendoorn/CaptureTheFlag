import hashlib
from django.core import serializers
from django.http import HttpResponse, HttpResponseRedirect, Http404, JsonResponse
from django.template import loader
from Capture_the_Flag.Admin.models import Team, Team_Toernooi, Vraag, Teamlid
from django.db import models
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404, render
from .forms import *

#def get_complementary(self):
#        if self == "":
#            return "#000000"
#        self = self[1:]
#        self = int(self, 16)
#        comp_color = 0xFFFFFF ^ self
#        comp_color = "#%06X" % comp_color
#        return comp_color

def dashboard(request, id):
    teams = Team.objects.filter(team_toernooi__toernooicode=id).order_by('-score')
    current_teamcode = request.COOKIES.get('team_teamcode')
    current_team = teams.filter(teamcode=current_teamcode)[0]
    max_rondes = Ronde.objects.filter(toernooicode=id).count()
    vraagCount = 2 + (Antwoord.objects.filter(teamcode_id=current_team.teamcode).count())
    team_has_name = False
    teamname_form = TeamNameForm()
    tournament = Toernooi.objects.get(toernooicode=id)
    try:
        current_round = Ronde.objects.get(toernooicode=id, rondenummer=tournament.current_round)
    except:
        return HttpResponseRedirect('/')


    if tournament.type == '1':
        vragen = Vraag.objects.filter(ronde_vraag__ronde=current_round)
    else:
        vragen = Vraag.objects.filter(ronde_vraag__ronde=current_round)[:vraagCount]

    if request.method == 'POST':
        form = TeamNameForm(request.POST, instance=current_team)
        if form.is_valid():
            if form.cleaned_data['naam'] != "":
                form.save()

    # Check if team has team name
    if current_team.naam != "":
        team_has_name = True

    antwoord = Antwoord.objects.filter(teamcode=request.COOKIES.get("team_teamcode"))
    context = { 
        'teams': teams,
        'current_team': current_team,
        'vragen' : vragen,
        'id' : id,
        'antwoorden': antwoord,
        'team_has_name' : team_has_name,
        'form': teamname_form,
        'current_round': tournament.current_round
    }

    template = loader.get_template('dashboard.html')
    return HttpResponse(template.render(context, request))

def vraag(request, vraagid, counter):
    template = loader.get_template('vraag.html')
    vraag = Vraag.objects.get(vraagID= vraagid)
    teamcode = request.COOKIES.get('team_teamcode')
    tournamentCode = request.COOKIES.get('team_tournamentCode')
    teams = Team.objects.filter(team_toernooi__toernooicode=tournamentCode).order_by('-score')
    tournament = Toernooi.objects.get(toernooicode=tournamentCode)
    current_team = Team.objects.get(teamcode=teamcode)
    answer = None
    timer = Timer.objects.get(toernooicode=tournamentCode)
    current_round = Ronde.objects.get(toernooicode=tournamentCode, rondenummer=tournament.current_round)
    vragen = Vraag.objects.filter(ronde_vraag__ronde=current_round)
    counter_max = vragen.count()
    backbutton_href = '#?first=true'
    nextbutton_href = '#?last=true'
    antwoord = Antwoord.objects.filter(teamcode=teamcode)

    try:
        ronde_vraag = Ronde_Vraag.objects.get(ronde=current_round, vraagID=vraag)
    except:
        return HttpResponseRedirect('/dashboard/' + tournamentCode)

    temp = vragen
    vragen = []
    for vr in temp:
        vragen.append(vr)

    try:
        backbutton_href = '/dashboard/vraag/' + str(vragen[int((counter - 1) - 1)].vraagID) + '/' + str(int(counter - 1))
    except:
        pass

    try:
        nextbutton_href = '/dashboard/vraag/' + str(vragen[int((counter + 1) - 1)].vraagID) + '/' + str(int(counter + 1))
    except:
        pass


    try:
        answer = Antwoord.objects.filter(teamcode=teamcode).filter(vraagID=vraagid).get()
    except:
        pass

    if timer.active == 0:
        return HttpResponseRedirect('/dashboard/' + tournamentCode)

    if ronde_vraag.disabled == 1:
        return HttpResponseRedirect('/dashboard/' + tournamentCode)

    if(vraag.type == 'T'):
        form = SubmitAnswerForm()
        context = {
            'vraag' : vraag, 
            'teams' : teams,
            'teamcode' : teamcode,
            'form' : form,
            'answer': answer,
            'counter': counter,
            'timer': timer,
            'tournamentCode': tournamentCode,
            'antwoorden': antwoord,
            'counter_max': counter_max,
            'backbutton_href': backbutton_href,
            'nextbutton_href': nextbutton_href,
            'current_team': current_team
        }
    elif(vraag.type == 'I'):
        form = SubmitImageAnswerForm()
        context = {
            'vraag' : vraag, 
            'teams' : teams,
            'teamcode' : teamcode,
            'form' : form,
            'answer': answer,
            'counter': counter,
            'timer': timer,
            'tournamentCode': tournamentCode,
            'antwoorden': antwoord,
            'counter_max': counter_max,
            'backbutton_href': backbutton_href,
            'nextbutton_href': nextbutton_href,
            'current_team': current_team
        }
    elif vraag.type == 'M':
        form = SubmitAnswerForm()
        keuzes = Vraag_Antwoord.objects.get(vraagID=vraagid)
        context = {
            'vraag' : vraag, 
            'teams' : teams,
            'teamcode' : teamcode,
            'form' : form,
            'keuzes': keuzes,
            'answer': answer,
            'counter': counter,
            'antwoorden': antwoord,
            'timer': timer,
            'tournamentCode': tournamentCode,
            'counter_max': counter_max,
            'backbutton_href': backbutton_href,
            'nextbutton_href': nextbutton_href,
            'current_team': current_team
        }

    if request.method == 'POST':
        if timer.active == 0:
            return HttpResponseRedirect('/dashboard/' + tournamentCode)

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
            post.teamcode = current_team
            post.vraagID = vraag

            if(vraag.type == 'T'):
                antwoord = request.POST.get('antwoord')
                upperantwoord = antwoord.upper()
                
                if upperantwoord == "":
                    response = HttpResponseRedirect('/dashboard/vraag/' + str(vraagid) + '/' + str(counter) + '?err=1')
                    return response

                if vraag.nakijken == 1:
                    post.correct = 0
                elif upperantwoord == vraag.juist_antwoord:
                    #if correct, VRAAG.correct is 1 (correct)
                    post.correct = 1
                else:
                    post.correct = 2

                post.antwoord = upperantwoord
           
            elif(vraag.type == 'M'):
                post.antwoord = request.POST.get('gekozen')
                if post.antwoord == vraag.juist_antwoord:
                    post.correct = 1
                else:
                    post.correct = 2

            elif(vraag.type == 'I'):
                post.antwoord = form.antwoord
                if post.antwoord == vraag.juist_antwoord:
                    post.correct = 1
                else:
                    post.correct = 2

            if(post.correct == 1):
                current_team.score += vraag.punten
                current_team.save()
            post.save()
            response = HttpResponseRedirect('/dashboard/vraag/' + str(vraagid) + '/' + str(counter))
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

def teamProfile(request, team_code):
    #Get team using teamcode
    current_team = get_object_or_404(Team, pk=team_code)
    #Get 1 team_toernooi using teamcode
    team_toernooi = Team_Toernooi.objects.get(teamcode = team_code)
    #Get teamleden using teamcode
    teamleden = Teamlid.objects.filter(teamcode = team_code)

    #Load page
    template = loader.get_template('teamProfile.html')

    if request.method == 'POST':

        if request.POST.get("add_student"):
            #Add saving teammembers
        
            model_with_code = Teamlid(teamcode=current_team)
        
            form = TeamMemberForm(request.POST, instance=model_with_code)

            if form.is_valid():
                form.save()
        else:
            student_name = request.POST['delete_student']
            Teamlid.objects.filter(teamcode = team_code, schermnaam = student_name).delete()

    form = TeamMemberForm()

    context = { 
        'current_team': current_team,
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
            'timestamp': notif.timestamp.strftime("%Y-%m-%dT%H:%M:%SZ"),
            'vraagID': notif.ronde_vraag.vraagID.vraagID,
            'disabled': notif.ronde_vraag.disabled
        }
        response.append(temp)

    #serialized = serializers.serialize('json', notifications)

    return JsonResponse(response, safe=False)

def editTeamProfile(request, team_code):
    #Get team using teamcode
    current_team = get_object_or_404(Team, pk=team_code)
    #Get 1 team_toernooi using teamcode
    team_toernooi = Team_Toernooi.objects.get(teamcode = team_code)

    template = loader.get_template('teamProfileEdit.html')

    if request.method == "POST":
        #model_with_code = Team(teamcode=team)
        
        form = TeamProfileForm(request.POST, instance=current_team)

        if form.is_valid():
            form.save()

    form = TeamProfileForm(instance=current_team)

    context = {
        'team_toernooi': team_toernooi,
        'current_team': current_team,
        'form': form}

    return HttpResponse(template.render(context, request))