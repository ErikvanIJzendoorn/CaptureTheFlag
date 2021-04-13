from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name="dashboard"

urlpatterns = [
    #path('', views.index, name='index'),
    #path('', views.vragenlijst, name="vragenlijst"),
    #path('vraag/', views.vraag, name='vraag'),
    path('<str:id>/', views.dashboard, name='dashboard'),
    #path('', views.vragenlijst, name="vragenlijst"),
    path('vraag/<int:vraagid>/', views.vraag, name='vraag'),
    path('<str:tournament_code>/timer', views.ajaxGetTimer, name='ajaxGetTimer'),
    path('<str:tournament_code>/getNotifs', views.ajaxGetNotifications, name='ajaxGetNotifs'),

] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

