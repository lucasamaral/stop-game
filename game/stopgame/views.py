# Create your views here.
import json
import datetime
from pytz import timezone
from django import forms
from django.contrib import auth
from django.http import HttpResponse, Http404
from django.shortcuts import render, redirect
from models import GameRoom, Field, Letter, Selection, GameRound, Answer, Player, PlayerGameRoom
from django.contrib.auth.decorators import login_required

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

@login_required
def game_play(request, room_id):
    if not request.user.is_authenticated():
        return HttpResponse("Faca login")
    
    cur_room = GameRoom.objects.get(id=room_id)
    fields = cur_room.fields.all()
    all_letters = cur_room.selected_letters.all()
    cur_round_query = GameRound.objects.filter(room__id=room_id)
    if not cur_round_query:
        cur_round = GameRound(cur_letter=all_letters[0], room=cur_room, round_number=1)
        cur_round.save()
        rnd = cur_round
        cur_room.round_number = 1
        cur_round_query = GameRound.objects.filter(room__id=room_id)
    else:
        rnd = cur_round_query.latest('round_number')
        if cur_room.game_duration == rnd.round_number:
            rnd = None
        else:
            cur_room.round_number = rnd.round_number
    cur_room.save()

    player = request.user.player

    if len(PlayerGameRoom.objects.filter(room__id=cur_room.id).filter(player__id=player.id))== 0:
        player_room = PlayerGameRoom(room=cur_room, player=player, current_score=0)
        player_room.save()

    player_answers = {}
    for rd in cur_round_query:
        query = Answer.objects.filter(roundd__id=rd.id).filter(player__id=player.id)
        if query:
            for ans in query:
                if str(ans.field.short_name) not in player_answers.keys():
                    player_answers[str(ans.field.short_name)] = []
                player_answers[str(ans.field.short_name)].append(str(ans.ans))
                print 'field: ' + str(ans.field.short_name)
                print 'ans: ' + str(ans.ans)
    print player_answers
    return render(request, 'play.html', 
        {'room': cur_room,
        'fields': fields,
        'letters': all_letters,
        'round': rnd,
        'player_answers':player_answers,
        })


def receive_ans_ajax(request):
    if not request.user.is_authenticated():
        return HttpResponse("Faca login")


    if request.is_ajax() and request.method == 'POST':
        json_data = json.loads(request.readline())
        print json_data
        
        player = request.user.player
        
        room_query = GameRoom.objects.filter(players__id=player.id)
        room = room_query[0]

        round_query = GameRound.objects.filter(room__id=room.id)
        cur_round = round_query.latest('round_number')

        for key in json_data:
            value = json_data[key]
            field_query = Field.objects.filter(short_name=key)
            field = field_query[0]
            valid = value[0].lower() == cur_round.cur_letter.lower()

            ans = Answer(roundd=cur_round, player=player, field=field, ans=value, valid=valid,points= 10 if valid else 0 )
            ans.save()
        return HttpResponse("OK")
    else:
        if not request.is_ajax():
            return HttpResponse('Only ajax is allowed')
        elif not request.method == 'POST':
            return HttpResponse(request.method + ' is not allowed')
        else:
            return HttpResponse('unknown error')

def everyone_answers(request):
    if not request.user.is_authenticated():
        return HttpResponse("Faca login")

    player = request.user.player
        
    room_query = GameRoom.objects.filter(players__id=player.id)
    room = room_query[0]

    round_query = GameRound.objects.filter(room__id=room.id)
    cur_round = round_query.latest('round_number')

    all_players = room.players.all()
    ans_dic = {}
    for player in all_players:
        ans_dic[player.user.username] = {}
        ans_query = Answer.objects.filter(roundd__id=cur_round.id).filter(player__id=player.id)
        for answer in ans_query:
            ans_dic[player.user.username][answer.field.short_name] = answer.ans
    return HttpResponse(json.dumps(ans_dic), content_type="application/json")


@login_required
def results(request):
    player = request.user.player
    pgr = PlayerGameRoom.objects.filter(player=player)[0]
    room = pgr.room
    players = room.playergameroom_set
    return render(request, 'results.html',{
        'room' : room,
        'players' : players
        })

def end_of_round(request):
    if not request.user.is_authenticated():
        return HttpResponse("faca login")
    
    user = request.user
    player_query = Player.objects.filter(user__id = user.id)
    player = player_query[0]
    
    room_query = GameRoom.objects.filter(players__id = player.id)
    cur_room = room_query[0]
    
    round_query = GameRound.objects.filter(room__id = cur_room.id )
    cur_round = round_query.latest("round_number")
    now = datetime.datetime.now()
    now = brasil.localize(now)

    dt =  now - cur_round.start_time
    if dt.seconds < cur_room.game_duration :
        return HttpResponse("Jogo em andamento")
    else:
        return HttpResponse("Jogo terminado")    
    
@login_required
def pre_play(request, room_id):
    room = GameRoom.objects.get(id=room_id)
    if not request.user.player in room.players.all():
        pg = PlayerGameRoom(player=request.user.player, room=room, current_score=0)
        pg.save()
    return render(request, 'pre-play.html', {'room_id': room_id})

def can_play(request, room_id):
    room = GameRoom.objects.get(id=room_id)
    if len(room.players.all()) >= 1:
        return HttpResponse("YES")
    return HttpResponse("NO")

@login_required
def enter_room(request, room_id):
    room = GameRoom.objects.get(id=room_id)
    if room.is_protected:
        if request.method == 'POST':
            pass
        else:
            pass
        return render(request, 'enter_room.html')
    return redirect('stopgame.views.pre_play', room_id=room_id)

def rooms(request):
    rooms = GameRoom.objects.all()
    return render(request, 'rooms.html', {'rooms': rooms})

def login_view(request):
    username = request.POST.get('username', '')
    password = request.POST.get('password', '')
    user = auth.authenticate(username=username, password=password)
    if user is not None and user.is_active:
        player_query = Player.objects.filter(user__id=user.id)
        if not player_query:
            raise Http404('Nao existe player com esse nome')
        # Correct password, and the user is marked "active"
        auth.login(request, user)
        # Redirect to a success page.
        return HttpResponse("Login deu certo")
    else:
        # Show an error page
        return HttpResponse("Login deu errado")
