from django.shortcuts import render

#import the Category model
from rango.models import Category
#import the Page model
from rango.models import Page

from rango.forms import CategoryForm 
from rango.forms import PageForm

from django.http import HttpResponse

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
	category_list = Category.objects.order_by('-likes')[:5]	# '-likes' is likes in descending order
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