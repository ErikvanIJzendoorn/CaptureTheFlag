from django.http import HttpResponse, HttpResponseRedirect, HttpRequest, JsonResponse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import authenticate, login as auth_login
from django.shortcuts import get_object_or_404, render
from django.forms.utils import ErrorList
from django.template import loader
from datetime import datetime, date
from .forms import *
from .models import *
import random
import string
from .clock import Clock

@user_passes_test(lambda u: u.groups.filter(name='admin').exists() or u.groups.filter(name='moderator').exists(), login_url='/')
def viewVragen(request):
    tournament = request.COOKIES.get('toernooicode')
    vragenlijst = Vraag.objects.all()
    context = {
        'vragenlijst': vragenlijst,
        'tournament' : tournament
    }
    return render(request, 'Admin/viewVragen.html',context)

@user_passes_test(lambda u: u.groups.filter(name='admin').exists() or u.groups.filter(name='moderator').exists(), login_url='/')
def createVraag(request):
    if request.method == 'POST':
        form = QuestionForm(request.POST)
        temp_form = request.POST.copy()
        
        if request.POST.get('type') == 'M':
            opties = request.POST.getlist('opties[]')
            correct = request.POST.get('correct')
            temp_form.update({'juist_antwoord': opties[int(correct)]})

        form = QuestionForm(data=temp_form)
        if form.is_valid():

            #stop form from posting.  Allow changes to be made
            post = form.save(commit=False)

            #turn juist_antwoord into all uppercase
            if(post.type == 'T'):
                post.juist_antwoord = post.juist_antwoord.upper()
            post.save()

            if post.type == 'M':
                vraagID = Vraag.objects.get(title=post.title, juist_antwoord=post.juist_antwoord)
                vraag_antwoord = Vraag_Antwoord(vraagID.vraagID, keuzeEen = opties[0], keuzeTwee = opties[1], keuzeDrie = opties[2], keuzeVier = opties[3], correctAntwoord = int(correct) + 1, vraagID_id = vraagID.vraagID)
                vraag_antwoord.save()

            tournament_code = request.COOKIES.get('toernooicode')
            if tournament_code:
                return HttpResponseRedirect('/admin/tournament/' + tournament_code)
            else:
                return HttpResponseRedirect('/admin/')
    else:
        form = QuestionForm()
    return render(request, 'Admin/createVraag.html', {'form': form})

@user_passes_test(lambda u: u.groups.filter(name='admin').exists() or u.groups.filter(name='moderator').exists(), login_url='/')
def createTournament(request):
    message = ''

    # if the form was submitted
    if request.method == 'POST':
        # generate tournament code
        tournament_code = generateRandomString(12, 'tour')

        # create model instance with code
        model_with_code = Toernooi(toernooicode=tournament_code, datum=datetime.now())

        # populate the model with form data from the request
        form = TournamentForm(request.POST, instance=model_with_code)

        # form validation
        if form.is_valid():
            # add the tournament to the database
            form.save()
            created_tournament = get_object_or_404(Toernooi, pk=tournament_code)

            # create timer instance
            timer = Timer(toernooicode=created_tournament, eindtijd=datetime.now(), current_timer_time='00:00:00')

            # add the timer to the database
            timer.save()

            message = "Toernooi succesvol aangemaakt met toernooicode " + tournament_code
            # redirect to the tournament view page
            response = HttpResponseRedirect('/admin/tournament/' + tournament_code)
            response.set_cookie('toernooicode', tournament_code)
            return response

        else:
            # set errormessage
            message = form.errors        

            # return back to the create tournament template
            return render(request, 'Admin/createTournament.html', {'form': form, 'message': message})

    else:
        # leave the form empty
        form = TournamentForm()

    # render the template
    return render(request, 'Admin/createTournament.html', {'form': form, 'message': message})

