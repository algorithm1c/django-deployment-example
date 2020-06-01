from django.shortcuts import render
from basic_app.forms import UserForm, UserProfileInfoForm

#
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required


# Create your views here.
def index(request):
    return render(request, 'basic_app/index.html')

@login_required
def special(request):
    # Remember to also set login url in settings.py!
    # LOGIN_URL = '/basic_app/user_login/'
    return HttpResponse("You are logged in. Nice!")

@login_required #this will require login to be required before the below logout method will run
def user_logout(request):
    # Log out the user.
    logout(request)
    # Return to homepage.
    return HttpResponseRedirect(reverse('index'))

def register(request):

    registered = False

    if request.method == "POST":    #notice the '=='
        user_form = UserForm(data=request.POST) #this matches the variable sent back from the context dictionary
        profile_form = UserProfileInfoForm(data=request.POST)
        #these two lines grab the info from the forms

        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            user.set_password(user.password) #this hashes the pwd
            user.save() #this saves the hashed pwd to the DB
            #these lines grab everything from the base user form

            profile = profile_form.save(commit=False)
            profile.user = user #this relates this extra info to the one to one relationship with the user above
            #these lines grab everything from the extra info form

            if 'profile_pic' in request.FILES:
                profile.profile_pic = request.FILES['profile_pic']
            profile.save()
            #if there's a pic uploaded, we save the pic to this user's profile

            registered=True
            #and we then set registered = true for this user

        else:
            print(user_form.errors, profile_form.errors)

    else: #meaning, no POST request, these below two lines set the forms
        user_form = UserForm()
        profile_form = UserProfileInfoForm()
        #user_form is an instance of UserForm()

    return render(request, 'basic_app/registration.html',
                {'user_form':user_form,
                'profile_form':profile_form,
                'registered':registered})


def user_login(request):

    if request.method == 'POST':
        # First get the username and password supplied
        username = request.POST.get('username') #this grabs the username supplied by the user from login.html
        password = request.POST.get('password') #this grabs the pwd supplied by the user from login.html

        # Django's built-in authentication function:
        user = authenticate(username=username, password=password)

        # If we have a user
        if user:
            #Check if the account is active
            if user.is_active:
                # Log the user in.
                login(request,user)
                # Send the user back to some page.
                # In this case their homepage.
                return HttpResponseRedirect(reverse('index'))
            else:
                # If account is not active:
                return HttpResponse("Your account is not active.")
        else:
            print("Someone tried to login and failed.")
            print("They used username: {} and password: {}".format(username,password))
            return HttpResponse("Invalid login details supplied.")

    else:
        #Nothing has been provided for username or password.
        return render(request, 'basic_app/login.html', {})
        # we can pass in the empty context dict if you want
