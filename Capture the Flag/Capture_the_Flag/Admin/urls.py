from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.viewTournamentList, name='tournaments'),
    path('controlpanel/<str:tournament_code>/', views.controlPanel, name='controlPanel'),
    path('create/vraag/', views.createVraag, name='createVraag'),
    path('create/tournament/', views.createTournament, name='createTournament'),
    path('create/ronde/<str:tournament_code>/', views.createRonde, name='createRonde'),
    path('modify/vraag/', views.viewVragen, name="viewVragen"),
    path('modify/vraag/<int:vraagID>/<int:rondenummer>', views.editVraag, name='editVraag'),
    path('modify/vraag/<int:vraagID>/', views.editVraag, name='editVraag'),
    path('tournament/<str:tournament_code>/modify/ronde/<int:rondeID>/', views.EditRound, name='EditRound'),
    path('tournament/<str:tournament_code>/', views.viewTournament, name='ViewTournament'),
    path('tournament/<str:tournament_code>/scheidsrechter/', views.scheidsrechterToevoegen, name='scheidsrechterToevoegen'),
    path('tournament/<str:tournament_code>/beheerder/', views.toernooibeheerderWijzigen, name='toernooibeheerderWijzigen'),
    path('tournament/<str:tournament_code>/team/delete/', views.teamVerwijderen, name='teamVerwijderen'),
    path('controlpanel/<str:tournament_code>/timer/set/<int:minutes>/', views.setTimer, name='setTimer'),
    path('controlpanel/<str:tournament_code>/timer/start/', views.startTimer, name='startTimer'),
    path('controlpanel/<str:tournament_code>/timer/reset/', views.resetTimer, name='resetTimer'),
    path('controlpanel/<str:tournament_code>/timer/pause/', views.pauseTimer, name='pauseTimer'),
    path('controlpanel/<str:tournament_code>/timer/', views.ajaxGetTimer, name='getTimer'),
    path('controlpanel/<str:tournament_code>/<int:rondenummer>/<int:vraagID>/', views.manageQuestion, name='manageQuestion'),
    path('controlpanel/<str:tournament_code>/<int:rondenummer>/<int:vraagID>/<str:team_code>/changeresult', views.changeResult, name='changeresult'),
    path('controlpanel/<str:tournament_code>/<int:rondenummer>/<int:vraagID>/disable', views.disableQuestion, name='disableQuestion'),
    path('dashboard/<str:tournament_code>/', views.dashboard, name='dashboard'),
    path('controlpanel/<str:tournament_code>/restart/', views.resetTournament, name='restartTournament'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),
    path('scoreboard/<str:tournament_code>', views.ajaxGetScoreboard, name="scoreboard")
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
