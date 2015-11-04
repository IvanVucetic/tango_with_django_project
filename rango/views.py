from django.shortcuts import render

#import the Category model
from rango.models import Category

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

	# Return a rendered response to send to the client
	# We make use of the shortcut function to make our lives easier
	# Note that the first parameter is the template we wish to use
	return render(request, 'rango/index.html', context_dict)


def about(request):
	# return HttpResponse("Rango says here is the About page! </br> <a href='/rango'>Index</a>") 
	return render(request, 'rango/about.html')