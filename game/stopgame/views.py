# Create your views here.
from django import forms
from django.contrib import auth
from django.http import HttpResponse
from django.shortcuts import render, redirect
from models import GameRoom, Field, Letter, Selection, GameRound, Answer, Player

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
    if not cur_round_query:
        cur_round = GameRound(cur_letter=all_letters[0], room=cur_room, round_number=1)
        cur_round.save()
        rnd = cur_round
    else:
        rnd = cur_round_query.latest('round_number')

    user = request.user
    player_query = Player.objects.filter(user__id=user.id)
    player = player_query[0]
    player_answers = []
    for rd in cur_round_query:
        query = Answer.objects.filter(roundd__id=rd.id).filter(player__id=player.id)
        if query:
            player_answers.append(query[0])

    return render(request, 'play.html', 
        {'room': cur_room,
        'fields': fields,
        'letters': all_letters,
        'round': rnd,
        'player_answers':player_answers,
        })

def send_answers(request, room_id):
    cur_round_query = GameRound.objects.filter(room__id=room_id)
    rnd = cur_round_query.latest('round_number')

    player_query = Player.objects.filter(user__id=request.user.id)
    player = player_query[0]
    for key, value in request.POST.iteritems():
        if not key == 'csrfmiddlewaretoken':
            valid = value[0].lower() == rnd.cur_letter.lower()
            ans = Answer(roundd=rnd, player=player, ans=value, valid=valid, points= 2 if valid else 0)
            ans.save()
    return HttpResponse('answers sent')

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

def login_view(request):
    username = request.POST.get('username', '')
    password = request.POST.get('password', '')
    user = auth.authenticate(username=username, password=password)
    if user is not None and user.is_active:
        # Correct password, and the user is marked "active"
        auth.login(request, user)
        # Redirect to a success page.
        return HttpResponse("Login deu certo")
    else:
        # Show an error page
        return HttpResponse("Login deu errado")
