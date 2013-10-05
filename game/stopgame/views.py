# Create your views here.
from django.shortcuts import render

def home(request):
	return render(request, 'home.html')

def game_configuration(request):
	return render(request, 'game_configuration.html')

def game_play(request):
	return render(request, 'play.html')

def results(request):
	return render(request, 'results.html')