@user_passes_test(lambda u: u.groups.filter(name='admin').exists() or u.groups.filter(name='moderator').exists(), login_url='/')
def viewTournament(request, tournament_code):
    # get tournament by tournament code
    tournament = get_object_or_404(Toernooi, pk=tournament_code)

    # if the add team form was filled out
    if request.method == 'POST':
        # populate the form with requestdata
        form = TeamForm(request.POST)

        if form.is_valid():
            # further process the addition of so much teams
            amount = form.cleaned_data['team_amount']

            # generate teamcodes and store teams in the database
            for i in range(amount):
                new_code = generateRandomString(8, 'team')

                team = Team(teamcode=new_code)
                team_tournament = Team_Toernooi(teamcode=team, toernooicode=tournament)

                team.save()
                team_tournament.save()

            message = "Teams succesvol toegevoegd!"

        else:
            message = "Er was een probleem tijdens het valideren"

    # if there was no form filled out
    else:
        # init empty form
        form = TeamForm()

        message = ""


    # get teams by tournament code
    teams = Team.objects.filter(team_toernooi__toernooicode=tournament_code)
    rondes = Ronde.objects.filter(toernooicode=tournament_code)
    #mods = Gebruiker.objects.raw('SELECT userID, username FROM Admin_gebruiker LEFT JOIN Admin_gebruiker_toernooi ON userID = Admin_gebruiker_toernooi.userID_id WHERE Admin_gebruiker_toernooi.toernooicode_id = %s AND Admin_gebruiker_toernooi.rol = 1', [tournament_code])
    #scheidsrechters = Gebruiker.objects.raw('SELECT userID, username FROM Admin_gebruiker LEFT JOIN Admin_gebruiker_toernooi ON userID = Admin_gebruiker_toernooi.userID_id WHERE Admin_gebruiker_toernooi.toernooicode_id = %s AND Admin_gebruiker_toernooi.rol = 2', [tournament_code])
    modss = tournament.gebruiker_toernooi_set.filter(rol=1)
    mods = []
    for m in modss:
        mods.append(m.userID)
    scheidsrechterss = tournament.gebruiker_toernooi_set.filter(rol=2)
    scheidsrechters = []
    for s in scheidsrechterss:
        scheidsrechters.append(s.userID)

    context = {
        'form': form, 
        'tournament': tournament, 
        'teams': teams, 
        'message': message,
        'rondes': rondes,
        'mods': mods,
        'scheidsrechters': scheidsrechters,
    }
    response = render(request, 'Admin/viewTournament.html', context)
    response.set_cookie('toernooicode', tournament_code)
    return response
    # render page

def generateRandomString(length, type):
    """
    type determines in which table the method is going to check for duplicate keys
    team = teams
    tour = tournaments
    """
    lettersAndDigits = string.ascii_letters + string.digits + string.digits + string.digits
    code = ''.join((random.choice(lettersAndDigits) for i in range(length)))

    # check if code is already in database (unlikely, but still)
    if type == "tour":
        foundCode = Toernooi.objects.filter(toernooicode=code)
    elif type == "team":
        foundCode = Team.objects.filter(teamcode=code)
    else:
        raise ValueError("type must be either team or tour")

    # if so, start over
    if foundCode:
        generateRandomString(length, type)

    # if not, return code
    return code

