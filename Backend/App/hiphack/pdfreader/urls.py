from django.urls import path

from . import views



urlpatterns = [
    path('', views.index, name='index'),
    # path('your-name/', views.index, name='index'),
    path('pdfreader/results.html',views.add_items,name = 'add_items'),
    
    path('pdfreader/search.html',views.add_items,name = 'add_items'),

    path('pdfreader/error.html',views.add_items,name = 'add_items'),


]
