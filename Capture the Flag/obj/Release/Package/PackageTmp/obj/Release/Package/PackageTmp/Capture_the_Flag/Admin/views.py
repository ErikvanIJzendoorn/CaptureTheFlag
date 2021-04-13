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

def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")


def viewVragen(request):
    vragenlijst = Vraag.objects.all()
    context = {
        'vragenlijst': vragenlijst,
    }
    return render(request, 'Admin/viewVragen.html',context)

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
            post.juist_antwoord = post.juist_antwoord.upper()
            post.save()

            if post.type == 'M':
                vraagID = Vraag.objects.get(title=post.title, juist_antwoord=post.juist_antwoord)
                vraag_antwoord = Vraag_Antwoord(vraagID.vraagID, keuzeEen = opties[0].upper(), keuzeTwee = opties[1].upper(), keuzeDrie = opties[2].upper(), keuzeVier = opties[3].upper(), correctAntwoord = int(correct) + 1, vraagID_id = vraagID.vraagID)
                vraag_antwoord.save()

            tournament_code = request.COOKIES.get('toernooicode')
            if tournament_code:
                return HttpResponseRedirect('/admin/tournament/' + tournament_code)
            else:
                return HttpResponseRedirect('/admin/')
    else:
        form = QuestionForm()
    return render(request, 'Admin/createVraag.html', {'form': form})


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

    # render page
    return render(request, 'Admin/viewTournament.html', context)


def assessableAnswers(request, tournament_code):
    # get tournament
    tournament = get_object_or_404(Toernooi, pk=tournament_code)
    # get assessable questions
    answers = Antwoord.objects.filter(teamcode__team_toernooi__toernooicode=tournament_code).filter(correct=0)

    # render page
    return render(request, 'Admin/assessableAnswers.html', {'answers': answers, 'tournament': tournament})


def assessAnswer(request, tournament_code, answer_id):
    # get answer, tournament and question
    answer = get_object_or_404(Antwoord, pk=answer_id)
    question = get_object_or_404(Vraag, pk=answer.vraagID.vraagID)
    tournament = get_object_or_404(Toernooi, pk=tournament_code)

    # if the form was filed out
    if request.method == 'POST':
        # fill form with request
        form = AssessForm(request.POST)

        # process data
        if form.is_valid():
            # if the teacher deems the answer correct
            if form.cleaned_data['correct'] == True:
                answer.correct = 1
            else:
                answer.correct = 0
            answer.save()

            # return back to the overview
            return HttpResponseRedirect('/admin/assess/' + tournament_code)

    # init empty form
    form = AssessForm()

    # render page
    return render(request, 'Admin/assessAnswer.html', {'question': question, 'answer': answer, 'tournament': tournament, 'form': form})


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


def editVraag(request, vraagID):
    vraag = get_object_or_404(Vraag, pk=vraagID)
    if(request.method == 'POST'):
        form = QuestionForm(request.POST, instance=vraag)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/admin/')

    else:
        form = QuestionForm(instance=vraag)

    return render(request, 'Admin/modify.html', {'form': form})

def login(request):
    if(request.user.is_authenticated):
        return HttpResponseRedirect('/admin/')

    else:
        if request.method == 'POST':
            form = LoginForm(request.POST)
            username = request.POST['username']
            password = request.POST['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                auth_login(request, user)
                return HttpResponseRedirect('/admin/')

        else:
            form = LoginForm()

        return render(request, 'Admin/login.html', {'form': form})

def createRonde(request, tournament_code):
    message = ''
    roundCount = Ronde.objects.filter(toernooicode=tournament_code).count() + 1
    tournament = Toernooi.objects.filter(toernooicode=tournament_code)
    vragenlijst = Vraag.objects.all()

    if not tournament:
        message = 'Geen toernooi gevonden met deze code'
        return HttpResponse(message)

    # if the form was submitted
    if request.method == 'POST':

        # populate the model with form data from the request
        form = RondeForm(request.POST)

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
                            message = "De volgende vraag zit al in het toernooi: " + vraag
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
                            rondeNummer = Ronde.objects.get(toernooicode=tournament_code, rondenummer=roundCount)
                            vraag = Vraag.objects.get(pk=vraag)
                            v = Ronde_Vraag.objects.create(toernooicode=tournament, rondenummer=rondeNummer, vraagID=vraag)
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
            form = RondeForm()
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


def restartTournament(request, tournament_code):
    tournament = get_object_or_404(Toernooi, pk=tournament_code)
    tournament.current_round = 1

    tournament.save()

    # this needs to be expanded later on

    return HttpResponseRedirect('/admin/controlpanel/' + tournament_code)


def controlPanel(request, tournament_code):
    # get relevant data from database
    tournament = get_object_or_404(Toernooi, pk=tournament_code)
    rounds = Ronde.objects.filter(toernooicode=tournament_code)
    questions = []

    # get questions per round
    for round in rounds:
        questions.append(Vraag.objects.filter(ronde_vraag__toernooicode=tournament_code).filter(ronde_vraag__rondenummer=round))

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


def setTimer(request, tournament_code, minutes):
    timer = get_object_or_404(Timer, pk=tournament_code)
    clock = Clock(tournament_code)

    clock.set(minutes)

    return HttpResponseRedirect('/admin/controlpanel/' + tournament_code)

def resetTimer(request, tournament_code):
    timer = get_object_or_404(Timer, pk=tournament_code)
    clock = Clock(tournament_code)

    clock.reset()

    return HttpResponseRedirect('/admin/controlpanel/' + tournament_code)

def startTimer(request, tournament_code):
    timer = get_object_or_404(Timer, pk=tournament_code)
    clock = Clock(tournament_code)

    clock.start()

    return HttpResponseRedirect('/admin/controlpanel/' + tournament_code)

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


def manageQuestion(request, tournament_code, rondenummer, vraagID):
    #question = Vraag.objects.filter(ronde_vraag__rondenummer=rondenummer).filter(vraagID=vraagID).filter(ronde_vraag__toernooicode=tournament_code)
    question = get_object_or_404(Vraag, pk=vraagID)
    tournament = get_object_or_404(Toernooi, pk=tournament_code)
    ronde = Ronde.objects.filter(toernooicode=tournament_code).filter(rondenummer=rondenummer).get()
    disabled = Ronde_Vraag.objects.filter(toernooicode=tournament_code).filter(rondenummer=ronde, vraagID=vraagID).get().disabled
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


def disableQuestion(request, tournament_code, rondenummer, vraagID):
    ronde = Ronde.objects.filter(toernooicode=tournament_code).filter(rondenummer=rondenummer).get()
    ronde_vraag = Ronde_Vraag.objects.filter(toernooicode=tournament_code).filter(rondenummer=ronde, vraagID=vraagID).get()
    vraag = get_object_or_404(Vraag, pk=vraagID)

    if ronde_vraag.disabled == 0:
        ronde_vraag.disabled = 1
        sendNotification(tournament_code, vraag.title + " is door het beheer uitgeschakeld.<br>Deze vraag is nu niet meer te bekijken of te beantwoorden.")
    else:
        ronde_vraag.disabled = 0
        sendNotification(tournament_code, vraag.title + " is door het beheer ingeschakeld.<br>Deze vraag is nu weer te bekijken en te beantwoorden.")

    ronde_vraag.save()

    return HttpResponseRedirect('/admin/controlpanel/' + tournament_code + '/' + str(rondenummer) + '/' + str(vraagID))

def sendNotification(tournament_code, content):
    tournament = get_object_or_404(Toernooi, pk=tournament_code)
    notif = Notification.objects.create(toernooicode=tournament, content=content)
    notif.save()


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