@user_passes_test(lambda u: u.groups.filter(name='admin').exists() or u.groups.filter(name='moderator').exists(), login_url='/')
def editVraag(request, vraagID, rondenummer=0):
    vraag = get_object_or_404(Vraag, pk=vraagID)
    if(request.method == 'POST'):
        if vraag.type == 'M':
            temp_form = request.POST.copy()
            opties = request.POST.getlist('opties[]')
            correct = int(request.POST.get('correct')) - 1
            temp_form.update({'juist_antwoord': opties[correct]})
            form = ModifyQuestionForm(data = temp_form, instance = vraag)
        else:
            form = ModifyQuestionForm(request.POST, instance = vraag)
            post = form.save(commit=False)
            if(post.type == 'T'):
                post.juist_antwoord = post.juist_antwoord.upper()
            post.save()
        if form.is_valid():
            form.save()
            if vraag.type == 'M':
                vraag_antwoord = Vraag_Antwoord(vraag.vraagID, keuzeEen = opties[0], keuzeTwee = opties[1], keuzeDrie = opties[2], keuzeVier = opties[3], correctAntwoord = correct + 1, vraagID_id = vraag.vraagID)
                vraag_antwoord.save()
            
            tournament_code = request.COOKIES.get('toernooicode')
            if tournament_code:
                if rondenummer != 0:
                    tournament = get_object_or_404(Toernooi, pk=tournament_code)
                    return HttpResponseRedirect('/admin/controlpanel/' + tournament_code + '/' + str(rondenummer) + '/' + str(vraagID) + '/')
                else:
                    return HttpResponseRedirect('/admin/modify/vraag/')
            else:
                return HttpResponseRedirect('/admin/')

    else:
        form = ModifyQuestionForm(instance=vraag)

    context = {
        'vraag' : vraag,
        'form': form
    }

    if vraag.type == 'M':
        opties = Vraag_Antwoord.objects.get(pk=vraag.vraagID)
        context.update({'opties': opties})

    return render(request, 'Admin/modifyQuestion.html', context)

@user_passes_test(lambda u: u.groups.filter(name='admin').exists() or u.groups.filter(name='moderator').exists(), login_url='/')
def createRonde(request, tournament_code):
    message = ''
    roundCount = Ronde.objects.filter(toernooicode=tournament_code).count() + 1
    tournament = Toernooi.objects.filter(toernooicode=tournament_code)
    vraag_ronde = Ronde_Vraag.objects.filter(toernooicode=tournament_code)
    huidige_vragen = []
    alle_vragen = Vraag.objects.all()  

    for v in vraag_ronde:
        vraagID = v.vraagID_id
        vraag = Vraag.objects.get(pk=vraagID)
        huidige_vragen.append(vraag)

    vragenlijst = list(set(alle_vragen) - set(huidige_vragen))

    if not tournament:
        message = 'Geen toernooi gevonden met deze code'
        return HttpResponse(message)

    # if the form was submitted
    if request.method == 'POST':

        # populate the model with form data from the request
        form = RoundForm(request.POST)

        tournament = get_object_or_404(Toernooi, pk=tournament_code)
        
        # form validation
        if form.is_valid():
            gekozenVragen = request.POST.getlist('vragen[]')
            tournament = Toernooi.objects.get(pk=tournament_code)
            # Check if duration > 0
            if form.cleaned_data['duratie'] >= 10:
                # add the round to the database
                obj = form.save(commit=False)
                obj.toernooicode = tournament
                obj.rondenummer = roundCount                

                if len(gekozenVragen) != 0:
                    for vraag in gekozenVragen:

                        bestaand = Ronde_Vraag.objects.filter(toernooicode=tournament, vraagID=vraag)
                        if bestaand:
                            message = "De volgende vraag zit al in het toernooi: " + Vraag.objects.get(pk=vraag).title
                            context = {
                                'message': message,
                                'tournament': tournament_code,
                                'RoundCount': roundCount,
                                'form': form,
                                'vragenlijst': vragenlijst
                            }
                            return render(request, 'Admin/createRonde.html', context)
                        else:
                            form.save()
                            ronde = Ronde.objects.get(toernooicode=tournament_code, rondenummer=roundCount)
                            vraag = Vraag.objects.get(pk=vraag)
                            v = Ronde_Vraag.objects.create(toernooicode=tournament, ronde=ronde, rondenummer=roundCount, vraagID=vraag)
                            v.save()
                            message = "Succesfully created a round"
                else:
                    message = 'Er zijn geen vragen toegevoegd aan de ronde, dit moet wel'
                    context = {
                        'message': message,
                        'tournament': tournament_code,
                        'RoundCount': roundCount,
                        'form': form,
                        'vragenlijst': vragenlijst
                    }
                    return render(request, 'Admin/createRonde.html', context)

                
                return HttpResponseRedirect('/admin/tournament/' + tournament_code)

            else :
                message = 'De duratie kan niet kleiner dan 10 minuten zijn'
                context = {
                    'message': message,
                    'tournament': tournament_code,
                    'RoundCount': roundCount,
                    'form': form,
                    'vragenlijst': vragenlijst
                }
                response = render(request, 'Admin/createRonde.html', context)
                response.set_cookie('error_CreateRonde', message)
                return response

        else:
            # set errormessage
            message = 'Invalid form input'
            
            # return back to the create ronde template
            return render(request, 'Admin/createRonde.html', {'form': form, 'message': message})

    else:
        if tournament:
            # leave the form empty
            form = RoundForm()
        else: 
            message = 'Geen toernooi gevonden met deze code'

    context = {
        'message': message,
        'tournament': tournament_code,
        'RoundCount': roundCount,
        'form': form,
        'vragenlijst': vragenlijst
    }
    # render the template
    response = render(request, 'Admin/createRonde.html', context)
    response.delete_cookie('error_CreateRonde')
    return response

