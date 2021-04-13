from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.template import loader
from django.shortcuts import render
from Capture_the_Flag.Admin.models import Team, Team_Toernooi, Vraag, Teamlid
from django.db import models
from django.contrib.auth import authenticate, login as auth_login
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404
from .forms import *

def index_main(request):
    message = ''
    template = loader.get_template('Main/index.html')
    user_form = LoginForm(request.POST)
    form = TeamLoginForm(request.POST)
    # Als team inlogt
    if request.method == 'POST' and 'submitteam' in request.POST:
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
    # Als gebruiker inlogt
    elif request.method == 'POST' and 'submituser' in request.POST:
        if(request.user.is_authenticated):
            return HttpResponseRedirect('/admin/')

        else:
            if request.method == 'POST':
                user_form = LoginForm(request.POST)
                username = request.POST['username']
                password = request.POST['password']
                user = authenticate(request, username=username, password=password)
                if user is not None:
                    auth_login(request, user)
                    return HttpResponseRedirect('/admin/')

            else:
                user_form = LoginForm()

            return render(request, 'Admin/login.html', {'user_form': user_form})
    else:
        form = TeamLoginForm()
    return HttpResponse(template.render({'form': form, 'message': message, 'user_form': user_form}, request))
