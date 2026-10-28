from django.urls import path
from . import views

urlpatterns=[
    path('',views.dashboard_view,name='dashboard'),
    path('signup/',views.signup_view,name='signup'),
    path('login/',views.login_view,name='login'),
    path('logout/',views.logout_view,name='logout'),
    path('decision/new/',views.new_decision,name='new_decision'),
    path('decision/<int:pk>/', views.decision_detail, name='decision_detail'),
    path('whatif/',views.whatif_view,name='whatif'),
    path('decisions/', views.decision_list,name='decision_list'),
    path('decision/<int:pk>/status/', views.update_status, name='update_status'),
    path('profile/', views.profile_view, name='profile'),
    path('assistant/', views.assistant_view, name='assistant'),
]