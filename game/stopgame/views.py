# Create your views here.
from django import forms
from django.shortcuts import render
from models import GameRoom

def home(request):
	return render(request, 'home.html')

def game_configuration(request):
	class GameForm(forms.ModelForm):
		class Meta:
			model = GameRoom
			exclude = ['players', 'round_number']
	form = GameForm()
	form.fields['fields'].widget = forms.CheckboxSelectMultiple()
	return render(request,'game_configuration.html', {'form':form})

def game_play(request):
	return render(request, 'play.html')

def results(request):
	return render(request, 'results.html')