@user_passes_test(lambda u: u.groups.filter(name='admin').exists() or u.groups.filter(name='moderator').exists(), login_url='/')
def resetTournament(request, tournament_code):
    """
    quickly reset the tournament for testing.
    for development purposes only, deletes all answers and scores given by participants
    """
    tournament = get_object_or_404(Toernooi, pk=tournament_code)
    tournament.current_round = 1

    tournament.save()

    # set score of all teams to zero
    teams = Team.objects.filter(team_toernooi__toernooicode=tournament_code)
    for team in teams:
        team.score = 0
        team.save()

    # delete all answers for this tournament
    Antwoord.objects.filter(teamcode__team_toernooi__toernooicode=tournament_code).delete()

    return HttpResponseRedirect('/admin/controlpanel/' + tournament_code + '/timer/reset/')

@user_passes_test(lambda u: u.groups.filter(name='admin').exists() or u.groups.filter(name='moderator').exists(), login_url='/')
def controlPanel(request, tournament_code):
    # get relevant data from database
    tournament = get_object_or_404(Toernooi, pk=tournament_code)
    rounds = Ronde.objects.filter(toernooicode=tournament_code)
    questions = []

    # get questions per round
    for round in rounds:
        questions.append(Vraag.objects.filter(ronde_vraag__ronde=round))

    teams = Team.objects.filter(team_toernooi__toernooicode=tournament_code).order_by('-score')
    clock = get_object_or_404(Timer, pk=tournament_code)

    # if timer not active and not set, set timer for that rounds duration
    if clock.active == 0 and clock.set == 0:
        timer = Clock(tournament_code)
        timer.reset()

    # create context
    context = {'tournament': tournament, 'rounds': rounds, 'questions': questions, 'teams': teams, 'clock': clock}

    # render page
    return render(request, 'Admin/controlPanel.html', context)

@user_passes_test(lambda u: u.groups.filter(name='admin').exists() or u.groups.filter(name='moderator').exists(), login_url='/')
def setTimer(request, tournament_code, minutes):
    timer = get_object_or_404(Timer, pk=tournament_code)
    clock = Clock(tournament_code)

    clock.set(minutes)

    return HttpResponseRedirect('/admin/controlpanel/' + tournament_code)

@user_passes_test(lambda u: u.groups.filter(name='admin').exists() or u.groups.filter(name='moderator').exists(), login_url='/')
def resetTimer(request, tournament_code):
    timer = get_object_or_404(Timer, pk=tournament_code)
    clock = Clock(tournament_code)

    clock.reset()

    return HttpResponseRedirect('/admin/controlpanel/' + tournament_code)

@user_passes_test(lambda u: u.groups.filter(name='admin').exists() or u.groups.filter(name='moderator').exists(), login_url='/')
def startTimer(request, tournament_code):
    timer = get_object_or_404(Timer, pk=tournament_code)
    clock = Clock(tournament_code)

    clock.start()

    return HttpResponseRedirect('/admin/controlpanel/' + tournament_code)

