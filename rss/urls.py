from django.urls import path, include
from . import views
app_name = 'rss'
urlpatterns = [

    path('rss/', views.index, name="index"),
    path('info/', views.Score, name="info"),
    path('about/', views.about, name="about"),
    path('scorecard/', views.scorecard, name="scorecard"),
    path('schedule/', views.schedule, name="schedule"),
    path('match_details/', views.match_details, name="match_details"),
    path('batting_ranking/', views.batting_ranking, name="batting_ranking"),
    path('bowling_ranking/', views.bowling_ranking, name="bowling_ranking"),
    path('all_rounder_ranking/', views.all_rounder_ranking, name="all_rounder_ranking"),
    path('team_ranking/', views.team_ranking, name="team_ranking"),


]
