
from django.urls import path, include, re_path

from . import views

urlpatterns = [
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path('', views.allPost, name="allposts"),
    path('u/<username>', views.profile, name="profile"),
    path('following/', views.following, name="following"),
    path('like/', views.like),
    path('follow/', views.follow),
    path('edit_post/', views.edit_post),
    path('addpost/', views.addpost),

    path('home/', views.home, name='home'),

    #profile_detail /@username/
    path('@<str:username>/', views.profile_detail, name='profile_detail'),

    #add new album /@username/add
    path('@<str:username>/add/', views.add_album, name='add_album'),

    #album's detail page /@username/album/album_name
    path('@<str:username>/album/<str:album>/', views.album_detail, name='album_detail'),

    #delete album /@username/album/album_name/delete
    path('@<str:username>/album/<str:album>/delete/', views.delete_album, name='delete_album'),

    #add songs to the albums
    path('@<str:username>/album/<str:album>/add/', views.add_song, name='add_song'),
]
