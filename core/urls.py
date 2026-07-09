from django.urls import path

from core.views import *

app_name = 'core'

urlpatterns = [
    path('',index,name='index'),

path('about/',about,name='about'),
    path('login/',login_user,name='login'),
    path('logout',logout_user,name='logout'),
    path('register/',register_user,name='register'),
    path('product/<str:name>',product,name='product'),
    path('category/<str:name>',category,name='category'),
    path('category_summary/', category_summary, name='category_summary'),
    path('update_user/', update_user, name='update_user'),
    path('update_password/', update_password, name='update_password'),
    path('update_info/', update_info, name='update_info'),
    path('search/', search, name='search'),

]