@user_passes_test(lambda u: u.groups.filter(name='admin').exists() or u.groups.filter(name='moderator').exists(), login_url='/')
def pauseTimer(request, tournament_code):
    timer = get_object_or_404(Timer, pk=tournament_code)
    clock = Clock(tournament_code)

    clock.pause()

    return HttpResponseRedirect('/admin/controlpanel/' + tournament_code)

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

@user_passes_test(lambda u: u.groups.filter(name='admin').exists() or u.groups.filter(name='moderator').exists(), login_url='/')
def viewTournamentList(request):
    tournaments = Toernooi.objects.all()
    if(request.user.groups.filter(name='admin').exists()):
        userTournaments = Toernooi.objects.all()
    elif(request.user.groups.filter(name='moderator').exists()):
        userTournaments = []
        for t in request.user.gebruiker_toernooi_set.all():
            userTournaments.append(t.toernooicode)
    return render(request, 'Admin/tournamentList.html', {'tournaments': userTournaments})

@user_passes_test(lambda u: u.groups.filter(name='admin').exists() or u.groups.filter(name='moderator').exists(), login_url='/')
def manageQuestion(request, tournament_code, rondenummer, vraagID):
    #question = Vraag.objects.filter(ronde_vraag__rondenummer=rondenummer).filter(vraagID=vraagID).filter(ronde_vraag__toernooicode=tournament_code)
    question = get_object_or_404(Vraag, pk=vraagID)
    tournament = get_object_or_404(Toernooi, pk=tournament_code)
    ronde = Ronde.objects.filter(toernooicode=tournament_code).filter(rondenummer=rondenummer).get()
    disabled = Ronde_Vraag.objects.filter(toernooicode=tournament_code).filter(ronde=ronde, vraagID=vraagID).get().disabled
    #teams_answers = Team.objects.raw("SELECT * FROM Admin_Team JOIN Admin_Antwoord ON teamcode")
    teams = Team.objects.filter(team_toernooi__toernooicode=tournament_code)
    answer = Antwoord.objects.all()

    # build context
    context = {
        'question': question,
        'tournament': tournament,
        'round': rondenummer,
        'disabled': disabled,
        #'answers': teams_answers
        'teams' : teams,
        'answer' : answer,
    }

    return render(request, 'Admin/manageQuestion.html', context)

@user_passes_test(lambda u: u.groups.filter(name='admin').exists() or u.groups.filter(name='moderator').exists(), login_url='/')
def changeResult(request, tournament_code, rondenummer, vraagID, team_code):
    antwoord = get_object_or_404(Antwoord, vraagID=vraagID, teamcode_id=team_code)
    team = get_object_or_404(Team, teamcode=team_code)
    vraag = get_object_or_404(Vraag, vraagID = vraagID)
    if antwoord.correct == 0:
        if antwoord.antwoord ==  vraag.juist_antwoord:
            antwoord.correct = 1
            team.score += vraag.punten
        else:
            antwoord.correct = 2
    elif antwoord.correct == 1: #goed
        antwoord.correct = 2 #naar fout
        if (team.score - vraag.punten) < 0:
            team.score = 0
        else:
            team.score -= vraag.punten
    elif antwoord.correct == 2: #fout
        antwoord.correct = 1 #naar goed
        team.score += vraag.punten
    antwoord.save()
    team.save()

    return HttpResponseRedirect('/admin/controlpanel/' + tournament_code + '/' + str(rondenummer) + '/' + str(vraagID))

