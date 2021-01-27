from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
# module that django provides to create users for the site
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.contrib.auth import login, logout, authenticate
# import the form created for the todos
from .forms import TodoForm
# import the Todo model to be used
from .models import Todo
# import time zone
from django.utils import timezone
# only loged users can access some pages
from django.contrib.auth.decorators import login_required

# Create your views here.
def signupuser(request):
    # check if it is a post or get, since we are dealing with a form.
    if request.method == 'GET':
        return render (request, 'todo/signupuser.html', {'form': UserCreationForm()} )
    else:
    # django provides that function to create the object with a dictionary, inside the html you can find the key for each field, 
    # basically the key for the fields are the attribute name, example:  name='username'. In order to access the attribute you
    # can use the request.POST['namefield'].
    # first - let's check if the user typed the same password before procedding to save the data.
        if request.POST['password1'] == request.POST['password2']:
        # proceed to save the data on the database with the django function, that the auth.contrib provides.
            try:
                #create the variable to hold the user
                user = User.objects.create_user(request.POST['username'], password=request.POST['password1'])
                #save the user on the database
                user.save()
                #log the user - passing the request and the name of the object with the user info.
                login(request, user)
                return redirect('currenttodos')

            except IntegrityError:
                return render (request, 'todo/signupuser.html', {'form': UserCreationForm(), 'error':'That user has been taken' })
        else:
        # In case the password does not match, I can return the user to the same page, and send some information in a dic for the form.
        # Then I can go o my signupser.html and include that variable there, to display the message.
            return render (request, 'todo/signupuser.html', {'form': UserCreationForm(), 'error':'The password does not match' })

@login_required
def logoutuser(request):
    if request.method == 'POST':
        logout(request)
        return redirect('home')

def loginuser(request):
    if request.method == 'GET':
        return render(request,'todo/loginuser.html',{'form': AuthenticationForm()} )
    else:
        user = authenticate(request, username=request.POST['username'], password=request.POST['password'])
        if user is None:
            return render(request,'todo/loginuser.html',{'form': AuthenticationForm(), 'error': 'something did not match' } )
        else:
            login(request, user)
            return redirect('currenttodos')



# site stuff and todos ... 

def home(request):
    return render(request, 'todo/home.html')

@login_required
def currenttodos(request):
    # Import the Model of Todos and then get all the data from the database and then pass as dictionaries...
    # You can check if it is completed with __isnull, okay for this project...
    todos = Todo.objects.filter(user=request.user, datecompleted__isnull=True)

    return render (request, 'todo/currenttodos.html', {'todos':todos})

# this time get the todo_pk as well passed inside the URL.
@login_required
def viewtodo(request, todo_pk):
    # get the todo related to that primary key - and make sure it belongs to that user
    todo = get_object_or_404(Todo, pk=todo_pk, user=request.user)
    if request.method == 'GET':
        # create the form in case you want to edit
        form = TodoForm(instance=todo)
        return render (request, 'todo/viewtodo.html', {'todo':todo, 'form':form})
    else:
        try:
            # take the form and save it to the database
            form = TodoForm(request.POST , instance=todo)
            form.save()
            # then redirect to the current todo
            return redirect('currenttodos')
        except ValueError:
            return render (request, 'todo/viewtodo.html', {'todo':todo, 'form':form, 'error':'bad information'})

@login_required
def createtodo(request):
    if request.method == 'GET':
        return render(request, 'todo/createtodo.html',{'form':TodoForm()})
    else:
        try:
            # get the information coming from the form
            form = TodoForm(request.POST)
            # create the new todo for the user, but don't add to the database yet...
            newtodo = form.save(commit=False)
            # create a variable obj to especify the todo, to the same user request
            newtodo.user = request.user
            # save the todo to that user
            newtodo.save() 
            # redirect the user to a page
            return redirect('currenttodos')
        except ValueError:
            return render(request, 'todo/createtodo.html',{'form':TodoForm(),'error':'Bad error passed in...Please try again.'})

@login_required
def completetodo(request, todo_pk):
    # get the object, only the person that owns that obj
    todo = get_object_or_404(Todo, pk=todo_pk, user=request.user)
    # check if it is a post and completed... checking on the database.
    if request.method == 'POST':
        todo.datecompleted = timezone.now()
        todo.save()
        return redirect('currenttodos')

@login_required
def deletetodo(request, todo_pk):
    # get the object, only the person that owns that obj
    todo = get_object_or_404(Todo, pk=todo_pk, user=request.user)
    # check if it is a post and completed... checking on the database.
    if request.method == 'POST':
        todo.datecompleted = timezone.now()
        todo.delete()
        return redirect('currenttodos')

@login_required
def completedtodos(request):
    # Import the Model of Todos and then get all the data from the database and then pass as dictionaries...
    # You can check if it is completed with __isnull, okay for this project...
    todos = Todo.objects.filter(user=request.user, datecompleted__isnull=False).order_by('-datecompleted')

    return render (request, 'todo/completedtodos.html', {'todos':todos})
