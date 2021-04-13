from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

app_name="dashboard"

urlpatterns = [
    #path('', views.index, name='index'),
    #path('', views.vragenlijst, name="vragenlijst"),
    #path('vraag/', views.vraag, name='vraag'),
    path('<str:id>/', views.dashboard, name='dashboard'),
    #path('', views.vragenlijst, name="vragenlijst"),
    path('vraag/<int:vraagid>/<int:counter>', views.vraag, name='vraag'),
    path('timer/<str:tournament_code>', views.ajaxGetTimer, name='ajaxGetTimer'),
    path('<str:tournament_code>/getNotifs', views.ajaxGetNotifications, name='ajaxGetNotifs'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout')
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

