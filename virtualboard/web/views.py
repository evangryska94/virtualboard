from django.contrib.auth import authenticate, logout, login
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist


from django.core.urlresolvers import reverse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect, HttpResponse
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_exempt
from django.utils import timezone

from datetime import datetime
from django.db import connection

from forms import *
from web.models import *


def index(request):
    return render(request, 'web/base.tpl', {})


def signup(request):
    """
    Signup view, handles signup requests.
    """
    if request.method=='POST':
        # if user is already signed in
        if request.user.is_authenticated():
            errmsg = 'You are already signed in.'
            form = signupForm()
            return render(request, 'web/signup.tpl', 
                                {'form':form, 'error':errmsg})

        # handle a sign up request
        uname = request.POST['username'].lower().strip()
        pswd = request.POST['password']
        pswdagain = request.POST['password_again']
        
        err_list = []
        if not uname.isalnum():
            err_list.append('Username is not alphanumeric. ')
        if len(uname) < 3:
            err_list.append('Username is too short (must be at least 3 characters long). ')
        if len(pswd) < 6:
            err_list.append('Password is too short (must be at least 6 characters long). ')
        if pswd!=pswdagain:
            err_list.append('Passwords do not match. ')

        if err_list:
            errmsg = ''.join(err_list)
            form = signupForm()
            return render(request, 'web/signup.tpl', 
                    {'form':form, 'error':errmsg})
        else:
            try:
                newuser = User.objects.create_user(uname, password=pswd)
                newuser.save()
            except:
                errmsg = 'Username exists.'
                form = signupForm()
                return render(request, 'web/signup.tpl', 
                        {'form':form, 'error':errmsg})
               
            # add the profile 
            profile = Profile(user=newuser, motto = '', currentLobby = None)
            profile.save()

        # redirect welcome page
        return HttpResponseRedirect(reverse('web:index'))
    elif request.method=='GET':
        # get request
        form = signupForm()
        return render(request, 'web/signup.tpl', {'form' : form})
        

def signin(request):
    """
    Signin view, handles signin requests.
    """
    if request.method=='POST':
        uname = request.POST['username']
        passwd = request.POST['password']
        
        user = authenticate(username=uname, password=passwd)
        
        if user is not None and user.is_active:
            # auth successful Redirect to a success page.
            login(request, user)
            return HttpResponseRedirect(reverse('web:index'))
        else:
            # auth failure
            form = signinForm()
            context = {'form':form, 'authfail':True}
            return render(request, 'web/accountform.tpl', context)
    else:
        # get requests
        form = signinForm()
        return render(request, 'web/accountform.tpl', {'form' : form, 'next':next})


def signout(request):
    """
    Signout view, handles signout requests
    """
    logout(request)
    # redirect signout successful
    return HttpResponseRedirect(reverse('web:index'))


def listoflobbies(request):
    """
    List of Lobbies view
    """
    lobby_list = Lobby.objects.order_by('-num_members')
    context = {'lobby_list': lobby_list}
    return render(request, 'web/lobbylist.tpl', context)

def createlobby(request):
    """
    create lobby view, take an input of name for the lobby
    """
    if request.user.is_authenticated():
        if request.method == 'POST':
            form = lobbyCreationForm(request.POST)
            if form.is_valid():
                fetchedName = form.cleaned_data['lobbyName']
                
                try:
                    tempLobby = Lobby.objects.get(name=fetchedName)
                except ObjectDoesNotExist:
                    tempLobby = None

                if tempLobby != None:
                    return render(request, 'web/createlobby.tpl', {
                        'error_msg': 'lobby with selected name already exists'
                        })
                else:
                    new_lobby = Lobby(name = fetchedName, num_members = 1)
                    new_lobby.save()
                    curUserProfile = Profile.objects.get(user=request.user)
                    curUserProfile.currentLobby = new_lobby
                    curUserProfile.save()
                    return HttpResponseRedirect(reverse('web:lobby', args=(new_lobby.id,)))
        else:
            form = lobbyCreationForm()
            return render(request,'web/createlobby.tpl',{'form': form})
    else:
        return HttpResponseRedirect(reverse('web:index'))
    

def lobby(request,lobby_id):
    lobby_instance = get_object_or_404(Lobby, pk=lobby_id)
    context = {"lobby_instance":lobby_instance}
    return render(request, 'web/lobby.tpl', context)


def leavelobby(request,lobby_id):
    curUserProfile = Profile.objects.get(user=request.user)
    curUserProfile.currentLobby = None
    curLobby = Lobby.objects.get(pk=lobby_id)
    curLobby.num_members -= 1
    if curLobby.num_members <= 0:
        curLobby.delete()

    return HttpResponseRedirect(reverse('web:listoflobbies'))

def joinlobby(request,lobby_id):
    if request.user.is_authenticated():
        curLobby = Lobby.objects.get(pk=lobby_id)
        curLobby.num_members += 1
        Profile.objects.get(user = request.user).currentLobby =  curLobby
        return HttpResponseRedirect(reverse('web:lobby', args=(lobby_id,)))
    else:
        return HttpResponseRedirect(reverse('web:signin'))
