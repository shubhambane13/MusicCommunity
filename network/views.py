from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.utils import timezone
from django.core.paginator import Paginator
from .models import User, Post, Profile
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django import forms

from .models import Album, Song
from .forms import NewAlbum, NewSong



def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("allposts"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


@login_required
def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("login"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        profile = Profile()
        profile.user = user
        profile.save()
        return HttpResponseRedirect(reverse("allposts"))
    else:
        return render(request, "network/register.html")


@login_required
def allPost(request):
    posts = Post.objects.all().order_by('-timestamp')
    paginator = Paginator(posts, 10)
    if request.GET.get("page") != None:
        try:
            posts = paginator.page(request.GET.get("page"))
        except:
            posts = paginator.page(1)
    else:
        posts = paginator.page(1)
    return render(request, 'network/allpost.html', {'posts': posts})


@login_required
def profile(request, username):
    try:
        user = User.objects.get(username=username)
        profile = Profile.objects.get(user=user)
        users_profile = Profile.objects.get(user=request.user)
    except:
        return render(request, 'network/profile.html', {"error": True})
    posts = Post.objects.filter(user=user).order_by('-timestamp')
    paginator = Paginator(posts, 10)
    if request.GET.get("page") != None:
        try:
            posts = paginator.page(request.GET.get("page"))
        except:
            posts = paginator.page(1)
    else:
        posts = paginator.page(1)
    for i in users_profile.follower.all():
        print(i)
    context = {
        'posts': posts,
        "user": user,
        "profile": profile,
        'users_profile': users_profile
    }
    return render(request, 'network/profile.html', context)


@login_required
def following(request):
    following = Profile.objects.get(user=request.user).following.all()
    posts = Post.objects.filter(user__in=following).order_by('-timestamp')
    paginator = Paginator(posts, 10)
    if request.GET.get("page") != None:
        try:
            posts = paginator.page(request.GET.get("page"))
        except:
            posts = paginator.page(1)
    else:
        posts = paginator.page(1)
    return render(request, 'network/following.html', {'posts': posts})


@login_required
@csrf_exempt
def like(request):
    if request.method == "POST":
        post_id = request.POST.get('id')
        is_liked = request.POST.get('is_liked')
        try:
            post = Post.objects.get(id=post_id)
            if is_liked == 'no':
                post.like.add(request.user)
                is_liked = 'yes'
            elif is_liked == 'yes':
                post.like.remove(request.user)
                is_liked = 'no'
            post.save()

            return JsonResponse({'like_count': post.like.count(), 'is_liked': is_liked, "status": 201})
        except:
            return JsonResponse({'error': "Post not found", "status": 404})
    return JsonResponse({}, status=400)


@login_required
@csrf_exempt
def follow(request):
    if request.method == "POST":
        user = request.POST.get('user')
        action = request.POST.get('action')

        if action == 'Follow':
            try:
                # add user to current user's following list
                user = User.objects.get(username=user)
                profile = Profile.objects.get(user=request.user)
                profile.following.add(user)
                profile.save()

                # add current user to  user's follower list
                profile = Profile.objects.get(user=user)
                profile.follower.add(request.user)
                profile.save()
                return JsonResponse({'status': 201, 'action': "Unfollow", "follower_count": profile.follower.count()}, status=201)
            except:
                return JsonResponse({}, status=404)
        else:
            try:
                # add user to current user's following list
                user = User.objects.get(username=user)
                profile = Profile.objects.get(user=request.user)
                profile.following.remove(user)
                profile.save()

                # add current user to  user's follower list
                profile = Profile.objects.get(user=user)
                profile.follower.remove(request.user)
                profile.save()
                return JsonResponse({'status': 201, 'action': "Follow", "follower_count": profile.follower.count()}, status=201)
            except:
                return JsonResponse({}, status=404)

    return JsonResponse({}, status=400)


@login_required
@csrf_exempt
def edit_post(request):
    if request.method == "POST":
        post_id = request.POST.get('id')
        new_post = request.POST.get('post')
        try:
            post = Post.objects.get(id=post_id)
            if post.user == request.user:
                post.post = new_post.strip()
                post.save()
                return JsonResponse({}, status=201)
        except:
            return JsonResponse({}, status=404)

    return JsonResponse({}, status=400)


@login_required
@csrf_exempt
def addpost(request):
    if request.method == "POST":
        post = request.POST.get('post')
        if len(post) != 0:
            obj = Post()
            obj.post = post
            obj.user = request.user
            obj.save()
            context = {
                'status': 201,
                'post_id': obj.id,
                'username': request.user.username,
                'timestamp': obj.timestamp.strftime("%B %d, %Y, %I:%M %p"),
            }
            return JsonResponse(context, status=201)
    return JsonResponse({}, status=400)

#==================================================================#


#def music(request):
#	return render(request, 'network/music.html')

def home(request):
    #show all albums in chronological order of it's upload
    albums = Album.objects.all()
    return render(request, 'music/home.html',{'albums':albums})

#........................................................#

def profile_detail(request, username):
    # show all albums of the artist
    albums = get_object_or_404(User, username=username)
    albums = albums.albums.all()
    return render(request, 'music/artist_detail.html', {'albums':albums, 'username':username})

#........................................................#

@login_required
def add_album(request, username):
    user = get_object_or_404(User, username=username)
    #only currently logged in user can add album else will be redirected to home
    if user == request.user:
        if request.method == 'POST':
            form = NewAlbum(request.POST, request.FILES)
            if form.is_valid():
                # form.save(commit='False')
                album = Album.objects.create(
                    album_logo=form.cleaned_data.get('album_logo'),
                    album_name=form.cleaned_data.get('album_name'),
                    album_genre=form.cleaned_data.get('album_genre'),
                    uploaded_on = timezone.now(),
                    album_artist = request.user
                )
                return redirect('profile_detail', username=request.user)
        else:
            form = NewAlbum()
        return render(request, 'music/add_new_album.html', {'form':form})
    else:
        return redirect('profile_detail', username=user)

#........................................................#

def album_detail(request,username, album):
    #show album details here. single album's details.
    album = get_object_or_404(Album, album_name=album)
    songs = get_object_or_404(User, username=username)
    songs = songs.albums.get(album_name=str(album))
    songs = songs.songs.all()
    return render(request, 'music/album_detail.html', {'songs':songs, 'album':album, 'username':username
    })


@login_required
def delete_album(request, username, album):
    user = get_object_or_404(User, username=username)
    if request.user == user:
        album_to_delete = get_object_or_404(User, username=username)
        album_to_delete = album_to_delete.albums.get(album_name=album)
        song_to_delete = album_to_delete.songs.all()
        for song in song_to_delete:
            song.delete_media()#deletes the song_file
        album_to_delete.delete_media()#deletes the album_logo
        album_to_delete.delete()#deletes the album from database
        return redirect('profile_detail', username=username)
    else:
        return redirect('profile_detail', username=username)


@login_required
def add_song(request, username, album):

    user = get_object_or_404(User, username=username)

    if request.user == user:

        album_get = Album.objects.get(album_name=album)

        if request.method == 'POST':
            form = NewSong(request.POST, request.FILES)
            if form.is_valid():
                # form.save(commit='False')
                song = Song.objects.create(
                    song_name = form.cleaned_data.get('song_name'),
                    song_file = form.cleaned_data.get('song_file'),
                    song_album = album_get
                )
                return redirect('album_detail', username=username, album=album)

        else:
            form = NewSong()
            return render(request, 'music/add_new_song.html', {'form':form})
    else:
        return redirect('album_detail', username=username, album=album)