@user_passes_test(lambda u: u.groups.filter(name='admin').exists() or u.groups.filter(name='moderator').exists(), login_url='/')
def disableQuestion(request, tournament_code, rondenummer, vraagID):
    ronde = Ronde.objects.filter(toernooicode=tournament_code).filter(rondenummer=rondenummer).get()
    ronde_vraag = Ronde_Vraag.objects.filter(toernooicode=tournament_code).filter(ronde=ronde, vraagID=vraagID).get()
    vraag = get_object_or_404(Vraag, pk=vraagID)

    if ronde_vraag.disabled == 0:
        ronde_vraag.disabled = 1
        sendNotification(tournament_code, ronde_vraag, vraag.title + " is door het beheer uitgeschakeld.<br>Deze vraag is nu niet meer te bekijken of te beantwoorden.")
    else:
        ronde_vraag.disabled = 0
        sendNotification(tournament_code, ronde_vraag, vraag.title + " is door het beheer ingeschakeld.<br>Deze vraag is nu weer te bekijken en te beantwoorden.")

    ronde_vraag.save()

    return HttpResponseRedirect('/admin/controlpanel/' + tournament_code + '/' + str(rondenummer) + '/' + str(vraagID))

def sendNotification(tournament_code, ronde_vraag, content):
    tournament = get_object_or_404(Toernooi, pk=tournament_code)
    notif = Notification.objects.create(toernooicode=tournament, content=content, ronde_vraag=ronde_vraag)
    notif.save()

@user_passes_test(lambda u: u.groups.filter(name='admin').exists() or u.groups.filter(name='moderator').exists(), login_url='/')
def scheidsrechterToevoegen(request, tournament_code):
    tournament = get_object_or_404(Toernooi, pk=tournament_code)
    modss = tournament.gebruiker_toernooi_set.filter(rol=1)
    mods = []
    for m in modss:
        mods.append(m.userID)
    scheidsrechterss = tournament.gebruiker_toernooi_set.filter(rol=2)
    scheidsrechters = []
    for s in scheidsrechterss:
        scheidsrechters.append(s.userID)

    mogelijkeScheidsrechters = []
    for u in User.objects.all():
        if(u not in mods and u not in scheidsrechters):
            mogelijkeScheidsrechters.append(u.username)

    if(request.method == 'POST'):
        form = AssignScheidsrechterForm(request.POST)
        if(form.data['gebruikers'] is not None):
            gebruiker = User.objects.get(id = form.data['gebruikers'])
            GebruikerToernooi = Gebruiker_Toernooi(userID = gebruiker, toernooicode = tournament, rol = 2)
            GebruikerToernooi.save()
            return HttpResponseRedirect('/admin/tournament/' + tournament_code + '/')
    else:
        form = AssignScheidsrechterForm(mogelijkeScheidsrechters = mogelijkeScheidsrechters)

    return render(request, 'Admin/assignScheidsrechter.html', {'form': form})

@user_passes_test(lambda u: u.groups.filter(name='admin').exists() or u.groups.filter(name='moderator').exists(), login_url='/')
def toernooibeheerderWijzigen(request, tournament_code):
    if(request.method == 'POST'):
        form = toernooibeheerderWijzigenForm(request.POST)
        tournament = get_object_or_404(Toernooi, pk=tournament_code)

        if(form.is_valid()):
            gebruiker = User.objects.get(id = form.data['gebruikers'])
            GebruikerToernooi = Gebruiker_Toernooi.objects.get(userID = request.user)
            GebruikerToernooi.delete()

            try:
                NieuweGebruikerToernooi = Gebruiker_Toernooi.objects.get(userID = gebruiker)
            except Gebruiker_Toernooi.DoesNotExist:
                NieuweGebruikerToernooi = Gebruiker_Toernooi(userID = gebruiker, toernooicode = tournament, rol = 1)

            NieuweGebruikerToernooi.save()
            return HttpResponseRedirect('/admin/')
    else:
        form = toernooibeheerderWijzigenForm()

    return render(request, 'Admin/toernooibeheerderWijzigen.html', {'form': form})

