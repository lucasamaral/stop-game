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

@login_required
def answer_acceptance(request, round_number):
    if request.is_ajax() and request.method == 'POST':
        json_data = json.loads(request.readline())
        print json_data
        
        this_player = request.user.player
        room = GameRoom.objects.get(players=this_player)
        cur_round = GameRound.objects.get(room=room, round_number=round_number)

        for player_name in json_data:
            play_ans = json_data[player_name]
            for ans_name in play_ans:
                ans_value = play_ans[ans_name]
                player = Player.objects.get(user__username=player_name)
                print player, ans_name, ans_value
                ans_db = Answer.objects.get(roundd=cur_round, player=player, field__short_name=ans_name)
                if ans_value:
                    print "Aumentando"
                    ans_db.positive = ans_db.positive + 1
                else:
                    print "Diminuindo"
                    ans_db.negative = ans_db.negative + 1

                if ans_db.positive > ans_db.negative:
                    ans_db.valid = True;
                    ans_db.points = 10;
                else:
                    ans_db.valid = False;
                    ans_db.points = 0;
                ans_db.save()
        return HttpResponse("OK")
    else:
        if not request.is_ajax():
            return HttpResponse('Only ajax is allowed')
        elif not request.method == 'POST':
            return HttpResponse(request.method + ' is not allowed')
        else:
            return HttpResponse('unknown error')


@login_required
def receive_ans_ajax(request, round_number):
    if request.is_ajax() and request.method == 'POST':
        json_data = json.loads(request.readline())
        
        player = request.user.player
        
        room_query = GameRoom.objects.filter(players__id=player.id)
        room = room_query[0]

        round_query = GameRound.objects.filter(room__id=room.id)
        cur_round = round_query.filter(round_number=round_number)[0]

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

@login_required
def everyone_answers(request, round_number):
    player = request.user.player
        
    room_query = GameRoom.objects.filter(players__id=player.id)
    room = room_query[0]

    round_query = GameRound.objects.filter(room__id=room.id)
    cur_round = round_query.filter(round_number=round_number)[0]

    all_players = room.players.all()
    ans_dic = {}
    ok = True
    for player in all_players:
        ans_dic[player.user.username] = {}
        ans_query = Answer.objects.filter(roundd__id=cur_round.id).filter(player__id=player.id).all()
        if len(ans_query) < len(room.fields.all()):
            problematic = False
        for answer in ans_query:
            ans_dic[player.user.username][answer.field.short_name] = answer.ans
    return HttpResponse(json.dumps({'ok': ok, 'data':ans_dic}), content_type="application/json")


@login_required
def results(request):
    player = request.user.player
    pgr = PlayerGameRoom.objects.filter(player=player)[0]
    room = pgr.room
    players = room.playergameroom_set
    for p in players.all():
        playe = p.player
        answers = Answer.objects.filter(player=playe)
        su = 0
        for an in answers:
            su+=an.points
        p.current_score = su
        p.save()
    return render(request, 'results.html',{
        'room' : room,
        'players' : players
        })

@login_required
def end_of_round(request):
    player = request.user.player
    
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

def request_stop(request, room_id, round_id):
    room = GameRoom.objects.get(id=room_id)
    roundd = GameRound.objects.get(round_number=round_id, room=room)
    roundd.stopped = True
    roundd.save()
    return HttpResponse("YES")

def game_ended(request, room_id):
    room = GameRoom.objects.get(id=room_id)
    if room.round_number > room.game_duration:
        return HttpResponse("YES")
    return HttpResponse("NO")

def letter(request, room_id, round_id):
    room = GameRoom.objects.get(id=room_id)
    roundd = GameRound.objects.get(round_number=round_id, room=room)
    return HttpResponse(roundd.cur_letter)

def round_over(request, room_id, round_id):
    room = GameRoom.objects.get(id=room_id)
    roundd = GameRound.objects.get(round_number=round_id, room=room)
    all_letters = room.selected_letters.all()
    if roundd.stopped:
        if room.round_number == roundd.round_number:
            print "Updating room"
            room.round_number = room.round_number +1
            g = GameRound(cur_letter=all_letters[roundd.round_number%len(all_letters)], room=room, round_number=roundd.round_number+1)
            g.save()
            room.save()
        return HttpResponse("YES")
    return HttpResponse("NO")

def round_started(request, room_id, round_id):
    room = GameRoom.objects.get(id=room_id)
    roundd = GameRound.objects.filter(round_number=round_id, room=room).exists()
    if roundd:
        return HttpResponse("YES")
    return HttpResponse("NO")

@login_required
def enter_room(request, room_id):
    room = GameRoom.objects.get(id=room_id)
    if room.is_protected:
        if request.method == 'POST':
            password = request.POST['senha']
            if password == room.password:
                return redirect('stopgame.views.pre_play', room_id=room_id)
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
