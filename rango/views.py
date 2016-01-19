from django.shortcuts import render

#import the Category model
from rango.models import Category
#import the Page model
from rango.models import Page

from rango.forms import CategoryForm, PageForm
from rango.forms import UserForm, UserProfileForm

from django.http import HttpResponse, HttpResponseRedirect

from django.contrib.auth import authenticate, login


def index(request):
    # old:
    # construct a dictionary to pass to the template engine as its context
    # Note the key 'boldmessage' is the same as {{boldmessage}} in the template
    #context_dict = {'boldmessage': "I am bold font from the context"}

    #new:
    # Query the database for a list of ALL categories currently stored.
    # Order the categories by no. likes in descending order.
    # Retrieve the top 5 only - or all if less than 5.
    # Place the list in our context_dict dictionary which will be passed to the template engine.
    category_list = Category.objects.order_by('-likes')[:5] # '-likes' is likes in descending order
    context_dict = {'categories': category_list}

    # Aslo show top 5 most viewed companies
    top_categories_list = Category.objects.order_by('-views')[:5]
    context_dict['top_categories'] = top_categories_list

    # Return a rendered response to send to the client
    # We make use of the shortcut function to make our lives easier
    # Note that the first parameter is the template we wish to use
    return render(request, 'rango/index.html', context_dict)


def about(request):
    # return HttpResponse("Rango says here is the About page! </br> <a href='/rango'>Index</a>") 
    return render(request, 'rango/about.html')

def category(request, category_name_slug):
# What is category_name_slug? Check urls.py. I believe that whatever we pass
# in url after "/category/" is assigned to category_name_slug. That way, we 
# use that part of the link to see if that category exists.

    #create a dictionary that we can pass to the template rendering engine
    context_dict = {}

    try:
        # Can we find a category name slug with a given name
        # If we can't, the .get() method raises DoesNotExist exception
        # So the .get() method returns one model instance or returns exception
        category = Category.objects.get(slug=category_name_slug)
        context_dict['category_name'] = category.name

        # Retrieve all of the associated pages
        # Note that filter returns >=1 model instance.
        pages = Page.objects.filter(category = category)

        # Adds our results list to the template context under name pages
        context_dict['pages'] = pages
        # We also add the category object from the database to the context dictionary
        # We'll use this in the template to verify that the category exists
        context_dict['category'] = category

        #Add slug to dict- we need it when adding new pages
        context_dict['category_name_slug'] = category.slug

    except Category.DoesNotExist:
        # We get here if we didnt find the specified category
        # Don't do anything - the template displays the 'no category' message for us
        pass

    # Go render the response and return it to client
    return render(request, 'rango/category.html', context_dict)


def add_category(request):
    # A HTTP POST
    if request.method == 'POST':
        form = CategoryForm(request.POST)

        # Have we been provided with valid form
        if form.is_valid():
            # Save the new category to the database
            form.save(commit=True)

            # Now call the index view
            # The user will be shown the home page
            return index(request)
        else:
            # The supplied form contains errors - print them out to terminal
            print form.errors   

    else:
        # If the request was not a POST, display the form to enter details
        form = CategoryForm()

    # Bad form or form details, no form supplied...
    # Render the form with error messages (if any)
    return render(request, "rango/add_category.html", {'form': form})

def add_page(request, category_name_slug):
# check under category view to understand category_name_slug

    try:
        cat = Category.objects.get(slug=category_name_slug)
    except Category.DoesNotExist:
        cat = None

    if request.method == 'POST':
        form = PageForm(request.POST)
        if form.is_valid():
            if cat:
                page = form.save(commit=False)
                page.category = cat
                page.views = 0
                page.save()
                #probably better to use redirect here
                return category(request, category_name_slug)
        else:
            print form.errors
    else:
        form = PageForm()

    context_dict = {'form': form, 'category': cat, 'category_name_slug': category_name_slug}

    return render(request, "rango/add_page.html", context_dict)


# A view for user registration
def register(request):

    # A boolean value for telling the template whether the registration was successful.
    # Set to False initially. Code changes value to True when registration succeeds.
    registered = False

    # If it is a POST method, we're interested in processing
    if request.method == 'POST':
        # Attempt to grab information from the forms
        # We make use of both UserForm and UserProfileForm
        user_form = UserForm(data = request.POST)
        profile_form = UserProfileForm(data = request.POST)

        # if the 2 forms are valid
        if user_form.is_valid() and profile_form.is_valid():
            # save the user's form data to the database
            user = user_form.save()

            # now we hash the password with with the set_password method
            # once hashed, we can update the user object
            user.set_password(user.password)
            user.save()

            # now sort out the UserProfile instance
            # we need to set the user attribute ourselves, so commit=False
            # delays saving until we're ready to avoid integrity problems
            profile = profile_form.save(commit=False)
            profile.user = user

            # did user provide a profile picture. if so...
            if 'picture' in request.FILES:
                profile.picture = request.FILES['picture']

            # now we save the UserProfile model instance
            profile.save()

            # update variable to tell the template that the registration was successful
            registered = True

            # Invalid form or forms - mistakes or something else?
            # Print problems to the terminal.
            # They'll also be shown to the user.
        else:
            print user_form.errors, profile_form.errors

    # not a POST, so we render a form using 2 ModelForm instances
    # forms will be blank, ready for user input
    else:
        user_form = UserForm()
        profile_form = UserProfileForm()

    # render the template depending on the context
    return render(request,
        'rango/register.html', 
        {'user_form': user_form, 'profile_form': profile_form, 'registered': registered})


# User login view
def user_login(request):

    # POST or GET
    if request.method == 'POST':
    # Gather username and pasword from the form
    # We use request.POST.get('<variable>') as opposed to request.POST['<variable>'],
    # because the request.POST.get('<variable>') returns None, if the value does not exist,
    # while the request.POST['<variable>'] will raise key error exception
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Use Django machinery to check if user/pass combination is correct
        # return User object if it is
        user = authenticate(username=username, password=password)

        # If we have a User object, the details are correct.
        # If None (Python's way of representing the absence of a value), no user
        # with matching credentials was found.
        if user:
            # Is the account active- it could've been disabled
            if user.is_active:
                # If the account is valid and active, we can log the user in.
                # We'll send the user back to the homepage.
                login(request, user)
                return HttpResponseRedirect('/rango/')
            else:
                # An inactive account was used - no logging in!
                return HttpResponse("Your account is disabled")
        else:
            # Bad details were provided, we can't log user in
            print "Invalid login details: %s, %s" % (username, password)
            return HttpResponse("Invalid login details supplied")
    
    # not POST, most likely GET
    else:
        # No context variables to pass to the template system, hence the
        # blank dictionary object...
        return render(request, 'rango/login.html', {})