@user_passes_test(lambda u: u.groups.filter(name='admin').exists() or u.groups.filter(name='moderator').exists(), login_url='/')
def EditRound(request, tournament_code, rondeID):
    round = Ronde.objects.get(pk=rondeID)
    print(round)
    alle_vragen = Vraag.objects.all()
    tournament = request.COOKIES.get('toernooicode')
    if(request.method == 'POST'):
        form = RoundForm(request.POST, instance=round)
        remove = request.POST.getlist('verwijderen[]')
        add = request.POST.getlist('toevoegen[]')
        if form.is_valid():
            form.save()
            for vraag in remove:
                ronde = Ronde.objects.get(pk=rondeID)
                v = Ronde_Vraag.objects.get(vraagID=vraag, ronde=round)
                v.delete()

            for vraag in add:
                vraag = Vraag.objects.get(pk=vraag)
                toernooi = Toernooi.objects.get(pk=tournament_code)
                ronde = Ronde.objects.get(pk=round.id)
                v = Ronde_Vraag.objects.create(toernooicode=toernooi, rondenummer=ronde.rondenummer, ronde=ronde, vraagID=vraag)
                v.save()
            return HttpResponseRedirect('/admin/tournament/' + tournament_code + '/modify/ronde/' + str(rondeID))

    else:
        
        huidige_vragen = []
        gekozen_vragen = []
        rondes = Ronde.objects.filter(toernooicode=tournament_code)
        for ronde in rondes:
            vraag_ronde = Ronde_Vraag.objects.filter(ronde=ronde)
            for v in vraag_ronde:
                vraagID = v.vraagID_id
                vraag = Vraag.objects.get(pk=vraagID)
                if ronde.id == rondeID:
                    huidige_vragen.append(vraag)
                gekozen_vragen.append(vraag)
        
        vragenlijst = list(set(alle_vragen) - set(gekozen_vragen))

        form = RoundForm(instance=round)

    return render(request, 'Admin/modifyRound.html', {'form': form, 'huidige_vragen': huidige_vragen, 'vragenlijst': vragenlijst, 'tournament': tournament})

@user_passes_test(lambda u: u.groups.filter(name='admin').exists() or u.groups.filter(name='moderator').exists(), login_url='/')
def teamVerwijderen(request, tournament_code):
    team = Team_Toernooi.objects.filter(toernooicode=tournament_code).order_by('-id')[0]
    gekozen_team = Team.objects.get(teamcode=team.teamcode_id)
    team.delete()
    gekozen_team.delete()
    return HttpResponseRedirect('/admin/tournament/' + tournament_code)

@user_passes_test(lambda u: u.groups.filter(name='admin').exists() or u.groups.filter(name='moderator').exists(), login_url='/')
def dashboard(request, tournament_code):
    tournament = get_object_or_404(Toernooi, pk=tournament_code)
    teams = Team.objects.filter(team_toernooi__toernooicode=tournament_code).order_by('-score')[:10]
    round = Ronde.objects.get(toernooicode=tournament_code, rondenummer=tournament.current_round)

    context = {
        'tournament' : tournament,
        'teams': teams,
        'round' : tournament.current_round}
    return render(request, 'Admin/dashboard.html', context)


@user_passes_test(lambda u: u.groups.filter(name='admin').exists() or u.groups.filter(name='moderator').exists(), login_url='/')
def ajaxGetScoreboard(request, tournament_code):
    tournament = get_object_or_404(Toernooi, pk=tournament_code)
    timer = get_object_or_404(Timer, pk=tournament_code)
    dbteams = Team.objects.filter(team_toernooi__toernooicode=tournament_code).order_by('-score')[:10]
    total_rounds = Ronde.objects.filter(toernooicode=tournament_code).count()
    round = 0
    teams = []


    for t in dbteams:
        team = {
            'naam': t.naam,
            'score': t.score
        }
        teams.append(team)

    timerdata = {
        'active': timer.active,
        'set': timer.set,
        'current_timer_time': timer.current_timer_time,
        'start_time': timer.start_time,
        'endtime': timer.eindtijd,
    }

    if tournament.current_round > total_rounds:
        round = -1
    else:
        round = tournament.current_round

    data = {
        'teams': teams,
        'round' : round,
        'timer': timerdata
    }

    return JsonResponse(data)