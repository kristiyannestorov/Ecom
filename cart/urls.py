from django.urls import path,include


from . import views
path('', include('core.urls', namespace='core')),

urlpatterns = [
    path('',views.cart_summary,name='cart_summary'),
   path('add/',views.cart_add, name='cart_add'),
   path('delete/', views.cart_delete, name='cart_delete'),
  path('update/', views.cart_update, name='cart_update'),

]