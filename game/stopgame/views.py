# Create your views here.
from django import forms
from django.shortcuts import render, redirect
from models import GameRoom, Field, Letter, Selection, GameRound, Answers

def home(request):
	return render(request, 'home.html')

def game_configuration(request):
	class GameForm(forms.ModelForm):
		class Meta:
			model = GameRoom
			exclude = ['players', 'round_number', 'hash_code', 'is_protected']

		def clean_password(self):
			print "Arrumando password"
			if self.cleaned_data['password']:
				self.cleaned_data['is_protected'] = True
			else:
				self.cleaned_data['is_protected'] = False
			return self.cleaned_data['password']

	if request.method == 'POST':
		form = GameForm(request.POST)
		if form.is_valid():
			room = form.save(commit=False)
			room.round_number = 0
			room.save()
			for let in form.cleaned_data.get('selected_letters'):
				Selection.objects.create(letter=let, game=room, already_selected=False)
			for f in form.cleaned_data.get('fields'):
				room.fields.add(f)
	else:
		form = GameForm()
	form.fields['fields'].widget = forms.CheckboxSelectMultiple()
	form.fields['fields'].queryset = Field.objects.all()
	form.fields['selected_letters'].widget = forms.CheckboxSelectMultiple()
	form.fields['selected_letters'].queryset = Letter.objects.all()
	return render(request,'game_configuration.html', {'form':form})

def game_play(request, room_id):
	cur_room = GameRoom.objects.get(id=room_id)
	fields = cur_room.fields.all()
	all_letters = cur_room.selected_letters.all()
	cur_round_query = GameRound.objects.filter(room__id=room_id)
	player_answers = []
	# for rnd in cur_round_query:
	# 	player_answers.append(Answers.objects.filter(roundd__id=rnd.id).filter(player__id=player.id)[0])
	
	return render(request, 'play.html', 
		{'room': cur_room, 'fields': fields, 'letters': all_letters, 'round': cur_round_query.latest('round_number')})

def results(request):
	return render(request, 'results.html')

def enter_room(request, room_id):
	room = GameRoom.objects.get(id=room_id)
	if room.is_protected:
		if request.method == 'POST':
			pass
		else:
			pass
		return render(request, 'enter_room.html')
	return redirect('stopgame.views.game_play', room_id=room_id)

def rooms(request):
	rooms = GameRoom.objects.all()
	return render(request, 'rooms.html', {'rooms': rooms})